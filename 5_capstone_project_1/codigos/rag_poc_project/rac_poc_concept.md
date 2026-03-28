# CONTEXTO DEL PROYECTO: PoC RAG Agéntico para Sector Minería (Capstone 1)
## Descripción General
El objetivo de este proyecto es construir un "Hola Mundo" (Prueba de Concepto - PoC) de un sistema RAG (Retrieval-Augmented Generation) Agéntico. Este sistema procesará documentos técnicos de ingeniería/minería (EIA, ITS, Manuales, Reglamentos y Normativas) y permitirá hacer consultas sobre ellos.
El desarrollo se realizará en un Jupyter Notebook (`.ipynb`) utilizando Python y Google Colab.

## Tecnologías y Frameworks Requeridos
- **Lenguaje:** Python 3.10+
- **Entorno:** Jupyter Notebook
- **Framework de Orquestación:** Ecosistema Google (Google Generative AI SDK / emulando el comportamiento del Google Agent Development Kit mediante Function Calling/Tools).
- **Modelo de Lenguaje (LLM):** `gemini-1.5-pro` o `gemini-1.5-flash`. De no estar disponibles, usa, en este orden, gemini-2.5-flash, gemini-3.1-flash, gemini-3.1-flash-lite, gemini-2.5-flash-lite.
- **Modelo de Embeddings:** `text-embedding-004` (Google).
- **Base de Datos Vectorial:** `ChromaDB` (In-memory, para iteración rápida).
- **Procesamiento de Documentos:** `PyPDF2` o `pdfplumber` y `langchain-text-splitters`.

## Estructura del Directorio (Workspace)
```text
/rag_poc_project
│── data/
│   └── documento_muestra_1.pdf  # (Ej: Informe de permeabilidad de relaves)
│   └── documento_muestra_2.pdf  # (Ej: Normativa ambiental)
│── .env                         # Contiene GOOGLE_API_KEY
│── requirements.txt             # Dependencias
└── poc_rag_agentico.ipynb       # Notebook principal
```

## INSTRUCCIONES DE DESARROLLO (STEP-BY-STEP)
*Nota para el Asistente del IDE: Genera el código para el Jupyter Notebook siguiendo exactamente estos 6 pasos. Cada paso debe ser una o más celdas de código documentadas.*

### PASO 1: Instalación de Dependencias y Configuración
1. Crear el archivo `requirements.txt` con: 
   `google-generativeai`, `chromadb`, `pypdf`, `langchain-text-splitters`, `python-dotenv`, `jupyter`.
2. En la primera celda del notebook, cargar variables de entorno (`GOOGLE_API_KEY`) usando `dotenv`.
3. Configurar el SDK de Google: `genai.configure(api_key=os.environ["GOOGLE_API_KEY"])`.

### PASO 2: Ingesta de Datos (Document Ingestion)
1. Crear una función `load_pdfs(directory_path)` que lea iterativamente los PDFs dentro de la carpeta `/data`.
2. Extraer el texto crudo y mantener metadatos básicos (ej. `nombre_archivo`, `numero_pagina`).

### PASO 3: Segmentación de Texto (Chunking)
1. Utilizar `RecursiveCharacterTextSplitter` de LangChain.
2. Configurar un `chunk_size` de 1000 caracteres y un `chunk_overlap` de 200 caracteres (ideal para mantener el contexto en documentos técnicos densos).
3. Convertir el texto extraído en una lista de diccionarios que contengan `text` y `metadata`.

### PASO 4: Generación de Embeddings y Vector Store
1. Inicializar un cliente en memoria de ChromaDB: `chromadb.Client()`.
2. Crear una colección llamada `mineria_tecnica`.
3. Crear una función que envíe los chunks a la API de embeddings de Google (`models/text-embedding-004`).
4. Almacenar los chunks, metadatos y embeddings (vectores) en la colección de ChromaDB.

### PASO 5: Creación de la Herramienta de Recuperación (Retriever Tool)
*Aquí aplicamos el enfoque "Agéntico" de Google.*
1. Crear una función de Python llamada `buscar_informacion_tecnica(query: str) -> str`.
2. Esta función debe:
   - Recibir la consulta del usuario.
   - Convertir la consulta en un embedding.
   - Hacer un query a ChromaDB buscando los Top-K (ej. k=3) chunks más similares.
   - Formatear y retornar los resultados como un string consolidado citando el documento de origen.
3. Declarar esta función como una *Tool* compatible con Gemini.

### PASO 6: Instanciación del Agente (Google Gemini) y Prueba
1. Instanciar el modelo: `model = genai.GenerativeModel(model_name='gemini-1.5-pro', tools=[buscar_informacion_tecnica])`.
2. Definir un `System Instruction` (Prompt del sistema) estricto: 
   *"Eres un Agente Especialista en Ingeniería Minera. Tu tarea es responder consultas técnicas utilizando ÚNICAMENTE la herramienta de recuperación de información provista. Si la información no está en los documentos, debes indicar que no lo sabes. Cita siempre el documento de origen."*
3. Iniciar un chat: `chat = model.start_chat(enable_automatic_function_calling=True)`.
4. Ejecutar 2 consultas de prueba relacionadas a minería (ej. *"¿Cuáles son los parámetros de permeabilidad para relaves según los documentos?"*).
5. Imprimir la respuesta final del agente.

---

## REGLAS DE CODIFICACIÓN PARA EL ASISTENTE (GUARDRAILS)
- Todo el código de Python debe estar listo para ejecutarse secuencialmente en un entorno de celdas de Jupyter.
- Usa `typing` e incluye docstrings descriptivos en cada función.
- Implementa manejo de errores básico (ej. `try/except` al leer PDFs o consultar la API).
- Emplea un tono profesional y comentarios en español.
- NO uses emojis en el codigo ni documentacion.
- NO uses estructuras ni cuadros dentro de los comentarios, ej: "----------" para hacer cuadros o lineas. Eso no parece humano.
- NO uses herramientas genéricas de LangChain para el agente; utiliza la funcionalidad nativa de "Function Calling" (Tools) de la API de Google Gemini para demostrar el comportamiento agéntico puro recomendado por Google.