# Archivo 1: Trabajo Aplicativo Final

**UTEC**
**Evaluación Financiera de Proyectos**

### **Trabajo Aplicativo Final**
**(70% de Calificación de Proyecto Parte 2)**

El objeto de estudio aquí es su capstone y lo que buscamos es su capítulo financiero bajo este esquema:

**1. Resumen financiero del proyecto**
*   Qué se evalúa.
*   Horizonte de análisis.
*   Inversión requerida.
*   Resultado financiero principal.
*   Recomendación preliminar.

**2. Modelo de ingresos o beneficios**
Explicar cómo el proyecto genera valor.
Debe quedar claro si el valor viene de:
*   monetización directa,
*   monetización indirecta,
*   ahorro,
*   eficiencia,
*   reducción de pérdidas,
*   reducción de riesgo,
*   aumento de ingresos.

Regla:
Si no tiene fórmula, no es beneficio financiero.

**3. Estructura de costos**
Separar costos visibles y ocultos:
*   desarrollo,
*   infraestructura,
*   datos,
*   labeling,
*   HITL,
*   APIs,
*   licencias,
*   mantenimiento,
*   reentrenamiento,
*   monitoreo,
*   soporte,
*   deuda técnica.

Regla:
No basta presupuestar construir el modelo; deben presupuestar operarlo.

**4. Flujo de caja e indicadores**
Presentar:
*   flujo de caja libre,
*   VPN,
*   TIR,
*   payback,
*   punto de equilibrio si aplica.

Debe indicarse claramente:
*   WACC usado,
*   horizonte,
*   moneda,
*   supuestos base.

**5. Riesgo e incertidumbre**
Incluir:
*   sensibilidad,
*   escenarios,
*   Montecarlo.

La pregunta central es:
¿Qué tan robusto es el proyecto si los supuestos cambian?

**6. Recomendación final**
Cerrar con una decisión financiera defendible:
*   GO,
*   NO-GO,
*   GO condicional.

Debe estar sustentada en números, no en entusiasmo tecnológico.

**RÚBRICA DE CALIFICACIÓN**

| Criterio | Peso |
| :--- | :--- |
| Claridad del modelo de negocio y de su beneficio financiero | 15% |
| Calidad y coherencia de supuestos | 15% |
| Estructura completa de costos, incluyendo costos ocultos IA/ML | 15% |
| Flujo de caja, VPN, TIR y payback correctamente calculados | 20% |
| Sensibilidad, escenarios y Montecarlo | 20% |
| Recomendación y calidad de la decisión | 15% |
| **Total** | **100%** |

**CRITERIOS DE EXCELENCIA**
Un excelente trabajo demuestra:
*   de dónde viene el valor,
*   qué supuestos lo sostienen,
*   qué costos podrían estar ocultos,
*   qué variables destruyen el VPN,
*   qué probabilidad hay de crear valor,
*   y qué decisión debe tomar un inversionista.

**CHECKLIST DE CONTROL ANTES DE ENTREGAR**
*   El proyecto tiene una fórmula clara de generación de valor.
*   El modelo incluye CAPEX y OPEX.
*   Se incluyen costos de datos, cloud, mantenimiento y reentrenamiento.
*   El flujo de caja calcula VPN, TIR y payback.
*   Hay sensibilidad de variables críticas.
*   Hay escenarios pesimista, base y optimista.
*   Hay simulación Montecarlo.
*   Se reporta probabilidad de VPN positivo.
*   La recomendación final es GO, NO-GO o GO condicional.
*   La decisión está sustentada en números.

**FORMATO DE ENTREGA:**
*   1 Presentación ejecutiva (5 slides) pdf o pptx
*   1 documento con los puntos 1-6 solicitados

---

# Archivo 2: Sesión 07 - Análisis de Riesgo e Incertidumbre

**UTEC Posgrado | Una escuela para Early Adopters**
**MAESTRÍA EN CIENCIA DE DATOS & IA**
**EVALUACIÓN FINANCIERA DE PROYECTOS**
**Sesión 07: Análisis de Riesgo e Incertidumbre**

**Temario:**
1. **Análisis de Sensibilidad**: Variables en movimiento
2. **Construcción de Escenarios**: Análisis situacional con cambios en múltiples variables
3. **Análisis de Montecarlo**: Análisis con cambios en variables a través de estadísticos

**Objetivos de Aprendizaje**
*   **Bloque 1: Incertidumbre sobre el futuro y Variabilidad de resultados**
    *   Introducción al análisis de sensibilidad
*   **Bloque 2: Planteamiento de Escenarios y su Análisis**
    *   Comparación con el análisis de sensibilidad y construcción
*   **Bloque 3: Análisis de multiplicidad de escenarios: Montecarlo**
    *   Aplicaciones estadísticas al análisis de escenarios múltiples

**¿Por qué los modelos financieros siempre están equivocados?**
CASO FICTICIO - Startup de EdTech (2023)
| VARIABLE | PROYECCION | REALIDAD |
| :--- | :--- | :--- |
| Usuarios año 1 | 5,000 | 2,800 |
| Precio promedio | $120/mes | $95/mes |
| Churn anual | 8% | 18% |
| **VPN** | **$2.1M** | **-$450K** |

¿Qué salió mal?
Trataron números INCIERTOS como si fueran CIERTOS.
*"Todos los modelos están equivocados. Algunos son útiles."* - George Box (estadístico famoso)

**¿Qué es Análisis de Sensibilidad?**
DEFINICION SIMPLE: Cambiar UNA variable de entrada y ver cuánto cambia el resultado (VPN).
PREGUNTA QUE RESPONDE: "Que pasa con mi VPN si me equivoque en el precio?"
*   Precio = $100 -> VPN = $800K
*   Precio = $110 -> VPN = $1.2M (+50%)
*   Precio = $90 -> VPN = $400K (-50%)
CONCLUSION: Precio es MUY sensible.

**Tutorial Excel – Tabla de Datos PASO A PASO**
*   PASO 1: Construir modelo simple con: Celda B2: Precio (input) / Celda B10: VPN (output, con fórmula)
*   PASO 2: Crear tabla a la derecha con precios en columna
*   PASO 3: En celda superior derecha poner =B10
*   PASO 4: Seleccionar toda la tabla
*   PASO 5: Data > Análisis de Hipótesis > Tabla de Datos
*   PASO 6: Celda de entrada (columna) : B2 (celda del Precio)
*   PASO 7: Click Aceptar - La tabla se llena automáticamente
*   TIP: Si sale error #REF, verifica que B10 tenga fórmula, no valor fijo.

**EJERCICIO 1: Sensibilidad 1D**
CASO: Proyecto de food delivery
MODELO BASE:
*   Inversión inicial: $300,000
*   Pedidos año 1: 20,000
*   Ticket promedio: $25
*   Margen bruto: 25%
*   Crecimiento anual: 15%
*   WACC: 15%
*   Horizonte: 3 años
*   VPN BASE: $127,450

