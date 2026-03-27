# Resumen de Clase: Arquitecturas de Modelos de Forecasting

## Título
Arquitecturas de Modelos de Forecasting: TimesNet y PatchTST

## Temas Principales
*   **Logística del Curso:** Organización de presentaciones de papers y grupos de trabajo.
*   **Presentación de TimesNet:**
    *   Transformación de series temporales 1D a tensores 2D.
    *   Uso de bloques Inception y convoluciones 2D.
    *   Captura de variaciones temporales multi-escala (intra-periodo e inter-periodo).
    *   Uso de Transformada Rápida de Fourier (FFT) para identificar periodicidades.
*   **Análisis y Discusión sobre TimesNet:**
    *   Comparación con RNNs y Transformers.
    *   Evaluación de errores en diferentes horizontes de tiempo y granularidades (minutos vs horas).
    *   Discusión sobre eficiencia computacional vs. complejidad del modelo (ResNext vs. Inception).
    *   Métrica CKA (Centered Kernel Alignment) para evaluar versatilidad de representaciones.
*   **Presentación de PatchTST:**
    *   Solución a la "paradoja de los Transformers" en forecasting.
    *   Concepto de "Patching": agrupación de puntos de datos para conservar contexto local y semántico.
    *   Independencia de canales (Channel Independence).
    *   Reducción de complejidad computacional y mejora en la capacidad de generalización (Transfer Learning).

## Resumen Detallado
La sesión se centra en la presentación y discusión de artículos académicos (papers) relacionados con arquitecturas avanzadas para la predicción de series temporales (forecasting). Tras una breve coordinación logística, el **Grupo 12 presenta el modelo "TimesNet"**.

**TimesNet** se propone como una arquitectura versátil capaz de transformar series temporales unidimensionales en tensores 2D para aprovechar la potencia de las redes convolucionales modernas. El modelo utiliza la Transformada Rápida de Fourier (FFT) para analizar la serie en el dominio de la frecuencia, identificando los periodos más significativos. Basándose en estos periodos, la serie se reestructura en bloques 2D, permitiendo que bloques de tipo "Inception" capturen patrones complejos tanto dentro de un mismo periodo (intra-periodo) como entre diferentes periodos (inter-periodo). Se destaca su estructura residual y su capacidad para adaptarse a diversas tareas como predicción, imputación y clasificación.

Durante la discusión, se analiza el comportamiento del error de predicción. Se observa que, contraintuitivamente en algunos casos, el error puede disminuir en horizontes más largos o comportarse mejor en granularidades más finas (minutos) dependiendo de la capacidad del modelo para capturar patrones de alta frecuencia versus tendencias a largo plazo. También se debate sobre el costo computacional; modelos más grandes como ResNeXt pueden ofrecer mejor desempeño teórico pero requieren tiempos de entrenamiento significativamente mayores, mientras que bloques tipo Inception ofrecen un balance más eficiente. Se introduce el concepto de **CKA (Centered Kernel Alignment)** como métrica para comparar la similitud de las representaciones aprendidas por las capas del modelo, indicando qué tan versátil es el modelo para diferentes tareas.

Posteriormente, el **Grupo 4 presenta "PatchTST"**. Este modelo surge como respuesta a hallazgos previos donde modelos lineales simples superaban a Transformers complejos en forecasting. PatchTST introduce dos innovaciones clave: **Patching** y **Channel Independence**. El "patching" consiste en agrupar subseries de puntos de datos en vectores (parches), lo cual permite al Transformer procesar segmentos con contexto semántico local en lugar de puntos aislados, reduciendo drásticamente la complejidad computacional y de memoria (de cuadrática a lineal con respecto a la longitud de la serie dividida por el tamaño del parche). La independencia de canales trata cada serie temporal multivariada como una serie univariada independiente que comparte los mismos pesos del modelo, lo que mejora la capacidad de generalización y facilita el aprendizaje por transferencia (Transfer Learning).

## Conceptos Clave
*   **TimesNet:** Arquitectura que convierte series 1D en 2D para aplicar visión por computadora a series temporales.
*   **Transformada Rápida de Fourier (FFT):** Utilizada en TimesNet para descomponer la serie y encontrar periodicidades dominantes.
*   **PatchTST:** Modelo basado en Transformers que utiliza parches de datos para mejorar la eficiencia y precisión.
*   **Patching:** Técnica de agrupar pasos de tiempo consecutivos en tokens, preservando información semántica local.
*   **Independencia de Canales:** Estrategia en PatchTST donde cada variable de la serie se procesa por separado por el mismo backbone.
*   **CKA (Centered Kernel Alignment):** Métrica de similitud para comparar representaciones internas de redes neuronales.
*   **Horizonte de Predicción:** La cantidad de pasos de tiempo futuros que el modelo intenta predecir; su longitud afecta la incertidumbre y el error.
