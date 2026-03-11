import base64
import re
import os
import json
from datetime import datetime
from google.cloud import bigquery
from google.cloud import documentai_v1beta3 as documentai
from google.cloud import storage
from google.cloud import pubsub_v1
 
#Reading environment variables
gcs_output_uri_prefix = os.environ.get('GCS_OUTPUT_URI_PREFIX')
project_id = os.environ.get('GCP_PROJECT')
location = os.environ.get('PARSER_LOCATION')
processor_id = os.environ.get('PROCESSOR_ID')
geocode_request_topicname = os.environ.get('GEOCODE_REQUEST_TOPICNAME')
timeout = int(os.environ.get('TIMEOUT'))
 
# An array of Future objects: environvery call to publish() returns an instance of Future
geocode_futures = []
# Setting variables
gcs_output_uri = f"gs://{project_id}-output-invoices"
gcs_archive_bucket_name = f"{project_id}-archived-invoices"
destination_uri = f"{gcs_output_uri}/{gcs_output_uri_prefix}/"
name = f"projects/{project_id}/locations/{location}/processors/{processor_id}"
dataset_name = 'invoice_parser_results'
table_name = 'doc_ai_extracted_entities'

# Create a dict to create the schema and to avoid BigQuery load job fails due to inknown fields
bq_schema={
    "input_file_name":"STRING",  
    "address":"STRING",
    "supplier":"STRING", 
    "invoice_number":"STRING", 
    "purchase_order":"STRING",
    "date":"STRING",
    "due_date":"STRING",
    "subtotal":"STRING", 
    "tax":"STRING",
    "total":"STRING"
}
bq_load_schema=[]
for key,value in bq_schema.items():
    bq_load_schema.append(bigquery.SchemaField(key,value))
 
docai_client = documentai.DocumentProcessorServiceClient()
storage_client = storage.Client()
bq_client = bigquery.Client()
pub_client = pubsub_v1.PublisherClient()
 
def write_to_bq(dataset_name, table_name, entities_extracted_dict):
 
    dataset_ref = bq_client.dataset(dataset_name)
    table_ref = dataset_ref.table(table_name)

    test_dict=entities_extracted_dict.copy()
    for key,value in test_dict.items():
      if key not in bq_schema:
          print ('Deleting key:' + key)
          del entities_extracted_dict[key]

    row_to_insert =[]
    row_to_insert.append(entities_extracted_dict)
 
    json_data = json.dumps(row_to_insert, sort_keys=False)
    #Convert to a JSON Object
    json_object = json.loads(json_data)
   
    job_config = bigquery.LoadJobConfig(schema=bq_load_schema)
    job_config.source_format = bigquery.SourceFormat.NEWLINE_DELIMITED_JSON
 
    job = bq_client.load_table_from_json(json_object, table_ref, job_config=job_config)
    error = job.result()  # Waits for table load to complete.
    print(error)

def get_text(doc_element: dict, document: dict):
    # Document AI identifies form fields by their offsets in document text. This function converts offsets to text snippets.
    response = ''
    # If a text segment spans several lines, it will be stored in different text segments.
    for segment in doc_element.text_anchor.text_segments:
        start_index = (
            int(segment.start_index)
            if segment in doc_element.text_anchor.text_segments
            else 0
        )
        end_index = int(segment.end_index)
        response += document.text[start_index:end_index]
    return response
 
