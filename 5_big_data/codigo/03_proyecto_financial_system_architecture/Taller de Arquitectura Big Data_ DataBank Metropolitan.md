# **Taller de Arquitectura Big Data: DataBank Metropolitan**

## **1\. Introducción**

El sistema financiero de la región de **DataLandia** ha experimentado un crecimiento exponencial. La red bancaria metropolitana, con más de **9 millones de clientes** distribuidos en ocho distritos financieros, enfrenta desafíos de gestión de activos y servicios digitales complejos y crecientes.

### **Desafíos Actuales del Sector Bancario:**

* **Expansión Digital y Dispersión de Clientes:** El crecimiento ha llevado a una digitalización masiva. Los clientes operan desde toda la región, lo que significa que la mayoría no acude a oficinas físicas y depende exclusivamente de canales digitales para sus transacciones.  
* **Congestión de Procesamiento:** Durante los días de pago o cierres de mes, los sistemas sufren latencia, lo que provoca retrasos en la validación de transacciones y transferencias.  
* **Desajuste Demográfico y de Infraestructura:**  
  * La población de edad avanzada, que reside principalmente en zonas residenciales, a menudo tiene dificultades con las Apps móviles y prefiere atención humana.  
  * Las generaciones más jóvenes prefieren servicios 100% digitales y automatizados, pero la oferta de productos personalizados en tiempo real es limitada.  
* **Fragmentación de Entidades Financieras:** La región cuenta con doce instituciones bancarias independientes y desconectadas. Estas entidades compiten por recursos sin compartir información que ayude a prevenir fraudes o mejorar el perfilamiento de riesgo.  
* **Red de Cajeros y Oficinas Subutilizada:** DataBank posee una impresionante infraestructura física. El 89% de los clientes vive o trabaja a menos de 8 km de un punto de atención. Sin embargo, el sistema no ofrece servicios de "última milla digital", es decir, la conexión eficiente entre la necesidad financiera inmediata del usuario y la infraestructura disponible.

En 2024, se aprobó la **Iniciativa Financiera Lumina**, que unifica los servicios de estas doce agencias bajo una plataforma única conocida como **Lumina Bank**.

**Misión de Lumina Bank:** "Crear y operar un sistema financiero compartido único, eficiente, integrado y bajo demanda, aprovechando los activos combinados de las doce entidades financieras metropolitanas".

---

## **2\. Visión de Lumina Bank**

El documento de visión describe un sistema financiero dinámico que se adapta a las necesidades del cliente:

* **Banca Bajo Demanda y Sin Esfuerzo:** Mediante un dispositivo móvil, un cliente puede gestionar sus finanzas desde cualquier punto. El sistema planifica sus inversiones y pagos de manera inteligente.  
* **Optimización Financiera:** El sistema llevará al usuario a maximizar su rentabilidad de la manera más segura y rápida posible, guiándolo en cada decisión de gasto o inversión.  
* **Integración Multicanal:** El sistema integrado incluirá banca móvil, cajeros, corresponsales bancarios, asesores virtuales e incluso micro-créditos en tiempo real.  
* **Servicios Multimodales Flexibles:** Una operación puede incluir varios canales. Por ejemplo, iniciar una solicitud en la App, validarla en un cajero cercano y finalizarla con un asesor remoto.  
* **Ventaja Competitiva:** Los clientes optarán por Lumina porque será más rápido, seguro y económico que la banca tradicional.  
* **Sistema de Pago Integrado:** Un sistema de pago móvil total. Al iniciar una compra, el sistema monitorea el flujo de fondos y aplica los cargos de manera inteligente según el saldo y las metas de ahorro del usuario.

---

## **3\. Modelo de Negocio**

Lumina Bank opera como una **alianza público-privada** única, colaborando con empresas de IoT financiero, sistemas distribuidos y Big Data.

1. **RFP para el Front-End:** Apps, interfaces de cajeros, biometría y seguimiento (ya seleccionada).  
2. **RFP para el Back-End Inteligente:** Diseño de servicios de datos y aplicaciones que impulsarán el front-end y respaldarán la planificación de infraestructura financiera (objetivo de este taller).

**Consideraciones:** Tecnologías de **código abierto**. Lumina Bank es dueña de los datos; la empresa desarrolladora retiene la propiedad intelectual.

---

## **4\. Servicios de Datos y Aplicaciones de Lumina Bank**

La recopilación y el análisis de datos son fundamentales. La arquitectura debe considerar:

### **I. Decisiones en Tiempo Real**

Para autorizar transacciones y detectar fraudes de manera óptima:

* Solicitudes de transacciones activas de otros clientes.  
* Disponibilidad de fondos y límites en tiempo real.  
* Datos de geolocalización en vivo para prevenir fraudes.  
* Patrones de gasto aprendidos (históricos y predictivos).

### **II. Planes Diarios de Liquidez**

Predecir diariamente el efectivo y los recursos necesarios para el día siguiente:

* Datos de mercados financieros actualizados.  
* Eventos futuros que influyan en la demanda de efectivo (festivos, ferias).  
* Tendencias de movilidad y gasto de los usuarios.

### **III. Informes Operativos Bajo Demanda**

Métricas cruciales para evaluar el progreso:

* Tiempos promedio de aprobación.  
* Costo operativo por transacción.  
* Ingresos por producto financiero.  
* Nivel de salud financiera del sistema vs. banca tradicional.

### **IV. Mantenimiento y Planificación de Infraestructura**

* Monitoreo continuo de la salud de servidores y terminales.  
* Análisis predictivo para identificar posibles caídas del sistema.  
* Identificación de rutas de alta congestión transaccional para proponer nuevas oficinas o nodos digitales.

---

## **5\. Tarea para los Alumnos**

Como alumnos de Big Data, deben diseñar una arquitectura de datos que soporte estos servicios considerando:

1. **Fuentes de Datos:** Clasificación de datos transaccionales, sociales y de comportamiento.  
2. **Ingesta de Datos:** Mecanismos para streaming (transacciones) y batch (cierres contables).  
3. **Procesamiento:** Pipelines para decisiones en tiempo real (detección de fraude) y análisis histórico.  
4. **Almacenamiento:** Tecnologías para alta velocidad (InMemory) y gran volumen (Data Lake).  
5. **Seguridad y Gobernanza:** Medidas críticas de encriptación y privacidad de datos sensibles.  
6. **Tecnologías de Código Abierto:** Priorización de herramientas open source según el modelo de negocio.

**Entregable:** Presentación de la arquitectura con diagramas claros y justificación tecnológica detallada e implementacion