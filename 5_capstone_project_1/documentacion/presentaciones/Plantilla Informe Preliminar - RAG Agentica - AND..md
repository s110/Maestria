                                                 
**UNIVERSIDAD DE INGENIERÍA Y TECNOLOGÍA**  
ESCUELA DE POSGRADO

**Propuesta de Arquitectura RAG Agéntica para la Recuperación de Información Técnica en Corpus No Estructurados a Gran Escala** 

**INFORME PRELIMINAR**  
Para optar el grado de Maestro en Ciencia de Datos e Inteligencia Artificial

**AUTOR(ES)**  
Lopez Medina, Sebatián  
Nieto Espinoza, Brajan  
Tapia Chasquibol, Mateo 

**ASESOR(ES)**  
Machaca Arceda, Vicente

**Lima – Perú**  
**2026**

**RESUMEN**

El presente informe describe el diseño y planificación para el desarrollo de un sistema de Generación Aumentada por Recuperación (RAG) de naturaleza agéntica. El objetivo de la solución es optimizar el acceso y la precisión en la recuperación de información técnica contenida en documentos de consultoría, estudios especialziados y normativa, permitiendo a los profesionales de la organización localizar conocimiento relevante de manera rápida, precisa y segura. 

La propuesta busca abordar las limitaciones de los métodos tradicionales de búsqueda documental, porque estos resultan ser poco eficientes cuando se trabaja con grandes volúmenes de información técnica no estructurada. Para ello, el sistema implementará una arquitectura RAG que combina LLMs (Large Language Models) con mecanismos de recuperación semántica sobre un repositorio documental vectorizado de la compañía, permitiendo generar respuestas fundamentadas desde los propios documentos internos.

El alcance técnico del proyecto se estructura en dos módulos principales. El Módulo I contempla el diseño e implementación de la arquitectura RAG base, incluyendo el pipeline de procesamiento documental, generación de embeddings, almacenamiento vectorial y mecanismo de recuperación semántica. El Módulo II considera el desarrollo de una API para el acceso programático al sistema, la implementación de guardrails de seguridad para el control de consultas y respuestas generadas por el modelo, y una interfaz de usuario tipo chatbot, la cual facilite la interacción entre los usuarios y el sistema. 

Finalmente, se analiza el uso de frameworks especializados en sistemas agénticos como Google ADK, así como alternativas de infraestructura cloud para el despliegue del almacenamiento vectorial y bases de datos. La arquitectura propuesta busca garantizar escalabilidad, seguridad y trazabilidad en el acceso al conocimiento organizacional.  

**PALABRAS CLAVES:**   
RAG Agéntico; Google ADK; Guardrails; API; LLM; Bases de Datos Vectoriales; AWS; Azure.

**ABSTRACT**

**Proposal for an Agentic RAG Architecture for the Retrieval of Technical Information in Large-Scale Unstructured Corpora**

This report describes the design and planning for the development of an agentic Retrieval-Augmented Generation (RAG) system. The objective of the solution is to optimize access and precision in the retrieval of technical information contained in consulting documents, specialized studies, and regulations, enabling the organization's professionals to locate relevant knowledge quickly, accurately, and securely.

The proposal seeks to address the limitations of traditional document search methods, as these prove to be inefficient when dealing with large volumes of unstructured technical information. To achieve this, the system will implement a RAG architecture that combines Large Language Models (LLMs) with semantic retrieval mechanisms over a vectorized corporate document repository, allowing the generation of grounded responses directly from internal documents.

The technical scope of the project is structured into two main modules. Module I encompasses the design and implementation of the baseline RAG architecture, including the document processing pipeline, embedding generation, vector storage, and semantic retrieval mechanism. Module II covers the development of an API for programmatic access to the system, the implementation of security guardrails to control queries and model-generated responses, and a chatbot-style user interface to facilitate interaction between users and the system.

Finally, it analyzes the use of specialized frameworks for agentic systems, such as Google ADK, as well as cloud infrastructure alternatives for deploying the vector storage and databases. The proposed architecture aims to guarantee scalability, security, and traceability in accessing organizational knowledge.

**KEYWORDS:**

RAG Agéntico; Google ADK; Guardrails; API; LLM; Bases de Datos Vectoriales; AWS; Azure.

**TABLA DE CONTENIDO**