TAREA (8 minutos):
1. Abrir archivo Ejercicios S7.xlsx
2. Construir Tabla de Datos para: Ticket Promedio (rango: $20 a $30, incrementos $1) y Crecimiento Anual (rango 5% a 25%, incrementos 5%).
3. Responder: ¿Cuál variable impacta más? ¿Cuándo VPN es negativo?

**SOLUCION - Ejercicio 1**
SENSIBILIDAD TICKET PROMEDIO
| Ticket | VPN |
| :--- | :--- |
| $20 | -$39,130 |
| $22 | -$13,043 |
| $25 | $26,087 |
| $28 | $65,217 |
| $30 | $91,304 |

SENSIBILIDAD CRECIMIENTO
| Crec. | VPN |
| :--- | :--- |
| 5% | -$1,447 |
| 10% | $12,115 |
| 15% | $26,087 |
| 20% | $40,470 |
| 25% | $55,264 |

ANALISIS:
Ticket Promedio: Rango $130,434 (de -$39K a +$91K) - ALTA sensibilidad
Crecimiento: Rango $56,711 (de -$1K a $55K) - MEDIA sensibilidad
CONCLUSION: TICKET PROMEDIO es la variable crítica. Si cae a $20, PERDEMOS dinero. Debemos validar con piloto real.

**Sensibilidad 2D - Heat Map**
Cuando 2 variables cambian juntas
| | $20 | $22 | $25 | $28 | $30 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **5%** | -85K | -35K | 45K | 125K | 180K |
| **10%** | -70K | -18K | 82K | 180K | 248K |
| **15%** | -42K | 28K | 127K | 226K | 297K |
| **20%** | -15K | 73K | 180K | 287K | 365K |
| **25%** | 18K | 125K | 241K | 357K | 442K |

CODIGO DE COLOR: Rojo = VPN negativo (no invertir), Amarillo = VPN bajo (<$100K), Verde = VPN atractivo (>$100K).

**Sensibilidad vs. Escenarios**
| | SENSIBILIDAD | ESCENARIOS |
| :--- | :--- | :--- |
| Variables | UNA a la vez | MULTIPLES simultaneas |
| Pregunta | Y si esto cambia? | Qué pasa si el mundo se ve ASI? |
| Ejemplo | Precio +10% | Recesión: precios -15%, volumen -20%, costos +10% |
| Realismo | Artificial (variables no independientes) | Mas realista (correlación) |

EJEMPLO CONCRETO: Escenario 'Recesión económica'
*   Demanda baja (la gente compra menos)
*   Precio NO puede ser alto (nadie paga precios altos en recesión)
*   Costos fijos altos (no bajan aunque vendas menos)
*   WACC alto (capital más caro en crisis)
*   Las variables se mueven JUNTAS, no solas

**Construcción de Escenarios**
3 ESCENARIOS ESTANDAR:
| Escenario | Descripcion | Probabilidad |
| :--- | :--- | :--- |
| PESIMISTA | Todo sale mal | 25% |
| BASE | Expectativa realista | 50% |
| OPTIMISTA | Todo sale bien | 25% |

VPN ESPERADO (ponderado):
E(VPN) = (0.25 x VPN_pesimista) + (0.50 x VPN_base) + (0.25 x VPN_optimista)
COEFICIENTE DE VARIACION (riesgo relativo): CV = Desviación Estándar / E(VPN)
INTERPRETACION: CV < 0.3 = Riesgo bajo | 0.3 < CV < 0.8 = Riesgo medio | CV > 0.8 = Riesgo ALTO.

**Tutorial: Administrador de Escenarios en Excel**
*   PASO 1: Datos > Análisis de Hipótesis > Administrador de Escenarios
*   PASO 2: Click ‘Agregar'
*   PASO 3: Nombre del escenario: 'Pesimista' (Celdas cambiantes: ej: B2:B5)
*   PASO 4: Click Aceptar
*   PASO 5: Ingresar valores pesimistas para cada variable
*   PASO 6: Repetir pasos 2-5 para 'Base' y 'Optimista'
*   PASO 7: Click ‘Resumen...' (Celdas de resultado: Celda del VPN)
*   PASO 8: Click Aceptar -> RESULTADO: Nueva hoja de cálculo con tabla comparativa.

**EJERCICIO 2: Escenarios**
CASO: Expansión de cadena de cafeterías
MODELO BASE: Inversión $450,000 | Tiendas 3 | Ventas/tienda/día $800 | Margen 40% | OPEX fijo $120K/año | Horizonte 4 años | WACC 14% | VPN BASE $185,200

VALORES SUGERIDOS:
| Variable | Pesimista | Base | Optimista |
| :--- | :--- | :--- | :--- |
| Ventas/dia | $600 | $800 | $1,000 |
| Margen | 35% | 40% | 45% |
| OPEX fijo | $135K | $120K | $110K |
| WACC | 18% | 14% | 12% |

**SOLUCION - Ejercicio 2**
| Escenario | VPN | Probabilidad |
| :--- | :--- | :--- |
| Pesimista | -$555,656 | 25% |
| Base | -$31,888 | 50% |
| Optimista | $553,648 | 25% |

CALCULOS:
E(VPN) = (0.25 x -$555K) + (0.50 x -$32K) + (0.25 x $553K) = -$16,446
Desviación Estándar: $392,502
CV = $392,502 / $16,446 = 23.87
INTERPRETACION: E(VPN) negativo = Proyecto no rentable en promedio. CV > 1 = ALTO RIESGO.
RECOMENDACION: NO-GO rotundo.

**Limitación de los 3 Escenarios**
PROBLEMA: Los escenarios solo exploran 3 PUNTOS del universo de posibilidades. ¿Qué pasa con los INFINITOS casos intermedios? (600 - 800 - 1,000). ¿Y si la demanda real es 720? ¿ó 850? ¿ó 950?
REALIDAD: Las variables no son discretas (3 valores), son CONTINUAS (infinitos valores entre min y max).
SOLUCION: SIMULACION DE MONTECARLO.

**¿Qué es Montecarlo?**
DEFINICION: Generar muchos escenarios aleatorios y calcular el resultado (VPN) en cada uno.
PROCESO EN 5 PASOS:
1. Identificar variables inciertas (Ej: Demanda, Precio, Costos)
2. Asignar distribucion de probabilidad (Ej: Demanda ~ Normal(media=800, desv=120))
3. Generar 10,000 valores aleatorios de cada variable
4. Calcular VPN para cada combinacion (10,000 VPNs)
5. Analizar distribucion de VPNs
OUTPUT FINAL: Histograma mostrando todos los VPNs posibles y su frecuencia. Calcular P(VPN > 0) y percentiles.

