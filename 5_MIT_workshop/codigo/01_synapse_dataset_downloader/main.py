import synapseclient
import synapseutils
import os


#files = synapseutils.syncFromSynapse(syn, 'syn38943763') 
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("python-dotenv not found. Ensure environment variables are set manually.")

# Retrieve auth token from environment variables
auth_token = os.getenv("SYNAPSE_AUTH_TOKEN")

if not auth_token:
    print("Error: SYNAPSE_AUTH_TOKEN environment variable not set.")
    print("Please create a .env file with SYNAPSE_AUTH_TOKEN=your_token or export it.")
else:
    # Initialize Synapse
    syn = synapseclient.Synapse()

    try:
        # Log in using the auth token
        syn.login(authToken=auth_token)
        print("Logged in successfully!")
    except Exception as e:
        print(f"Login failed: {e}")