**[CAPÍTULO I	5](#capítulo-i)**

[**VISIÓN DEL PRODUCTO	5**](#visión-del-producto)

[1.1. Problema y Oportunidad	5](#1.1.-problema-y-oportunidad)

[1.2. Usuarios y Casos de Uso	6](#1.2.-usuarios-y-casos-de-uso)

[1.3. Propuesta de Valor y KPIs de éxito	7](#1.3.-propuesta-de-valor-y-kpis-de-éxito)

[**CAPÍTULO II	12**](#capítulo-ii)

[**DATOS Y PRIVACIDAD	12**](#datos-y-privacidad)

[2.1. Análisis de datos	12](#2.1.-análisis-de-datos)

[2.2. Cumplimiento de Privacidad de Datos	14](#2.2.-cumplimiento-de-privacidad-de-datos)

[**CAPÍTULO III	16**](#capítulo-iii)

[**DISEÑO DE SOLUCIÓN DEL PRODUCTO DE DATOS	16**](#diseño-de-solución-del-producto-de-datos)

[3.1. Arquitectura del Producto de Datos	16](#3.1.-arquitectura-del-producto-de-datos)

[3.2. Requisitos funcionales y no funcionales mínimos	18](#3.2.-requisitos-funcionales-y-no-funcionales-mínimos)

[**CAPÍTULO IV	12**](#capítulo-iv)

[**PROTOTIPO FUNCIONAL	12**](#prototipo-funcional)

[4.1. Alcance del Prototipo Funcional	12](#4.1.-alcance-del-prototipo-funcional)

[4.2. Construcción del prototipo	13](#4.2.-construcción-del-prototipo)

[4.3. Validación y Evaluación del Prototipo	13](#4.3.-validación-y-evaluación-del-prototipo)

[**CAPÍTULO V	15**](#capítulo-v)

[**PLAN DE SIGUIENTE FASE	15**](#plan-de-siguiente-fase)

[5.1. Roadmap y Siguientes Pasos	15](#5.1.-roadmap-y-siguientes-pasos)

[5.2. Cronograma	15](#5.2.-cronograma)

[**CONCLUSIONES	17**](#conclusiones)

[**REFERENCIAS BIBLIOGRÁFICAS	18**](#referencias-bibliográficas)

# **CAPÍTULO I** {#capítulo-i}

# **VISIÓN DEL PRODUCTO**  {#visión-del-producto}

## **1.1. Problema y Oportunidad** {#1.1.-problema-y-oportunidad}

Los procesos de consultoría de las firmas de diseño se caracterizan por requerir un rigor analítico exhaustivo, fundamentado en la revisión constante de volúmenes masivos de documentación técnica, registros históricos e informes previos. Firmas líderes con una trayectoria que abarca miles proyectos multidisciplinarios ejecutados a nivel internacional y un equipo de cientos de ingenieros especializados , generan y acumulan diariamente un corpus documental de extrema densidad y complejidad. A la fecha, la organización cuenta con un repositorio que supera los 73,000 documentos técnicos acumulados a lo largo de su trayectoria operativa, cifra que continúa en crecimiento constante con cada nuevo proyecto. Este acervo incluye Estudios de Impacto Ambiental (EIA), Informes Técnicos Sustentatorios (ITS), manuales de diseño geotécnico, modelamientos hidrológicos,  auditorías de cumplimiento normativo sectorial, entre otros.

La elaboración y sustentación de estos documentos críticos es un proceso inherentemente prolongado. Históricamente, la compilación de este tipo de estudios puede requerir plazos que oscilan entre los dieciocho meses y los siete años, dependiendo de la magnitud de la operación y las exigencias regulatorias. En el entorno operativo actual, la recuperación de la información necesaria para estructurar estos expedientes se realiza predominantemente de manera manual o mediante sistemas de búsqueda léxica rudimentarios basados en coincidencias exactas de palabras clave. Esta metodología tradicional genera tiempos de búsqueda excesivamente prolongados, ineficiencias operativas significativas y fomenta la creación de silos de conocimiento donde valiosa inteligencia técnica queda sepultada en discos duros departamentales o repositorios no indexados.

El problema central radica en que los sistemas de gestión documental estándar no comprenden la semántica, el contexto ni las interrelaciones complejas de la ingeniería aplicada. Por lo tanto, existe una oportunidad estratégica sin precedentes para implementar un sistema de Generación Aumentada por Recuperación (RAG) que trascienda la simple indexación de texto. La implementación de una arquitectura RAG de naturaleza agéntica permite automatizar la extracción de respuestas precisas y contextualmente ricas basadas en el repositorio documental corporativo de la firma, reduciendo de manera drástica los tiempos de operación y mejorando exponencialmente la calidad, coherencia y profundidad técnica de las consultas.

## **1.2. Usuarios y Casos de Uso** {#1.2.-usuarios-y-casos-de-uso}

**Usuarios:** El sistema está diseñado para empoderar directamente a consultores, ingenieros de proyectos, geotécnicos, hidrológicos, mecánicos, eléctricos, estructurales, hidráulicos, geólogos, geomecánicos, diseñadores civiles, especialistas ambientales y todo personal técnico operativo de la consultora.

Estos profesionales poseen un alto grado de especialización técnica y requieren respuestas que no solo sean informativas, sino que estén rigurosamente fundamentadas en datos empíricos, normativas vigentes e historiales de proyectos comparables. Su tolerancia a la ambigüedad o a las inexactitudes técnicas (alucinaciones algorítmicas) es prácticamente nula, dado el impacto que sus decisiones tienen sobre la viabilidad de infraestructuras críticas y el cumplimiento técnico, normativo y medioambiental.

**Caso de Uso Principal:** Un consultor ingresa una consulta técnica sobre normativas o proyectos pasados, y el sistema agéntico recupera los fragmentos de documentos relevantes para generar una respuesta técnica precisa, citando las fuentes internas.

Por ejemplo, el sistema permitirá que el usuario pueda solicitar un análisis comparativo sobre las normativas de permeabilidad para instalaciones de almacenamiento de relaves filtrados aplicadas en proyectos de gran minería durante los últimos cinco años, o buscar precedentes específicos sobre planes de gestión de aguas en topografías andinas accidentadas. En lugar de devolver una lista de cientos de documentos PDF sin procesar, el sistema agéntico interpreta la intencionalidad de la consulta y la descompone en subtareas. Posteriormente, se recuperan los fragmentos de documentos técnicos e históricos más relevantes, evalúan iterativamente la calidad de la información extraída y, finalmente, se genera una respuesta técnica redactada con precisión académica. Crucialmente, esta respuesta incluirá hipervínculos directos y citas explícitas a las fuentes internas de la firma de diseño de donde se extrajo cada parámetro, garantizando la trazabilidad absoluta de la información.

## 

## **1.3. Propuesta de Valor y KPIs de éxito** {#1.3.-propuesta-de-valor-y-kpis-de-éxito}

***Propuesta de Valor:*** 

Proveer a los equipos multidisciplinarios un ecosistema tecnológico de acceso rápido, semánticamente preciso y criptográficamente seguro al conocimiento corporativo acumulado, mediante un sistema RAG agéntico que transforma repositorios de datos pasivos en inteligencia operativa accionable en tiempo real. 

***Objetivos del prototipo:***

* Objetivo 1: Desarrollar un prototipo funcional RAG capaz de procesar un conjunto representativo de documentos técnicos de la organización y responder consultas en lenguaje natural durante la fase de prueba del proyecto.   
* Objetivo 2: Demostrar que el sistema reduce el tiempo de recuperación de información técnica en comparación con métodos de búsqueda manual o basados en coincidencias de palabras clave.  
* Objetivo 3: Implementar mecanismos de seguridad y control que permitan prevenir el uso de información no autorizada o la ejecución de consultas potencialmente maliciosas. 


***KPIs de Éxito:***

* Reducción del tiempo promedio de búsqueda de información documental en al menos un 50% respecto al método manual, medido en pruebas comparativas con usuarios piloto.  
* Precisión en la recuperación de documentos: MRR ≥ 0.75 en el conjunto de pruebas de validación.  
* Tasa de bloqueo efectivo de prompts inseguros mediante guardrails ≥ 95% en escenarios de prueba con inyecciones adversariales. 

# **CAPÍTULO II** {#capítulo-ii}

# **DATOS Y PRIVACIDAD** {#datos-y-privacidad}

## **2.1. Análisis de datos** {#2.1.-análisis-de-datos}

El rendimiento, la fiabilidad y la utilidad de cualquier sistema basado en Large Language Models (LLMs) dependen de manera absoluta en la calidad, la estructuración y la limpieza del corpus de datos subyacente. Puesto que, estos datos constituyen la principal fuente de conocimiento utilizada para alimentar el sistema de recuperación semántica. En adición, en una consultora de ingeniería como Anddes, el desafío de la gestión de datos es superlativo debido a la extrema heterogeneidad y complejidad técnica de la información.

***Inventario de fuente de datos:***

El sistema propuesto se alimentará de repositorios documentales utilizados en el desarrollo de proyectos de consultorái técnica. Estos repositorios contienen conocimiento acumulado a lo largo de múltiples proyectos, años de experiencia y abarcan una  una multitud de disciplinas de las ciencias de la tierra y la ingeniería civil, minera y ambiental.

El ecosistema de información está compuesto por repositorios históricos y activos que abarcan una gran diversidad de documentos técnicos especializados. Entre las principales fuentes de ingestión consideradas para el sistema RAG agéntico se incluyen:

* Informes técnicos de proyectos.  
* Normativas gubernamentales sectoriales.  
* Estudios de impacto ambiental (EIA).  
* Informes técnicos sustentatoriso (ITS).  
* Memorias descriptivas de proyectos.  
* Manuales de construcción.  
* Hojas de cálculo con parámetros técnicos.  
* Planos y documentos de ingeniería.  
* Historial de proyectos mineros y energéticos.

Estos documentos contienen no sólo texto narrativo, sino también especificaciones técnicas críticas, tablas de propiedades de materiales, coordenadas geoespaciales y evaluaciones de riesgos y datos técnicos estructurados, lo que introduce desafíos adicionales para su procesamiento automático.

***Procesamiento y preparación de datos:***

Para habilitar su uso en el sistema RAG, los documentos serán procesados mediante un pipeline de ingestión que incluye las siguientes etapas:

1. Extracción de contenido textual con técnicas de lenguaje natural (NLP) desde los documentos fuente.  
2. Limpieza y normalización del texto, eliminando contenido irrelevante.  
3. Segmentación del contenido en fragmentos (chunking) para facilitar su recuperación semántica.  
4. Generación de representaciones vectoriales (embeddings).  
5. Almacenamiento en una base de datos vectorial, junto con metadatos estructurados que permitan mejorar el proceso de búsqueda.

Este pipeline permite transformar documentos complejos en un formato adecuado para su utilización dentro de sistemas RAG.

***Diccionario y Calidad:*** 

Para facilitar la recuperación eficiente de información, el sistema incorporará un esquema estructurado de metadatos asociado a cada fragmento documental. Estos metadatos permitirán aplicar técnicas de filtrado previo a la búsqueda vectorial (pre-filtering), lo cual reduce el espacio de búsqueda y mejora la latencia del sistema.

El diccionario de metadatos considerado para el prototipo incluye los siguiente atributos:

| Metadato Estructural | Tipo de Dato | Propósito en el Pipeline RAG |
| :---- | :---- | :---- |
| id\_documento | UUID (Cadena) | Llave primaria para la trazabilidad y actualización en la base de datos vectorial contiene (Proyecto, cliente y  tipo de documento). |
| proyecto\_asociado | Cadena | Permite a los agentes restringir búsquedas a un proyecto minero específico mediante filtrado de metadatos. |
| disciplina\_tecnica | Categórico | Facilita el enrutamiento semántico hacia el sub-agente especializado correcto. |
| fragmento\_texto | Cadena Larga | Contenido semántico puro que será vectorizado y suministrado como contexto al LLM. |
| vector\_incrustacion | Arreglo de Flotantes | Representación matemática densa utilizada para calcular la similitud semántica. |

## **2.2. Cumplimiento de Privacidad de Datos** {#2.2.-cumplimiento-de-privacidad-de-datos}

El manejo de planos de infraestructura crítica, presupuestos operativos y datos de impacto ambiental impone responsabilidades legales y éticas intransigibles. Los contratos de consultoría están blindados por Acuerdos de Confidencialidad (NDA) que prohíben la exposición de propiedad intelectual a entidades no autorizadas.

***Privacidad por Diseño***

La arquitectura del producto de datos adopta un paradigma estricto de Privacidad por Diseño (Privacy by Design) y Confianza Cero (Zero Trust). Se garantiza que los datos vectorizados, así como los documentos originales procesados, residirán exclusivamente en un entorno virtual cerrado y privativo dentro de la infraestructura en la nube seleccionada (AWS o Azure). Bajo ninguna circunstancia se permitirá la exposición del corpus corporativo a Modelos de Lenguaje públicos o APIs de terceros que utilicen la telemetría de inferencia o el contenido de los prompts para el entrenamiento continuo, ajuste fino (fine-tuning) o mejora de sus propios modelos base fundacionales.

Todo el tráfico de datos estará confinado dentro de los límites de red corporativos mediante el uso de enlaces privados y políticas estrictas de gestión de identidades y accesos (IAM). Se incluirán mapas de datos exhaustivos para identificar y enmascarar dinámicamente cualquier conjunto de datos que contenga Información de Identificación Personal (PII) antes de que la consulta sea procesada por el motor de razonamiento algorítmico.

***Seguridad y Guardrails***

La naturaleza instructiva de los Modelos de Lenguaje modernos los hace susceptibles a vectores de manipulación únicos que las defensas tradicionales de ciberseguridad no pueden mitigar por sí solas. Por ello, se establece como mandato ineludible la implementación obligatoria de Guardrails (barreras de seguridad programáticas y heurísticas). Estos controles perimetrales actuarán bidireccionalmente: en la capa de entrada, evaluando sintáctica y semánticamente el prompt del usuario para evitar tácticas de inyección de instrucciones (prompt injection) y jailbreaking diseñadas para forzar al modelo a eludir sus directrices operativas; y en la capa de salida, auditando la respuesta generada para prevenir fugas de información sensible, filtrar alucinaciones detectables y garantizar la adherencia estricta a un tono profesional y pertinente a la materia de consultoría técnica.

# 

# **CAPÍTULO III** {#capítulo-iii}

# **DISEÑO DE SOLUCIÓN DEL PRODUCTO DE DATOS** {#diseño-de-solución-del-producto-de-datos}

## **3.1. Arquitectura del Producto de Datos** {#3.1.-arquitectura-del-producto-de-datos}

La arquitectura propuesta se basa en utilizar un LLM como un motor central de razonamiento, el cual opera como un componente orquestado capaz de interpretar consultas técnicas, planificar estrategias de recuperación de información y coordinar el uso de herramientas computacionales dentro del sistema.

Este enfoque se implementa mediante una arquitectura RAG agéntica, en la cual el LLM no actúa de forma aislada, sino que interactúa con repositorios documentales, bases de datos vectoriales y agentes especializados que colaboran entre sí para resolver consultas técnicas de gran complejidad.

***Framework Principal***

Tras una evaluación comparativa frente a alternativas ampliamente utilizadas en la industria del código abierto como LangChain y Microsoft AutoGen, se propone establecer el Google Agent Development Kit (ADK) como el framework principal para la orquestación del RAG agéntico. 

La elección de Google ADK se fundamenta en su enfoque "Multi-Agente por Diseño", el cual facilita la construcción de arquitecturas compuestas por múltiples agentes especializados que colaboran entre sí para resolver tareas complejas. Este enfoque resulta especialmente adecuado para el contexto de la consultoría técnica, donde las consultas pueden involucrar múltiples disciplinas y fuentes de información. 

La arquitectura diseñada contempla una jerarquía de agentes compuesta por los siguientes componentes principales:

* Agentes Especialistas: Agentes que se especializan en dominios técnicos específicos. Su función principal es interactuar con las bases vectoriales y ejecutar procesos de recuperación semántica para identificar fragmentos documentales relevantes. Por ello, pueden refinar búsquedas de manera iterativa utilizando resultados intermedios hasta localizar información adecuada para responder la consulta.   
* Agente de Síntesis: Es un agente que consolida los resultados obtenidos de los agentes especialistas y genera una respuesta coherente utilizando el LLM. Por ende, es el responsable de estructurar la respuesta final e incluir referencias a los documentos utilizados como fuente. 


***Infraestructura de Datos***

El despliegue también exige una infraestructura subyacente para alojar el Vector Store, las bases de datos relacionales auxiliares y la carga de inferencia del LLM. Se llevará a cabo un análisis exhaustivo contrastando las capacidades empresariales de proveedores como  Microsoft Azure, Amazon Web Services (AWS) o GCP.

Si bien se evalúa Azure por su profunda integración con los entornos corporativos convencionales y su oferta de Azure OpenAI, se identifica preliminarmente que su ecosistema presenta fricciones operativas en términos de gestión de cuotas de rendimiento provisionado, estructuras de costos opacas a escala masiva y una madurez incipiente en ciertos servicios de bases de datos vectoriales nativas comparadas con soluciones independientes. Por el contrario, AWS se perfila como la mejor opción para garantizar la madurez, elasticidad y estabilidad del despliegue en producción. AWS ofrece una plataforma resiliente para arquitecturas de microservicios y despliegues serverless. 

La arquitectura propuesta mantiene su neutralidad tecnológica (model-agnostic), permitiendo conmutar entre modelos fundacionales líderes de la industria (como los provistos por Google,  Anthropic, Meta o Amazon). 

![][image1]

## **3.2. Requisitos funcionales y no funcionales mínimos** {#3.2.-requisitos-funcionales-y-no-funcionales-mínimos}

***Requisitos Funcionales***

Los requisitos funcionales delinean las capacidades operativas intrínsecas que el producto de datos debe proporcionar a los usuarios e interfaces conectadas

* Recuperación de información semántica (Arquitectura RAG)  
  El sistema debe ser capaz de recuperar información relevante desde repositorios documentales utilizando representaciones vectoriales y consultas en lenguaje natural.  
* Generación de respuestas fundamentadas  
  Las respuestas generadas por el sistema deben basarse en información recuperada desde los documentos disponibles, incluyendo referencias a las fuentes utilizadas.  
* Exposición de las capacidades mediante una API  
  Las funcionalidades del sistema deberán ser accesibles mediante una API que permita su integración con interfaces conversacionales u otros sistemas corporativos.  
* Implementación de mecanismos de seguridad (guardrails)

  El sistema deberá incluir mecanismos de control que permitan prevenir el uso indebido del LLM y mitigar riesgos asociados a consultas maliciosas.


**Requisitos No Funcionales**

Los requisitos no funcionales definen los atributos de calidad, rendimiento y seguridad que determinan la viabilidad del sistema en un entorno de producción exigente

* Alta disponibilidad de la API.  
  La API del sistema debe mantenerse disponible para los usuarios durante la operación normal del servicio.  
* Latencia de respuesta aceptable para el usuario final.  
  El tiempo requerido para procesar consultas y generar respuestas debe mantenerse dentro de niveles adecuados para la interacción del usuario.  
* Aislamiento de la infraestructura cloud.

  La infraestructura utilizada para almacenar documentos y ejecutar el modelo debe mantenerse aislada dentro del entorno corporativo para garantizar la seguridad de la información.

* Seguridad y control de acceso

  El sistema debe implementar mecanismos de autenticación, autorización y registro de consultas para garantizar el uso seguro de la plataforma.

# **CAPÍTULO IV** {#capítulo-iv}

# **PROTOTIPO FUNCIONAL**  {#prototipo-funcional}

## **4.1. Alcance del Prototipo Funcional** {#4.1.-alcance-del-prototipo-funcional}

El proceso de ingeniería de software se ejecutará a través de una metodología incremental, segmentada en dos módulos lógicos para asegurar una entrega de valor medible y la mitigación temprana de riesgos arquitectónicos. 

***El Módulo I (Capstone 1\)***

Se enfocará exclusivamente en la validación algorítmica. Incluirá la codificación de la Arquitectura RAG clásica y la instanciación de los agentes base en un entorno de Notebook de Python, ejecutando diferentes estrategias de partición de texto (chunking) y modelos de incrustación vectorial (embeddings). En esta fase analítica se evaluará la viabilidad de integrar grafos de conocimiento (GraphRAG) para modelar relaciones jerárquicas complejas entre documentos técnicos.

***El Módulo II (Capstone 2\)***

Elevará el desarrollo a un nivel de software operativo. Incluirá el desarrollo completo de una API REST para conectar y exponer la lógica del sistema RAG agéntico, y el manejo maduro de seguridad mediante Guardrails activos en la etapa de inferencia. También, se contempla el desarrollo de una App ligera (chatbot) como interfaz gráfica para facilitar el testeo por parte de los ingenieros.

El prototipo no incluye integraciones con sistemas transaccionales heredados (ERP/CRM) ni el procesamiento óptico avanzado de planos CAD o documentos ilegibles que requieran transcripción manual.

Para garantizar la agilidad del ciclo de desarrollo, la ingesta inicial se restringirá a un subconjunto altamente curado y representativo del repositorio corporativo. Este conjunto inicial constará de cientos de Informes Técnicos Sustentatorios, Estudios de Impacto Ambiental recientes y manuales de procedimientos geotécnicos, garantizando que el corpus contenga la densidad técnica necesaria sin sobrecargar la infraestructura inicial. La arquitectura del sistema está diseñada para soportar la incorporación progresiva del repositorio completo (aprox 73000 documentos) mediante fases sucesivas de ingestión, de modo que la organización pueda ir ampliando la cobertura documental de forma controlada conforme se valide el rendimiento del sistema en cada incremento.

La API desarrollada en el Módulo II debe responder con códigos de estado HTTP 200 consistentes, devolviendo objetos JSON bien formados que incluyan tanto la respuesta redactada como los identificadores bibliográficos de las fuentes consultadas. Cualquier intento de violar las directrices del sistema debe resultar en una interceptación demostrable por parte de los guardrails, devolviendo un código de error controlado.

## **4.2. Construcción del prototipo** {#4.2.-construcción-del-prototipo}

Durante esta etapa, se desarrollará scripts modulares en Python para la ingestión, limpieza y vectorización del corpus documental. Se utilizarán bibliotecas especializadas para la manipulación de tensores y la gestión de la lógica de recuperación vectorial (por ejemplo, utilizando bases de datos en memoria para la agilidad de experimentación iterativa). La orquestación agéntica será codificada utilizando los principios de diseño recomendados por la documentación técnica del Google Agent Development Kit (ADK), definiendo claramente los roles, descripciones, herramientas e instrucciones del sistema (system prompts) para cada agente.

## **4.3. Validación y Evaluación del Prototipo** {#4.3.-validación-y-evaluación-del-prototipo}

***Protocolo de pruebas, escenarios y demostración***

Se estructurará un protocolo de evaluación metódico utilizando escenarios de prueba generados a partir de un histórico real de consultas de alta complejidad formuladas por los consultores. La demostración oficial involucró a un grupo focal compuesto por ingenieros líderes de diversas disciplinas. 

A través de la interfaz de la demostración, los usuarios ejecutarán guiones de prueba específicos que buscan forzar al sistema a correlacionar datos de normativas pasadas con parámetros de diseño estructural. Se habilitarán instrumentos de feedback integrados en la interfaz (como validación binaria de pulgar arriba/abajo) para recolectar las impresiones de los expertos en la materia (SMEs) sobre la precisión técnica, coherencia sintáctica y utilidad pragmática de las respuestas generadas. 

Para asegurar la reproducibilidad de la evaluación, las consultas utilizadas en los escenarios de prueba serán estructuradas como un conjunto de preguntas representativas del dominio técnico de la consultoría minera y de ingeniería. Cada consulta será evaluada tanto mediante métricas algorítmicas de recuperación y generación como mediante validación experta por parte de los SMEs participantes. Este enfoque permite contrastar la calidad objetiva del sistema con la utilidad práctica percibida por los usuarios finales.

***Resultado de pruebas y métricas alcanzadas***

Para garantizar la objetividad científica de la validación, el feedback humano se triangulará con evaluaciones algorítmicas utilizando el estándar de la industria RAGAS (Retrieval Augmented Generation Assessment). RAGAS emplea heurísticas basadas en LLMs para evaluar múltiples dimensiones del canal sin necesidad de conjuntos de datos anotados manualmente por humanos.

| Dimensión RAGAS | Definición Técnica | Métrica Objetivo para Aceptación |
| :---- | :---- | :---- |
| **Fidelidad (Faithfulness)** | Mide la proporción de afirmaciones generadas que pueden inferirse lógicamente del contexto recuperado, penalizando directamente las alucinaciones algorítmicas. | **≥ 0.80** (escala 0-1). Penalización directa de alucinaciones respecto al contexto recuperado. (Asegurando la estricta adherencia a la documentación corporativa). |
| **Relevancia de la Respuesta** | Cuantifica el grado en que la respuesta generada aborda directamente la intencionalidad de la consulta del usuario, evitando desviaciones temáticas. | **≥ 0.80** (escala 0-1). Respuestas enfocadas en la intencionalidad de la consulta. (Garantizando respuestas concisas, directas y altamente enfocadas). |
| **Precisión Contextual** | Evalúa si la base de datos vectorial posiciona los fragmentos de texto verdaderamente útiles en los rangos superiores (top-K) de los resultados recuperados. | **MRR ≥ 0.75** Alta puntuación de MRR (Mean Reciprocal Rank). |
| **Seguridad del Sistema (Guardrails)** | Evalúa la capacidad del sistema para detectar, bloquear o neutralizar consultas maliciosas o prompts diseñados para manipular el comportamiento del modelo, incluyendo intentos de *prompt injection*, extracción de información sensible o solicitudes fuera del dominio permitido. | **Tasa de bloqueo ≥ 95 %** de prompts maliciosos o inseguros detectados durante escenarios de prueba controlados. |

# **CAPÍTULO V** {#capítulo-v}

# **PLAN DE SIGUIENTE FASE** {#plan-de-siguiente-fase}

## **5.1. Roadmap y Siguientes Pasos** {#5.1.-roadmap-y-siguientes-pasos}

En la segunda etapa, el código experimental de los notebooks será refactorizado siguiendo principios de ingeniería de software robustos (como la inyección de dependencias y el manejo asíncrono) para ser servido a través de un framework web moderno de alto rendimiento (como FastAPI). La base de datos vectorial se migrará a la infraestructura gestionada de AWS o AZURE para simular condiciones de latencia reales. Finalmente, se construirá un cliente web ligero utilizando tecnologías orientadas a datos (como Streamlit) para proporcionar una ventana interactiva al motor de inferencia y se ejecutarán las pruebas RAGAS.

*![][image2]*

## **5.2. Cronograma**  {#5.2.-cronograma}

El proyecto se estructura en una ruta crítica de seis meses, dividida en cuatro fases evolutivas. Inicia con una etapa de Ingesta y Vectorización (Meses 1-2) centrada en el procesamiento de infraestructura y conversión semántica de documentos. Posteriormente, en el Mes 3, se ejecutará un MVP y Piloto Cerrado con early adopters para validar la funcionalidad core. La fase de Iteración y Ajuste (Mes 4\) se dedicará a la optimización mediante feedback y métricas RAGAS, culminando en los Meses 5 y 6 con el Despliegue Progresivo y el rollout total de la cartera.

| Fase | Temporalidad | Título de la Etapa | Descripción de Actividades |
| :---- | :---- | :---- | :---- |
| **1** | **Mes 1 – 2** | Ingesta y Vectorización | Ejecución de vectorización sobre una base de  documentos, configuración de la infraestructura base y Notebooks en Python. |
| **2** | **Mes 3** | MVP y Piloto Cerrado | Lanzamiento del Producto Mínimo Viable (MVP) en python. |
| **3** | **Mes 4** | Iteración y Ajuste | Corrección de errores basada en el feedback de usuarios y validación técnica mediante métricas RAGAS. |
| **4** | **Mes 5 – 6** | Despliegue Progresivo | *Rollout* gradual de la solución para abarcar la totalidad de la cartera de clientes o proyectos, crear la interfaz gráfica. |

# **CONCLUSIONES**  {#conclusiones}

El presente informe permitió definir la arquitectura completa del sistema RAG agéntico, incluyendo el pipeline de ingestión documental, la estructura de metadatos para filtrado vectorial, la jerarquía de agentes especializados sobre Google ADK y los mecanismos de seguridad perimetral.Como resultado concreto de esta fase de diseño, se establecieron umbrales cuantitativos de aceptación bajo el marco RAGAS: Fidelidad ≥ 0.85, Relevancia de Respuesta ≥ 0.80 y MRR ≥ 0.75. Asimismo, se definieron metas operativas orientadas a la reducción del tiempo promedio de búsqueda documental en al menos un 50% respecto a los métodos manuales vigentes, así como una tasa de bloqueo de guardrails ≥ 95% frente a inyecciones adversariales. Estos indicadores constituyen la línea base verificable contra la cual se evaluará el prototipo funcional al finalizar la fase 2\.

No obstante, se reconocen limitaciones inherentes al alcance de esta fase. El prototipo operará sobre un subconjunto curado y representativo del repositorio corporativo. Asimismo, la latencia de inferencia del LLM en consultas que involucran múltiples agentes especializados representa un riesgo para la experiencia del usuario final que deberá ser evaluado empíricamente durante el piloto cerrado del Módulo I.

El proceso de diseño también generó aprendizajes relevantes para las siguientes fases. Se identificó la necesidad de trade-offs entre distintas etapas como la granularidad del chunking y la latencia del sistema. Este hallazgo refuerza la necesidad de evaluar comparativamente configuraciones de chunking, embedding, etc. durante la experimentación del Módulo I. Adicionalmente, se determinó que la combinación de búsqueda semántica vectorial con filtrado previo por metadatos estructurados  resulta indispensable para reducir el espacio de búsqueda en corpus de alta densidad técnica, particularmente cuando las consultas involucran disciplinas o proyectos específicos.

En síntesis, la presente fase establece las bases arquitectónicas y metodológicas necesarias para el desarrollo del MVP del sistema RAG agéntico. Los criterios de éxito definidos —detallados en las secciones 1.3 y 4.3— permitirán evaluar de manera objetiva si el prototipo alcanza los niveles de precisión, seguridad y eficiencia operativa requeridos antes de avanzar hacia una fase de despliegue progresivo.

# **REFERENCIAS BIBLIOGRÁFICAS** {#referencias-bibliográficas}

| \[1\] | Engineering RAG Systems for Real-World Applications: Design, Development, and Evaluation, arXiv, 2026\. \[Online\]. Available: https://arxiv.org/html/2506.20869v2 |
| :---- | :---- |
| \[2\] | Business insights using RAG–LLMs: a review and case study, Taylor & Francis, 2024\. \[Online\]. Available: https://www.tandfonline.com/doi/abs/10.1080/12460125.2024.2410040 |
| \[3\] | R. Obrai, "Google Agent Development Kit (ADK): No-Code vs Code-First Agents," Medium, 2026\. \[Online\]. Available: https://medium.com/@rohitobrai11/google-agent-development-kit-adk-no-code-vs-code-first-agents-28ccc3f44bbb |
| \[4\] | RAGAS: Automated Evaluation of Retrieval Augmented Generation," ACL Anthology, 2024\. \[Online\]. Available: https://aclanthology.org/2024.eacl-demo.16.pdf |
| \[5\] | C. Wan, "Amazon Bedrock vs. Azure OpenAI: A Comprehensive Comparison of Generative AI Services," Medium, 2026\. \[Online\]. Available: https://charleswan111.medium.com/amazon-bedrock-vs-azure-openai-a-comprehensive-comparison-of-generative-ai-services-45013e49fecd |
| \[6\] | "LLM guardrails: Best practices for deploying LLM apps securely," Datadog, 2026\. \[Online\]. Available: https://www.datadoghq.com/blog/llm-guardrails-best-practices/ |
| \[7\] | "Agentic RAG: Types, Applications, and Implementation Guide," Softweb Solutions, 2026\. \[Online\]. Available: https://www.softwebsolutions.com/resources/agentic-rag-types-and-implementation-guide/ |
| \[8\] | "Securing LLM Systems Against Prompt Injection," NVIDIA Technical Blog, 2026\. \[Online\]. Available: https://developer.nvidia.com/blog/securing-llm-systems-against-prompt-injection/ |
| \[9\] | "Ragas: Automated Evaluation of Retrieval Augmented Generation," arXiv, 2023\. \[Online\]. Available: https://arxiv.org/html/2309.15217v2 |
| \[10\] | "Guidebook for Evaluating Mining Project EIAs," Environmental Law Alliance Worldwide, 2026\. \[Online\]. Available: https://elaw.org/wp-content/uploads/archive/attachments/publicresource/guidebook\_for\_evaluating\_mining\_project\_eias\_english.pdf 