**Distribuciones de Probabilidad**
1. NORMAL (Campana): Simétrica alrededor de media. Parámetros: media, desv.std. Ej: Errores de pronostico.
2. TRIANGULAR: 3 puntos: min, moda, max. Fácil de estimar con expertos. Ej: Estimación de costos.
3. UNIFORME: Todos los valores igual de probables. Ej: Sin información previa.

COMO ELEGIR:
*   Tienes datos históricos? NORMAL
*   Tienes 3 estimados expertos? TRIANGULAR
*   No tienes nada? UNIFORME
IMPORTANTE: No necesitas conocer toda la teoría estadística. Python/Excel hacen los cálculos por ti.

**EJERCICIO 3: Montecarlo en Google Colab (DEMO)**
CASO: Proyecto de consultoría
VARIABLES INCIERTAS:
*   Precio por hora: Normal(media=$150, desv=$20)
*   Horas vendidas/mes: Triangular(min=120, moda=160, max=200)
*   OPEX mensual: Normal(media=$18,000, desv=$2,500)
INSTRUCCIONES:
PASO 1-6: Abrir S7_Ejercicio3_Montecarlo.ipynb, importar librerías, generar variables, calcular VPN, gráfico histograma, estadísticas clave.

**Interpretación de Resultados**
EJEMPLO DE OUTPUT:
*   E(VPN): $ 124,580
*   Desv. Est.: $ 48,200
*   P(VPN > 0): 96.3%
*   Percentil 10: $ 58,100
*   Percentil 50: $ 125,000
*   Percentil 90: $ 189,400
QUÉ SIGNIFICA CADA METRICA: E(VPN) = Valor promedio de 10,000 simulaciones. P(VPN > 0) = Probabilidad de éxito. Percentil 10 = En el 10% PEOR de los casos, aún ganas $58K.

**Reglas de Decisión con Montecarlo**
| Metrica | Criterio GO | Criterio NO-GO |
| :--- | :--- | :--- |
| P(VPN > 0) | > 80% | < 60% |
| P10 | Positivo | Muy negativo |
| CV | < 0.5 | > 1.5 |

CASOS ESPECIALES:
*   CASO 1: P(VPN>0)=85%, pero P10=-$500K -> NO-GO (el downside es catastrófico)
*   CASO 2: P(VPN>0)=65%, pero P90=$10M -> Considerar GO si tolerancia a riesgo alta
*   CASO 3: P(VPN>0)=95%, P10=$200K, P90=$800K -> CLEAR GO
REGLA DE ORO: Mira el P10 (downside). Si puedes vivir con ese escenario, adelante.

**Ventajas vs. Desventajas de Montecarlo**
*   VENTAJAS: Explora MILES de escenarios, cuantifica probabilidades precisas, identifica distribución completa, permite análisis de sensibilidad post-simulación.
*   DESVENTAJAS: Requiere SOFTWARE, necesitas definir distribuciones, puede dar falsa precisión si inputs son malos, más difícil de explicar a directorio.
RECOMENDACION: Empieza con sensibilidad. Si proyecto >$1M, haz Montecarlo.

**EJERCICIO 4: Caso Integrado**
CASO: Lanzamiento de app móvil. Variables inciertas (Descargas, Conversión, Precio, Churn, CAPEX). Tarea en Google Colab: S7_Ejercicio4_AppMovil.ipynb. 15 MINUTOS.

**Variables Críticas - Análisis de Correlación**
PREGUNTA: De las 5 variables inciertas, cuál impacta MAS el VPN?
METODO: Calcular correlación de Pearson entre cada variable y VPN.
VARIABLES MAS CRITICAS: Descargas (+0.782), Conversión (+0.654), Churn (-0.421), Precio (+0.312), CAPEX (-0.156).
CONCLUSION: Enfoca tu esfuerzo en AUMENTAR DESCARGAS y MEJORAR CONVERSION.

**TAREA SEMANA 7: Evaluación de Planta de Manufactura**
ENTREGABLES (3 archivos):
1. EXCEL: Apellido_Taller3.xlsx (3 tabs: Modelo FCF, Sensibilidad 1D, Escenarios)
2. GOOGLE COLAB: Apellido_Taller3.ipynb (Simulación Montecarlo, Distribución VPN, Tornado chart)
3. SLIDE: Apellido_Taller3.pptx (1 slide: Recomendación GO/NO-GO, Métricas, Top 3 variables).
DEADLINE: Sábado 9:00 AM. TIEMPO ESTIMADO: 90 minutos.

**TAKEAWAY FINAL**
Nos falta poco para ir mejorando nuestra apreciación de los proyectos. Próxima pregunta: ¿cómo presento mis números a un CFO / inversionista?

---

# Archivo 3: Sesión 06 - Integración de Variables de Negocios IA / ML en Flujos de Caja

**UTEC Posgrado | Una escuela para Early Adopters**
**MAESTRÍA EN CIENCIA DE DATOS & IA**
**EVALUACIÓN FINANCIERA DE PROYECTOS**
**Sesión 06: Integración de Variables de Negocios IA / ML en Flujos de Caja**

**Temario:**
1. **Costos de Datos y HITL**: Conceptos y Traslación al Cash Flow
2. **Monetización de Datos**: ¿Cuánto valen los datos?
3. **Trade-Offs**: Velocidad-Exactitud-Costo. ¿Cómo los evaluamos financieramente?
4. **Total Cost of Ownership (TCO)**: Visión financiera del TCO

**Objetivos de Aprendizaje**
*   **Bloque 1: Costos Ocultos de IA/ML**: Datos, HITL, re-entrenamiento
*   **Bloque 2: Monetización de Datos**: APIs, venta datasets, valoración
*   **Bloque 3: Trade-offs Velocidad-Exactitud-Costo**: Costo del error, optimización
*   **Bloque 4: Total Cost of Ownership**: Build vs Buy vs SaaS, TCO real

**Bloque 1: Costos ocultos de IA/ML**
El GPU es solo el 25% del costo. El 75% restante esta OCULTO.
COSTOS OCULTOS:
1. DATOS: Adquisición, limpieza, almacenamiento, etiquetado
2. HUMAN IN THE LOOP: Anotadores, revisores, validadores
3. MANTENIMIENTO: Re-entrenamiento, model drift, debugging

**Anatomía de Costos: Pirámide Invertida**
*   INFRAESTRUCTURA (25%): GPU, Cloud, visible.
*   DATOS + HITL (45%): Labeling, limpieza, storage.
*   MANTENIMIENTO (30%): Re-training, drift, debugging, DevOps.