def process_invoice(event, context):
    gcs_input_uri = 'gs://' + event['bucket'] + '/' + event['name']
    print('Printing the contentType: ' + event['contentType'])

    if(event['contentType'] == 'image/gif' or event['contentType'] == 'application/pdf' or event['contentType'] == 'image/tiff' ):
        input_config = documentai.types.document_processor_service.BatchProcessRequest.BatchInputConfig(gcs_source=gcs_input_uri, mime_type=event['contentType'])
        # Where to write results
        output_config = documentai.types.document_processor_service.BatchProcessRequest.BatchOutputConfig(gcs_destination=destination_uri)
 
        request = documentai.types.document_processor_service.BatchProcessRequest(
            name=name,
            input_configs=[input_config],
            output_config=output_config,
        )
 
        operation = docai_client.batch_process_documents(request)
 
        # Wait for the operation to finish
        operation.result(timeout=timeout)
 
        match = re.match(r"gs://([^/]+)/(.+)", destination_uri)
        output_bucket = match.group(1)
        prefix = match.group(2)
      
        #Get a pointer to the GCS bucket where the output will be placed
        bucket = storage_client.get_bucket(output_bucket)
      
        blob_list = list(bucket.list_blobs(prefix=prefix))
        print('Output files:')
 
        for i, blob in enumerate(blob_list):
            # Download the contents of this blob as a bytes object.
            if '.json' not in blob.name:
                print('blob name ' + blob.name)
                print(f"skipping non-supported file type {blob.name}")
            else:
                #Setting the output file name based on the input file name
                print('Fetching from ' + blob.name)
                start = blob.name.rfind("/") + 1
                end = blob.name.rfind(".") + 1           
                input_filename = blob.name[start:end:] + 'gif'
                print('input_filename ' + input_filename)
      
                # Getting ready to read the output of the parsed document - setting up "document"
                blob_as_bytes = blob.download_as_bytes()
                document = documentai.types.Document.from_json(blob_as_bytes)
      
                #Reading all entities into a dictionary to write into a BQ table
                entities_extracted_dict = {}
                entities_extracted_dict['input_file_name'] = input_filename
                for page in document.pages:
                    for form_field in page.form_fields:  
                        field_name = get_text(form_field.field_name,document)
                        field_value = get_text(form_field.field_value,document)
                        if field_name.strip().lower() == 'date:':
                            entities_extracted_dict['date'] = field_value
                        if field_name.strip().lower() == 'invoice number:':
                            entities_extracted_dict['invoice_number'] = field_value
                        if field_name.strip().lower() == 'purchase order:':
                            entities_extracted_dict['purchase_order'] = field_value
                        if field_name.strip().lower() == 'payment due by:':
                            entities_extracted_dict['due_date'] = field_value
                        if field_name.strip().lower() == 'subtotal':
                            entities_extracted_dict['subtotal'] = field_value
                        if field_name.strip().lower() == 'tax':
                            entities_extracted_dict['tax'] = field_value
                        if field_name.strip().lower() == 'total':
                            entities_extracted_dict['total'] = field_value

                        # # Creating and publishing a message via Pub Sub
                        if field_name.strip().lower() == 'address:':
                            message = {
                                "entity_type": field_name,
                                "entity_text" : field_value,
                                "input_file_name": input_filename,
                            }
                            message_data = json.dumps(message).encode("utf-8")
                            
                            entities_extracted_dict['address'] = field_value
                            geocode_topic_path = pub_client.topic_path(project_id,geocode_request_topicname)
                            geocode_future = pub_client.publish(geocode_topic_path, data = message_data)
                            geocode_futures.append(geocode_future)
                      
                print(entities_extracted_dict)
                print('Writing to BQ')
                #Write the entities to BQ
                write_to_bq(dataset_name, table_name, entities_extracted_dict)
                
        #print(blobs)
        #Deleting the intermediate files created by the Doc AI Parser
        blobs = bucket.list_blobs(prefix=gcs_output_uri_prefix)
        for blob in blobs:
            blob.delete()
        #Copy input file to archive bucket
        source_bucket = storage_client.bucket(event['bucket'])
        source_blob = source_bucket.blob(event['name'])
        destination_bucket = storage_client.bucket(gcs_archive_bucket_name)
        blob_copy = source_bucket.copy_blob(source_blob, destination_bucket, event['name'])
        #delete from the input folder
        source_blob.delete()
    else:
        print('Cannot parse the file type')


if __name__ == '__main__':
    print('Calling from main')
    testEvent={"bucket":project_id+"-input-invoices", "contentType": "application/pdf", "name":"invoice2.pdf"}
    testContext='test'
    process_invoice(testEvent,testContext)
