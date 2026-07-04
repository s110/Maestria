# Taller 3 — AgroLens AI
**Evaluación Financiera de Proyectos · Maestría en Ciencia de Datos & IA (UTEC) · Sebastián López**

## El caso

**AgroLens AI**: plataforma SaaS de visión computacional para control de calidad en plantas empacadoras agroexportadoras (arándano y uva de mesa). Detecta defectos (hongos, deshidratado, calibre fuera de spec) en línea, reduciendo el rechazo de contenedores en destino. Se cobra **suscripción anual de USD 30,000 por línea de empaque** (monetización directa). Es deliberadamente distinto al capstone GeoMinder: aquí el valor viene de vender el producto, no de ahorro interno.

## Supuestos base (idénticos en los 3 entregables)

| Parámetro | Valor | Justificación |
|---|---:|---|
| CAPEX (desarrollo CV + edge devices) | $600,000 | 5 ingenieros × 10 meses + 40 kits edge de demo |
| Capital de trabajo | $60,000 | ~2 meses de costos fijos; se recupera en Año 5 |
| Líneas suscritas Año 1 | 25 | Pipeline comercial (Ica / La Libertad) |
| Precio suscripción anual | $30,000/línea | ~25% del ahorro por contenedores rechazados (>$120k/año por línea) |
| Costo variable anual | $8,000/línea | Hardware amortizado + cloud/inferencia + soporte + labeling HITL |
| Costos fijos anuales | $250,000 | 2 FTE MLOps, ventas, reentrenamiento estacional, gobernanza |
| Crecimiento neto de volumen | 15%/año | 25% bruto de nuevas líneas − 10% churn |
| WACC | 16% | rf + riesgo país + prima tecnológica |
| IR Perú | 29.5% | Régimen general |
| Depreciación / valor residual | 5 años lineal / 10% CAPEX | |

## Resultados clave

| Métrica | Valor |
|---|---:|
| VPN base (Excel Tab 1) | **$578,717** |
| TIR base | **43.5%** (≫ WACC 16%) |
| Payback descontado | 2.93 años |
| Escenarios: E(VPN) / SD / CV | $664,925 / $910,958 / **1.37 (riesgo alto)** |
| VPN pesimista / optimista | −$531,373 / +$2,033,641 |
| Montecarlo (10,000 iter, seed 42): E(VPN) | $526,138 |
| P(VPN > 0) | **96.5%** |
| **P(VPN > $1M)** | **7.3%** |
| **P10** | **+$134,694** (positivo) |
| CV Montecarlo | 0.60 |
| **Variable crítica** | **Líneas suscritas Año 1** (r = +0.63), seguida de Precio (r = +0.60) |

## Decisión: GO CONDICIONAL

P(VPN>0) de 96.5% y P10 positivo apoyan el GO; el CV de escenarios (1.37) y un pesimista de −$531k lo condicionan a: (1) ≥17 LOIs firmadas antes de liberar el CAPEX completo, (2) pilotos pagados que validen precio ≥$28k/línea, (3) contratos anuales con renovación automática que acoten el churn ≤10%.

## Archivos

- `Lopez_Taller3.xlsx` — Tab 1 Modelo FCF 5 años (VPN, TIR, payback), Tab 2 Sensibilidad 1D (precio ±20%, volumen ±30%, costo variable ±25%; fórmulas vivas equivalentes a Data Table), Tab 3 Escenarios (pesimista/base/optimista con E(VPN), SD, CV y recomendación). Todo con fórmulas, cero valores pegados.
- `Lopez_Taller3.ipynb` — Montecarlo 10,000 iteraciones (Normal/Triangular/Uniforme según criterio de la Sesión 7), histograma de VPN, tornado chart y respuestas a las 3 preguntas. Ejecutado con seed 42; corre tal cual en Google Colab.
- `Lopez_Taller3.pptx` — 1 slide ejecutivo: recomendación, métricas E(VPN)/P(VPN>0)/P10/CV y top 3 variables críticas con mitigación.

Consistencia: la celda de validación del notebook reproduce el VPN base del Excel al dólar ($578,717). El crecimiento neto del Excel (15%) equivale en el Montecarlo a crecimiento bruto Triangular(15%,25%,35%) menos churn Uniforme(5%,15%).
