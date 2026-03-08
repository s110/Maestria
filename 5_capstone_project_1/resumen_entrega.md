# Resumen Ejecutivo del Proyecto: GeoMinder

**Fecha del Resumen:** 8 de Marzo de 2026
**Proyecto:** GeoMinder: Agentic RAG System for Mining Consulting
**Institución:** UTEC - Escuela de Posgrado
**Maestría:** Ciencia de Datos e Inteligencia Artificial

---

## 1. Información General del Proyecto
**Equipo de Trabajo:**
*   Sebastián Lopez Medina
*   Brajan Nieto Espinoza
*   Mateo Tapia Chasquibol

**Asesor:** PhD. Vicente Machaca Arceda

**Visión General:**
GeoMinder es una solución de "Ingeniería Cognitiva" diseñada para transformar la gestión del conocimiento en consultoras mineras. El sistema evoluciona la infraestructura de datos pasiva (archivos estáticos) hacia una inteligencia activa mediante una arquitectura RAG (Retrieval-Augmented Generation) Agéntica.

---

## 2. Definición del Problema: "El Olvido Corporativo"
Las consultoras de ingeniería minera enfrentan ineficiencias críticas debido al manejo de grandes volúmenes de documentación técnica histórica y normativa.

*   **Pérdida Operativa:** Se estiman **+9,000 horas anuales** perdidas en tareas manuales de búsqueda y revisión de documentos de bajo valor.
*   **Impacto Económico:** Aproximadamente **$350,000 USD** gastados anualmente en revisión de información.
*   **Información "Dormida":** Más de **15 años** de datos e inteligencia operativa no son explotados eficientemente.
*   **Limitaciones Actuales:** Los buscadores tradicionales (Ctrl+F) fallan con consultas complejas, y las IAs genéricas presentan riesgos de alucinación y fuga de datos confidenciales.

---

## 3. Solución Propuesta: GeoMinder
Una plataforma API con arquitectura **RAG Agéntico** que orquesta agentes especializados para realizar tareas de ingeniería complejas.

### Funcionalidades Clave
1.  **Búsqueda Semántica Inteligente:** Recuperación precisa de información técnica y normativa.
2.  **Validación Cruzada:** Agentes que verifican la consistencia de los datos contra normativas (ej. DS 132) y parámetros de diseño.
3.  **Generación de Informes:** Capacidad de redactar borradores de propuestas y capítulos técnicos con un 70% de avance inicial.
4.  **Citas y Trazabilidad:** Respuestas fundamentadas con referencias directas a los documentos internos.

### Diferenciadores (Ventaja Competitiva)
*   **Orquestación Agéntica:** A diferencia de un RAG clásico, GeoMinder utiliza **Google ADK (Agent Development Kit)** para razonamiento jerárquico.
*   **Soberanía del Dato:** Infraestructura privada donde los datos no entrenan modelos de terceros.
*   **Especialización:** Diseñado específicamente para estructuras complejas de ingeniería, no para texto genérico.

---

## 4. Arquitectura y Aspectos Técnicos
El diseño técnico prioriza la seguridad, la escalabilidad y la precisión técnica.

*   **Framework de Orquestación:** Google ADK (seleccionado sobre LangChain y AutoGen por su capacidad de control).
*   **Infraestructura Cloud:**
    *   Despliegue híbrido/seguro en **AWS** (preferido por madurez en bases de datos vectoriales) o **Microsoft Azure**.
    *   Aislamiento de infraestructura para privacidad de datos.
*   **Seguridad (Guardrails):** Implementación de filtros de seguridad perimetral para evitar:
    *   *Prompt Injection*.
    *   Fugas de PII (Información Personal Identificable).
    *   Respuestas inseguras o alucinaciones.
*   **Datos:** Procesamiento de documentos no estructurados (PDFs, Word, Informes técnicos). Volumen estimado de ingesta inicial: **+73,000 documentos**.

---

## 5. Caso de Negocio y ROI
El proyecto presenta una viabilidad financiera sólida basada en la recuperación de eficiencia operativa.

*   **Inversión Inicial Estimada:** ~$50,000 USD (Principalmente costos de etiquetado, vectorización e infraestructura).
*   **Retorno de Inversión (ROI):** Recuperación estimada en **menos de 1 año**.
*   **Métricas de Éxito (KPIs):**
    *   **RAGAS Score:** Minimización de la tasa de alucinación.
    *   **Adopción:** Validación por ingenieros especialistas.
    *   **Eficiencia:** Reducción drástica de horas-hombre (HH) en elaboración de informes.

---

## 6. Plan de Implementación (Roadmap)
El proyecto se estructura en un plan de 6 meses hasta el despliegue progresivo.

1.  **Mes 1-2 (Ingesta):** OCR semántico de +73k documentos y configuración de infraestructura vectorizada.
2.  **Mes 3 (MVP):** Despliegue de Piloto Cerrado en 1 proyecto para "Early Adopters".
3.  **Mes 4 (Iteración):** Ajuste de errores basado en feedback y validación técnica (RAGAS).
4.  **Mes 5-6 (Despliegue):** Rollout gradual a toda la cartera de proyectos.

---

## 7. Alcance del Prototipo Académico
Para efectos del "Informe Preliminar" de la maestría, el entregable incluye:
*   **Núcleo Algorítmico:** Notebooks de Python con la lógica RAG y comparativas de rendimiento.
*   **API REST:** Interfaz programática para exponer los servicios de recuperación y generación.
*   **Interfaz de Usuario:** Aplicación tipo chatbot (posiblemente Streamlit) para interacción final.
*   **Validación:** Protocolo de pruebas con escenarios reales de ingeniería y métricas de recuperación (Recall/MRR).
