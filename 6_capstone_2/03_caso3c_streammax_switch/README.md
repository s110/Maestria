# Caso 3/C — StreamMax: Estrategia de SWITCH (Opción Real de Cambiar)
**Trabajo grupal Sesión 8 · Evaluación Financiera de Proyectos · Sebastián López**

## La estrategia analizada

Empezar con la Alt C (vendor AutoML, CAPEX $850k) para validar el approach con inversión mínima. Al final del Año 1, decidir según la reducción de churn observada: si >7pp, SWITCH a in-house (migración $2M, menor que los $2.8M de A directa por el aprendizaje del año 1, churn mejora de 26% a 22%); si 5–7pp, MANTENER la Alt C; si <5pp, ABANDONAR con pérdida acotada.

## Supuestos de las ramas (anclados al caso y al deck S8)

Éxito 65% = probabilidad de éxito de Alt C del caso, con reducción de 9pp (churn 26%, caso base). Mediocre 20% con 6pp (churn 29%, peor escenario del caso, dentro de la banda 5–7pp del deck). Falla 15% = sin señal atribuible (0pp), usando la probabilidad de demoras de C (15%) como proxy de falla dura. La migración exitosa tiene probabilidad 85% (los 75% de A mejorados por el aprendizaje, mismo razonamiento 75→85 de la Opción D del deck). Modelo financiero: FCF = (Δmargen bruto 68% + CAC evitado − campañas − OPEX) × (1−28%), usuarios comparados contra el contrafactual sin proyecto (churn 35%, crecimiento 5%), WACC 14%, 5 años, valor residual $0.

## Tarea 1 — Árbol con backward induction

| Nodo | Alternativas | Óptimo |
|---|---|---|
| Éxito (65%) | Switch $104.3M vs Mantener C $94.7M | **SWITCH** (+$9.6M) |
| Mediocre (20%) | Mantener $60.0M vs Abandonar $27.0M | **MANTENER** (6pp sigue siendo muy rentable a esta escala) |
| Falla (15%) | Abandonar −$1.2M vs Seguir pagando −$2.3M | **ABANDONAR** (pérdida acotada a CAPEX + 1 año de OPEX) |

Las decisiones óptimas coinciden exactamente con los umbrales de diseño del deck (>7pp / 5–7pp / <5pp).

## Tarea 2 — Valor de la opción de switch

VPN estrategia con opciones = 0.65×104.3 + 0.20×60.0 + 0.15×(−1.2) = **$79.6M**. VPN de C comprometida 5 años sin flexibilidad = **$73.2M**. **Valor de la flexibilidad = +$6.4M** (≈ $6.2M de la opción de switch + $0.2M de la opción de abandono). VPN expandido = VPN tradicional + flexibilidad, como en la fórmula de la sesión.

## Tarea 3 — ¿Mejor que elegir A o C desde el inicio?

Mejor que C estática, sí (+$6.4M). Pero **no mejor que A directa**: E(VPN) de A con estados 75% éxito / 15% peor escenario / 10% falla total = **$117.5M**, es decir la estrategia de switch cuesta **−$37.9M de valor esperado**. La razón: con 2.5M de usuarios y ARPU $16, cada punto de churn vale ~$3–4M al año, y el switch retrasa 2 años el churn de 22%. El costo de esperar aplasta al valor de la opción. Break-even: A tendría que tener ~38% de probabilidad de falla total para que el switch empate, muy por encima del 10–25% razonable según el caso. Lo que sí compra el switch es downside: peor caso −$1.2M vs −$4.1M de A, y solo $0.85M de CAPEX en riesgo en Año 0. Conclusión para la plenaria: no usaríamos esta estrategia como principal; refleja el mensaje de la sesión de que las opciones valen menos cuando la decisión es urgente, y aquí el churn sangra $168M/año. Si el comité no tolera el riesgo de ejecución de A, la respuesta correcta es B (85% de éxito, 11pp), no el switch.

## Tarea 4 — Información crítica del Año 1

La reducción de churn atribuible medida contra grupo de control (holdout), porque sin atribución los 7pp del umbral no son creíbles; el precision/recall del modelo del vendor por segmento de valor; la tasa real de éxito de las campañas (el 40% del caso tiene rango 28–52%); y la portabilidad de los datos etiquetados y features del vendor, porque con lock-in duro la migración costaría más de $2M y mataría la opción de switch.

## Archivos

- `Lopez_Caso3C_Switch.xlsx` — Inputs del caso (editables: cambiar WACC recalcula todo el árbol), motor FCF con los 10 caminos auditables, árbol con MAX() de backward induction y comparadores.
- `Lopez_Caso3C_Switch.pptx` — 1 slide formato plenaria: árbol visual, VPN sin/con opción, valor de flexibilidad, recomendación.

Verificación: Excel recalculado sin errores (658 fórmulas) y cuadra al dólar con el modelo Python de calibración.