**Fórmula: Costo del Human-in-the-Loop (HITL)**
COSTO LABELING = (# registros x tiempo/registro x tarifa/hora) / 3600
COMPONENTES: Total de datos a anotar, segundos promedio (45-120 seg tipico), tarifa/hora ($15-25 tipico).
NOTA: HITL NO ESCALA como código. Es LINEAL con volumen.

**EJERCICIO 1: COSTO LABELING IMAGENES MEDICAS**
CASO: Sistema clasificacion imagenes rayos-X.
Dataset inicial: 50,000 imagenes. 2 anotadores/imagen. Tiempo: 45 seg/imagen. Tarifa: $18/hora.

**BLOQUE 2: MONETIZACION DE DATOS**
Los datos no son costo, son ACTIVO. Si sabes como monetizarlos.
PREGUNTA CLAVE: Cuanto vale tu dataset?
RESPUESTA: Depende de como lo uses: 1. Venta directa (one-time fee), 2. API de prediccion (ingreso recurrente), 3. Ventaja competitiva (valor indirecto).

**3 MODELOS DE MONETIZACION DE DATOS**
*   VENTA DIRECTA: Dataset completo, One-time fee (Ej: $50k-500k)
*   API PREDICCION: Precio por llamada, Ingreso recurrente (Ej: $0.05/query)
*   DATA MOAT: Ventaja competitiva, Valor indirecto, Difícil cuantificar
VALORACION EXPRESS:
Metodo 1: COSTO REPOSICION. Cuanto cuesta volver a generar el dataset? (Tiempo + labeling + infraestructura)
Metodo 2: VPN INGRESOS FUTUROS. NPV = Suma[Ingresos / (1+WACC)^t]

**BLOQUE 3: TRADE-OFFS EN MODELOS ML**
No puedes tener velocidad, exactitud y bajo costo SIMULTANEAMENTE.
EL TRIANGULO IMPOSIBLE:
*   VELOCIDAD: Latencia baja, alto throughput (Requiere infraestructura cara)
*   EXACTITUD: Alta precision, bajo error (Requiere modelos complejos, mas compute)
*   COSTO: Infraestructura barata (Limita velocidad y exactitud)

**MATRIZ DE PRIORIZACION POR INDUSTRIA**
| INDUSTRIA | PRIORIDAD 1 | PRIORIDAD 2 | PRIORIDAD 3 |
| :--- | :--- | :--- | :--- |
| Fintech Fraud | EXACTITUD (99%+ recall) | VELOCIDAD (<100ms) | COSTO (secundario) |
| E-commerce Recs | VELOCIDAD (<50ms) | COSTO (scale barato) | EXACTITUD (85% OK) |
| Healthcare Dx | EXACTITUD (>99.5%) | EXACTITUD (doble check) | VELOCIDAD (segundos OK) |
TU PRIORIZACION define qué modelo elegir y cuánto pagar.

**CUANTIFICAR EL COSTO DEL ERROR**
FORMULA COSTO TOTAL:
Costo Total = Costo Infra + (FN x $/FN) + (FP x $/FP)
DEFINICIONES:
*   False Negative (FN): Caso positivo que NO detectaste. Costo: ALTO.
*   False Positive (FP): Caso negativo que marcaste positivo. Costo: MEDIO.

**EJERCICIO 3: OPTIMIZACION ANTI-FRAUDE**
CASO: Fintech evalúa 2 modelos detección fraude (Premium 99% recall a $60K/mes vs Estandar 95% recall a $18K/mes). Volumen: 400,000 transacciones/mes. Tasa fraude real: 0.5% (2,000 casos). Costo promedio fraude no detectado: $3,200.

**BLOQUE 4: TOTAL COST OF OWNERSHIP (TCO)**
Construir el modelo es el 30% del esfuerzo. Operarlo en producción es el 70%.
TCO = TODA LA HISTORIA: Desarrollo (20%), Despliegue (10%), Operación (40%), Mantenimiento (30%).
ERROR TIPICO: Solo estimar CAPEX (30%) e ignorar OPEX recurrente (70%). RESULTADO: Presupuesto se acaba en año 1, modelo se degrada.

**BUILD vs BUY vs SaaS: COMPARACION**
| OPCION | CAPEX | OPEX | CONTROL | TIME-TO-MARKET |
| :--- | :--- | :--- | :--- | :--- |
| BUILD (In-house) | ALTO ($200k+) | MEDIO ($10-20k/m) | TOTAL (100%) | 6-12 meses |
| BUY (Licencia) | MEDIO ($50-150k) | BAJO ($2-5k/m) | ALTO (80%) | 3-6 meses |
| SaaS (API ext.) | BAJO ($10-30k) | ALTO ($5-15k/m) | BAJO (20%) | 1-4 semanas |
NO hay respuesta correcta. Depende de: budget, urgencia, expertise.

**EJERCICIO 4: TCO CHATBOT NLP (15 min)**
CASO: E-commerce evalua chatbot NLP para soporte. Opcion A (Build) vs Opcion B (SaaS). Calcular TCO 3 años, Break-even, NPV y recomendar.

**FRAMEWORK DE DECISION INTEGRADO**
| PREGUNTA | HERRAMIENTA | OUTPUT |
| :--- | :--- | :--- |
| 1. Cuánto cuesta? | Incluir HITL + datos | CAPEX + OPEX completo |
| 2. Cuánto vale? | Monetización directa o indirecta | Ingresos proyectados |
| 3. Qué accuracy necesito? | Costo error x volumen | Punto óptimo |
| 4. Build/Buy/SaaS? | TCO 3 años | NPV comparado |
| 5. Sigo adelante? | NPV > 0 + sensibilidad | GO / NO-GO |

**CHECKLIST: ANTES DE PRESENTAR AL COMITÉ DE PROYECTOS**
[ ] Incluí costo de labeling y datos
[ ] Proyecté OPEX recurrente realísticamente (3-5 años)
[ ] Cuantifiqué el costo del error (FN y FP)
[ ] Comparé al menos 2 alternativas
[ ] Calculé VPN, no solo payback simple
[ ] Probé sensibilidad: qué pasa si accuracy baja 5%?
[ ] Consideré time-to-market como costo (oportunidad)

**TAREA SEMANA 6: ANALISIS SISTEMA RECOMENDACION**
CASO: Retail evalúa sistema recomendación para e-commerce. Excel + 1 Slide PPT.

**TAKEAWAY FINAL**
Ya estamos integrando los temas tecnológicos en versión dinero. ¿Qué nos faltó integrar?

---

# Archivo 4: Sesión 05 - Taller Práctico de Infonomics

**UTEC Posgrado | Una escuela para Early Adopters**
**MAESTRÍA EN CIENCIA DE DATOS & IA**
**EVALUACIÓN FINANCIERA DE PROYECTOS**
**Sesión 05: Taller Práctico de Infonomics: Convertir datos, analítica e IA en beneficios financieros defendibles**

**Temario:**
1. **Taller 1**: Revisión, Solución y Discusión

**Objetivos de Aprendizaje**
*   Poner en contexto el uso del análisis financiero.
*   Caso de Trabajo.

**Caso inicial: StreamMax / Predictor AI**
StreamMax quiere implementar Predictor AI para identificar usuarios con alto riesgo de churn y activar campañas de retención.
*   Problema: Churn elevado y pérdida de ingresos recurrentes.
*   Solución: Modelo predictivo + campañas dirigidas de retención.
*   Decisión: GO condicional si el beneficio financiero es verificable.
Objetivo de la clase: pasar de “reducir churn” a una fórmula financiera defendible.

**Pregunta inicial**
¿De dónde viene realmente el valor financiero de Predictor AI?
*   No basta decir: “usa IA”, “mejora decisiones” o “reduce churn”.
*   Necesitamos traducir la solución a variables económicas.

**Infonomics: datos como activo económico**
*   Infonomics propone tratar la información como un activo que puede gestionarse, valorarse y monetizarse.
*   Los datos no valen por existir: valen cuando cambian decisiones que mueven dinero.
*   La monetización puede ser directa o indirecta.

**Monetización directa vs. indirecta**
*   **Monetización directa**: Vender datos, insights o productos basados en datos. Ejemplos: API de datos, dashboard premium. El dato se convierte explícitamente en producto o servicio.
*   **Monetización indirecta**: Usar datos para mejorar el negocio propio. Ejemplos: reducir churn, detectar fraude, optimizar inventario. El valor aparece en costos, ingresos, margen o riesgo.

**Mapa de beneficios financieros**
1. Ahorros verificables (Menor costo operativo, reprocesos)
2. Nuevos ingresos (Mayor conversión, upsell, pricing)
3. Pérdidas evitadas (Churn, fraude, mora evitados)
4. Productividad (Horas liberadas que se capturan financieramente)
5. Riesgo reducido (Menor probabilidad de impacto de eventos negativos)
6. Capital eficiente (Menor inventario, mejor utilización)
Un beneficio financiero debe explicar qué métrica cambia, cuánto cambia y cuánto vale.

**Ahorros verificables vs. nuevos ingresos**
*   **Ahorros verificables**: Reducciones directas de costos. Más defendibles. Fórmula: volumen × reducción × costo unitario.
*   **Nuevos ingresos**: Ingresos adicionales. Requieren más evidencia. Fórmula: volumen incremental × precio × margen.

**Pérdidas evitadas, productividad y riesgo**
*   Pérdidas evitadas: churn evitado, fraude evitado.
*   Productividad: solo es beneficio financiero si se captura como menor costo o mayor capacidad.
*   Riesgo reducido: cambio en valor esperado.
*   Cuidado: doble conteo.

**Matriz de beneficios financieros**
| Campo | Pregunta que debe responder |
| :--- | :--- |
| Beneficio | ¿Qué valor genera el proyecto? |
| Tipo | ¿Ahorro, ingreso, pérdida evitada, productividad o riesgo? |
| Métrica impactada | ¿Qué KPI cambia? |
| Línea base | ¿Cuál es la situación actual? |
| Cambio esperado | ¿Cuánto mejora? |
| Fórmula | ¿Cómo se calcula en dinero? |
| Fuente | ¿De dónde sale la evidencia? |
| Riesgo | ¿Hay doble conteo o baja atribución? |

**Ejemplo aplicado: Predictor AI**
| Campo | Ejemplo |
| :--- | :--- |
| Beneficio | Churn evitado / ingreso protegido |
| Tipo | Pérdida evitada |
| Métrica | Churn mensual o anual |
| Fórmula | Usuarios retenidos × ARPU × margen |
| Fuente | CRM, facturación, cohortes, A/B test |
| Riesgo | Atribuir toda la reducción de churn al modelo o contar dos veces LTV/CAC |
Conclusión: el valor no está en predecir churn, sino en retener usuarios de forma medible y rentable.

**Taller por equipos: Proyectos Integradores**
*   Entregable: Completar una matriz con mínimo 3 beneficios financieros del proyecto.
*   Debe incluir: Tipo, fórmula, línea base, cambio esperado, fuente y verificabilidad.
*   Cuidado: Evitar doble conteo. Si no tiene fórmula, línea base y fuente de datos, todavía no es un beneficio financiero defendible.

**Conclusiones y checklist final**
1. Los datos valen cuando cambian decisiones que mueven dinero.
2. Todo beneficio debe tener fórmula, línea base, driver económico y fuente de verificación.
3. Los ahorros verificables suelen ser más defendibles.
4. Los nuevos ingresos pueden ser grandes, pero requieren evidencia más fuerte.
5. No toda productividad es ahorro.
6. Cuidado con el doble conteo.

---

# Archivo 5: Sesión 04 - Anatomía de Costos de IA y Deuda Técnica

**UTEC Posgrado | Una escuela para Early Adopters**
**MAESTRÍA EN CIENCIA DE DATOS & IA**
**EVALUACIÓN FINANCIERA DE PROYECTOS**
**Sesión 04: Anatomía de Costos de IA y Deuda Técnica**

**Temario:**
1. Costos de Entrenamiento e Inferencia
2. Costos de Datos y HITL
3. Costo financiero de la Deuda Técnica

**Agenda**
1. Puente con la sesión anterior: de Cloud Economics a AI Economics.
2. Anatomía de costos de IA: entrenamiento vs. inferencia.
3. Costos de datos y human-in-the-loop.
4. Hidden Technical Debt in ML Systems: lectura financiera.
5. Ejercicio aplicado: SupportAI y costo total de propiedad.

**De la Sesión 3 a la Sesión 4**
*   La pregunta cambia de “¿cuánto cuesta desplegar?” a “¿cuánto cuesta operar, mantener y escalar?”
*   Objetivo: evitar subestimaciones comunes en proyectos de IA.

**Idea central**
*   En IA, el modelo no es el producto.
*   El producto real incluye datos, pipelines, entrenamiento, inferencia, monitoreo, revisión humana, gobernanza y reentrenamiento.
*   El costo visible suele ser menor que el costo total de propiedad.

**Regla de oro**
Si no puedes explicar el costo por predicción, no puedes defender el margen del producto de IA.

**Mapa financiero del ciclo de vida IA**
1. Datos: adquisición, limpieza, etiquetado.
2. Entrenamiento: experimentos, tuning, validación y retraining.
3. Inferencia: costo por consulta, usuario.
4. Operación: monitoreo, alertas, soporte.
5. Human-in-the-loop: revisiones, excepciones.
6. Deuda técnica: complejidad acumulada, menor velocidad y mayor OPEX.

**1. Anatomía de costos de IA: cómputo**
Entrenamiento vs. inferencia
*   **Entrenamiento**: Antes del despliegue, episódico. Drivers: tamaño del modelo, datos.
*   **Inferencia**: Recurrente y escala con el uso. Drivers: volumen, latencia, tokens.

**Costo mensual de inferencia**
Costo Inferencia = # predicciones × costo por predicción.
*   La inferencia es un costo variable y puede superar al entrenamiento si escala.

**Costo de LLMs**
Costo = tokens input × precio input + tokens output × precio output.

**Preguntas financieras sobre cómputo**
*   ¿Cuál es el costo marginal por usuario?
*   ¿Hay caching, batching o modelos más pequeños?

**2. Costos de datos y Human-in-the-Loop**
Los datos no son gratis. Cuestan adquirir, limpiar, etiquetar, auditar y mantener.
Categorías de costos de datos: Adquisición, Ingesta, Limpieza, Etiquetado, Versionamiento y gobernanza.

**Human-in-the-loop**
Muchos productos de IA no eliminan trabajo humano: lo desplazan hacia revisión y control de calidad.
Costo HITL = casos revisados × minutos por caso × costo hora.
*   Impacto financiero: Reduce riesgo operativo, pero aumenta OPEX. El costo de excepción puede destruir la escalabilidad.

**3. Deuda técnica oculta en sistemas ML**
*   Paper: "Hidden Technical Debt in ML Systems". Sostiene que ML genera altos costos de mantenimiento; el código del modelo es una parte pequeña.
*   Lectura financiera: La deuda técnica de ML funciona como deuda financiera: acelera hoy, pero genera intereses en OPEX, riesgo e incidentes.

**Conceptos técnicos traducidos a finanzas**
*   Entanglement / CACE (Changing Anything Changes Everything) -> Cambiar una variable obliga a retestar todo = Mayor costo de mantenimiento.
*   Data dependencies y feedback loops -> Degradación silenciosa = Riesgo financiero.
*   Glue code, pipeline jungles y configuración -> Mayor OPEX de ingeniería, incidentes y retrasos.

**Costo financiero de la deuda técnica**
Costo deuda técnica = OPEX incremental + incidentes + retrasos + costo de oportunidad + compliance.
*   Se manifiesta como margen menor y roadmaps más lentos.

**4. Ejercicio aplicado: SupportAI**
*   Caso: Asistente de IA para atención al cliente.
*   Tu tarea: estimar el costo total de propiedad (Cómputo, Datos, HITL, Deuda técnica, Resultado financiero).
*   Sensibilidades clave: Volumen de tickets, Tokens promedio, Costo por 1K tokens, % de casos escalados, Frecuencia de retraining.

**Checklist financiero para proyectos IA**
*   ¿Cuánto cuesta entrenar y reentrenar?
*   ¿Cuánto cuesta inferir por usuario?
*   ¿Qué datos necesitamos y cuánto cuesta mantenerlos?
*   ¿Cuánto trabajo humano queda en el loop?
*   ¿Dónde se está acumulando deuda técnica?

**Cierre**
El business case de IA no termina cuando el modelo funciona. Empieza cuando el modelo entra en producción.

---

# Archivo 6: Sesión 03 - Economía Cloud y Monetización

**UTEC Posgrado | Una escuela para Early Adopters**
**MAESTRÍA EN CIENCIA DE DATOS & IA**
**EVALUACIÓN FINANCIERA DE PROYECTOS**
**Sesión 03: Economía Cloud y Monetización**

**Temario:**
1. **Cloud Economics**: Elementos Básicos
2. **Unit Economics**: LTV, CAC, rentabilidad por cliente
3. **Revisión de Casos**: Una mirada a Snowflake y a Datadog
4. **Explicación Taller 1**: Take-home para empezar a aplicar en proyectos

**37signals y el "Plan de Escape" de la Nube**
Problema: En 2022, la empresa pagaba $3.2 millones de dólares a AWS y Google Cloud.
Decisión: Salida total de la nube hacia un modelo On-Premise. Inversión: $800,000.
Resultado: Ahorro neto total de $10 millones de dólares en un plazo de 5 años.

**Bloque 1: Cloud Economics**
CapEx vs. OpEx y Decisiones de Infraestructura.
La decisión básica: Comprar vs. Alquilar (Analogía: comprar un auto vs usar Uber)
| | COMPRAR AUTO | UBER |
| :--- | :--- | :--- |
| Inversión inicial | $30,000 hoy | $0 |
| Costo por uso | Bajo (gasolina) | $7 por viaje |

**On-premise vs Cloud: Comparación**
| DIMENSIÓN | ON-PREMISE (Comprar) | CLOUD (Alquilar) |
| :--- | :--- | :--- |
| Inversión inicial | Alta ($500k+) | Baja ($0) |
| Costo mensual | Bajo ($10k fijos) | Variable ($5k-50k) |
| Flexibilidad | Baja (comprometida) | Alta (escalar) |
| Control | Total | Limitado |

**¿Cuándo usar cada uno?**
USAR ON-PREMISE SI: Workload predecible y masivo.
USAR CLOUD SI: Startup/proyecto nuevo, Workload variable, Velocidad > costo.

**El mito: Cloud es OpEx puro**
Realidad desde 2019 (NIIF 16): Si firmas contrato cloud plurianual, los contadores LO TRATAN como activo.

**Ahorro promedio cloud: 30-40%**
(NO 70% como prometen vendors).
Error 1: Lift-and-Shift sin optimizar. Migrar a cloud sin cambiar arquitectura = desperdiciar dinero.

**Bloque 2: Unit Economics**
LTV, CAC y Rentabilidad por Cliente.
Unit Economics responde a LA pregunta: ¿Este producto gana dinero por cliente, o pierde?
LECCIÓN: Los mejores modelos de ML no salvan economics malos.

**Métrica 1: CAC (Customer Adquisition Cost)**
Cuánto gastas en marketing y ventas para conseguir UN cliente nuevo.
CAC = Gasto Total en Marketing y Ventas / # Clientes Nuevos.

**Métrica 2: LTV (Lifetime Value)**
Cuánto dinero ganas de UN cliente durante todo el tiempo que permanece.
LTV = (ARPU x Margen) / Churn Mensual.

**Métrica 3: Ratio LTV/CAC**
Por cada $1 que gasto adquiriendo cliente, ¿cuánto recupero?
| Ratio | Interpretación | Acción |
| :--- | :--- | :--- |
| < 1.0 | CRISIS | Pivotear o cerrar |
| 1.0 - 3.0 | SUPERVIVENCIA | Optimizar antes crecer |
| 3.0 - 5.0 | HEALTHY | Acelerar crecimiento |
| > 5.0 | EXCELENTE | Validar underinvesting |

**EJERCICIO: Calculemos Unit Economics**
CASO: CodeAI (competidor GitHub Copilot). Pricing $19/mes, Clientes 340, COGS $7/dev/mes, Gasto Mkt $1.36M, Churn 4%/mes.

**Examinemos dos casos**
| Métrica | Snowflake | Datadog | Ganador |
| :--- | :--- | :--- | :--- |
| Gross Margin | 69% | 81% | Datadog |
| LTV/CAC | 6.9x | 10.7x | Datadog |
| Payback | 35 meses | 22 meses | Datadog |
| ARPU | $379k | $400k | Similar |
| NRR | 127% | 120% | Snowflake |
| S&M % | 42% | 35% | Datadog |

**Bloque 3: Explicación del Taller 1 (evaluable)**
Evaluación Migración Cloud & Unit Economics (20% nota del curso).

**Contexto del caso: TechRetail SA**
Empresa E-commerce. Ingresos $45M. Infraestructura 100% on-premise.
DILEMA: CFO propone migrar a Azure. CTO propone renovar servidores. CEO pregunta cuál es mejor.
Parte 1: Análisis Migración Cloud (60%). Parte 2: Unit Economics de Producto (40%).

**Formato de Entrega**
Archivos: Excel, PDF Análisis, PPTX (5 slides).
Tips: Hacer Excel con fórmulas, Insights propios. Evitar copiar, Excel desorganizado.

---

# Archivo 7: Sesión 02 - Métricas de Valoración Financiera

**UTEC Posgrado | Una escuela para Early Adopters**
**MAESTRÍA EN CIENCIA DE DATOS & IA**
**EVALUACIÓN FINANCIERA DE PROYECTOS**
**Sesión 02: Métricas de Valoración Financiera**

**Temario:**
1. Valor del Dinero (Elementos Básicos)
2. Métricas Clave (VAN, TIR, Payback, Índice de Rentabilidad)
3. Taller Guiado en Excel
4. Socialización de Resultados

**Problema: JPMorgan Chase con índices de transacciones fraudulentas no aceptables.**
Solución: Implementaron algoritmos de Machine Learning en tiempo real.
Valor Financiero Generado: Reducción de Pérdidas, Mejora en la Experiencia del Cliente, Eficiencia Operativa.

**Debate: ¿Por qué los Data Scientists necesitan saber finanzas?**
Justificar inversiones en proyectos de IA/ML, Comunicar ROI a stakeholders, Priorizar proyectos, Entender lenguaje de negocios, Defender presupuestos.

**Valor del Dinero en el Tiempo**
Concepto fundamental: $1 hoy NO es igual a $1 mañana.
Razones: Inflación, Costo de oportunidad, Riesgo e incertidumbre.
Formula básica: VF = VP x (1 + r)^n

**Pregunta: ¿Tu preferencia?**
Opcion A: Recibir $10,000 hoy vs Opcion B: Recibir $12,000 en 2 años. Tasa descuento = 8% anual.

**VPN - Valor Presente Neto (aka VAN)**
Definición: Valor actual de todos los flujos futuros. Formula: VPN = Sum [FCt / (1+r)^t] - Inversión Inicial.
Regla de decisión:
*   VPN > 0 : Proyecto crea valor, ACEPTAR
*   VPN < 0 : Proyecto destruye valor, RECHAZAR
En Excel: =VNA(tasa; flujos) - inversión_inicial

**TIR - Tasa Interna de Retorno (IRR)**
Definición: Tasa que hace VPN = 0.
Regla de decisión: TIR > Tasa de descuento: ACEPTAR.
En Excel: =TIR(flujos completos incluida inversión)
Limitación: Puede dar múltiples soluciones.

**Periodo de Recuperación (Payback)**
Definición: Tiempo para recuperar la inversión inicial.
Tipos: Payback simple y Payback descontado.
Ventajas: Simple e intuitivo, mide liquidez.
Desventajas: Ignora flujos post-recuperación, no mide rentabilidad total.

**Indice de Rentabilidad (IR o PI)**
Definición: Relación beneficio-costo. IR = VP(Flujos Futuros) / Inversión Inicial.
Regla de decisión: IR > 1 : Proyecto rentable.

**Comparación de Métricas**
*   VPN: Mejor métrica absoluta de valor creado.
*   TIR: Rentabilidad porcentual.
*   Payback: Mide riesgo y liquidez.
*   IR: Eficiencia por dólar invertido.
Recomendación: Usar VPN como principal.

**CASO PRÁCTICO: Build vs Buy**
Tu empresa necesita una solución de Machine Learning para optimización de inventarios. Opción A (BUILD) vs Opción B (BUY). Evaluar cuál alternativa es mejor usando VPN, TIR, Payback e IR.

**Errores Comunes a Evitar**
1. Olvidar descontar flujos futuros
2. No incluir todos los costos
3. Ser demasiado optimista con beneficios
4. Ignorar el costo de oportunidad
5. No considerar riesgos
6. Usar TIR como unica metrica
7. No actualizar el modelo con datos reales

**Consideraciones Especiales en IA/ML**
*   Costos específicos: Infraestructura, Datos, Talento, Mantenimiento.
*   Beneficios típicos: Automatización, Mejora en precisión, Nuevas fuentes de ingreso.

**Conclusiones Clave**
Valor del Dinero -> VPN, TIR, Payback, IR -> Sensibilidad. Ya podemos empezar a evaluar proyectos.

---

# Archivo 8: Sesión 01 - El valor de los proyectos

**UTEC Posgrado | Una escuela para Early Adopters**
**MAESTRÍA EN CIENCIA DE DATOS & IA**
**EVALUACIÓN FINANCIERA DE PROYECTOS**
**Sesión 01: El valor de los proyectos**
**Docente:** Javier Arturo Benavides Gonzales

**Normas de Netiqueta**
*   CÁMARA ENCENDIDA: Genera cercanía.
*   MICRÓFONO EN SILENCIO: Actívalo solo al intervenir.
*   ENFOQUE TOTAL: Sin distracciones.
*   ACTITUD PROFESIONAL: Lenguaje claro.
*   PARTICIPA CON RESPETO.

**Logro de la sesión**
Al finalizar la sesión, el estudiante será capaz de:
*   Identificar los conceptos financieros clave (VPN, TIR, ROI) aplicados a proyectos de Data & IA.
*   Analizar casos reales de proyectos tech que fallaron por falta de ROI.
*   Reflexionar sobre el valor del dinero en el tiempo.

**Propósito**
El 87% de los proyectos de Data Science nunca llegan a producción. No fallan por falta de ACCURACY. Fallan por falta de ROI.

**1. CONCEPTOS FINANCIEROS CLAVE**
*   RIESGO vs. RETORNO: Si tu proyecto es innovador, finanzas exige un retorno mayor.
*   COSTO DE OPORTUNIDAD: Tienes que ganar esa pelea financieramente.

**HOJA DE RUTA DEL CURSO**
*   UNIDAD I (S1-S3): Fundamentos (VPN, TIR, ROI | CAPEX vs OPEX).
*   UNIDAD II (S4-S6): Costos Cloud & Deuda Técnica. Monetización.
*   UNIDAD III (S7-S9): Simulación Monte Carlo. Storytelling Financiero.
*   TALLER 1 (30%).
*   AVANCE (30%) + FINAL (40%).

**Análisis: Tu Reto vs. El Reto del Negocio**
| CASO REAL | EL SUEÑO TÉCNICO (Lo que tú ves) | LA PESADILLA FINANCIERA (Lo que ve el CFO) |
| :--- | :--- | :--- |
| **META (Metaverso)** | VR Inmersiva + Hardware de punta. Innovación total. | Pérdida: -$46 Billones. CAPEX infinito sin ingresos a la vista. |
| **ZILLOW (iBuying)** | Algoritmo preciso. Predicción automática de precios. | Pérdida: -$500 Millones. Riesgo de Mercado > Precisión del Modelo. |
| **AMAZON (Alexa)** | NLP Perfecto. Latencia mínima, UX increíble. | Pérdida: -$10 Billones/año. No hay monetización directa (Unit Economics negativos). |

**CONCLUSIONES**
*   La técnica sola no basta: hay que demostrar supervivencia financiera.
*   Riesgo y Rentabilidad van unidos siempre.
*   El dinero puede ser reinvertido.

**Para la Próxima Sesión (Virtual):**
*   Ten Excel o Google Sheets listo.
*   Tarea Mental (Capstone): ¿Tu proyecto genera DINERO (Ventas) o ahorra DINERO (Eficiencia)?

---

# Archivo 9: Capstone Project - Cronograma 2026

**UTEC Posgrado | Una escuela para Early Adopters**
**CAPSTONE PROJECT II: GUÍA ACADÉMICA PARA ESTUDIANTES**
**CRONOGRAMA 2026**

**Agenda del curso**
Lo que cubriremos en este deck:
*   Estructura general y pesos de evaluación
*   Evaluación Continua (EC) — 25 %
*   Pitch Final (P1) — 25 %
*   MVP (P2) — 30 %: viabilidad técnica, financiera y comercial
*   Informe Final (P3) — 20 %: estructura I, II y III
*   Actas de reunión, reglas clave (Turnitin, IA, plazos)
*   Recomendaciones prácticas para llegar bien al jurado

**Resumen del cronograma**
*   Asesorías: hasta 12, distribuidas en 3 periodos
*   Sesiones presenciales: 5 encuentros entre mayo y agosto
*   Entregables: Informe del Trabajo Final y Producto Mínimo Viable (MVP)
*   Informe de Trabajo Final: sábado 1 de agosto de 2026
*   MVP: viernes 14 de agosto de 2026
*   Exposición final: sábado 15 de agosto de 2026
*   La ruta crítica está marcada por la aprobación del MVP por parte del asesor antes de la entrega del 14 de agosto.

**Distribución de asesorías**
*   Periodo 1: 24 mayo — 12 junio (Hasta 4 asesorías)
*   Periodo 2: 14 junio — 10 julio (Hasta 4 asesorías)
*   Periodo 3: 12 julio — 7 agosto (Hasta 4 asesorías)
*   Total máximo: 12 asesorías. Cada asesoría se realiza entre el equipo del Data Product y el asesor.

**Sesiones programadas**
| Nº | Fecha | Horario |
| :--- | :--- | :--- |
| 1 | sábado, 16 de mayo de 2026 | 15:00 – 19:00 |
| 2 | sábado, 23 de mayo de 2026 | 12:30 – 14:30 |
| 3 | sábado, 13 de junio de 2026 | 08:00 – 11:00 |
| 4 | sábado, 11 de julio de 2026 | 08:00 – 11:00 |
| 5 | sábado, 8 de agosto de 2026 | 08:00 – 11:00 |
| 6 | sábado, 15 de agosto de 2026 | Exposición final |

**Entregables del Capstone**
1. **Informe del Trabajo Final**: Documento completo del proyecto: marco, metodología, resultados y conclusiones. Entrega vía Canvas: sábado 1 de agosto de 2026, 11:59 pm.
2. **Producto Mínimo Viable (MVP)**: Entrega de código, dataset y otros componentes funcionales. Entrega vía Canvas: viernes 14 de agosto de 2026, 11:59 pm.

**Recomendaciones para el equipo**
1. Reservar asesorías con antelación: coordinar fechas al inicio de cada periodo.
2. Aprovechar las sesiones presenciales: aclarar dudas y validar avances.
3. Trabajo paralelo Informe + MVP: ambos deben madurar simultáneamente.
4. Cierre del MVP antes del 25 de julio: dejar margen para la aprobación del asesor.
5. Ensayo previo a la exposición: programar un dry-run entre el 1 y el 15 de agosto.

**Sistema de evaluación — cuatro componentes**
*   EC (25 %): Evaluación Continua (Asesor • 12 sesiones)
*   P1 (25 %): Pitch Final (Presentación al jurado)
*   P2 (30 %): MVP (Asesor 60 % • Jurado 40 %)
*   P3 (20 %): Informe Final (Asesor 60 % • Jurado 40 %)

**Evaluación Continua (EC) — 25%**
*   Acta de reunión al final de cada sesión (4 secciones obligatorias: Temas tratados, Acuerdos, Avances validados, Recomendaciones).
*   El acta es la evidencia para tu nota EC. Se entrega el mismo día.

**Pitch Final (P1) — 25%**
*   Presentación oral al jurado en la última sesión.
*   Objetivo: que el jurado comprenda el valor del MVP.
*   Debe quedar claro: Problema de negocio, Propuesta de valor, Demostración del MVP funcionando, KPIs, Plan de captura de valor.

**MVP (P2) — 30%**
*   Iterar hasta encontrar tres viabilidades: TÉCNICA, FINANCIERA, COMERCIAL.
*   Viabilidad Técnica: KPIs apropiados, baselines, pipeline.
*   Viabilidad Financiera: CAPEX vs OPEX, Trade-off precisión vs costo, Business case (ROI, payback).
*   Viabilidad Comercial: Segmento objetivo, Insights de pilotos, KPIs de negocio (adopción, retención), Plan go-to-market.

**Informe Final (P3) — 20%**
Tres bloques: Técnico, Financiero, Comercial.
*   I. Técnico: Arquitectura, desempeño, reporte y código reproducible.
*   II. Financiero: Costos y Validación, Evaluación de desempeño económico, Reporte ejecutivo de ROI.
*   III. Comercial: Segmento, KPIs de negocio, Pitch de valor y roadmap.

**Reglas clave del Informe Final**
*   Plazo: Debe presentarse 2 semanas antes para que llegue al jurado a tiempo.
*   Turnitin: El informe pasa por Turnitin antes de la evaluación.
*   Uso de IA: Se valida el uso de IA en la redacción y desarrollo.

**Recomendaciones prácticas**
*   Trata cada sesión con el asesor como una iteración real.
*   Sube el acta el mismo día.
*   Compara con baselines: el jurado no premia modelos sin contexto.
*   Escribe el informe en paralelo al MVP, no al final.
*   Construyamos un AI Product que el jurado quiera comprar.

---
