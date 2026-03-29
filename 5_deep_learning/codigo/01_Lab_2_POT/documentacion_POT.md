# POT: Prototypical Optimal Transport para WSSS

## Documentacion Tecnica del Script `pot_cityscapes_colab.py`

**Paper de referencia:** Wang et al., *"POT: Prototypical Optimal Transport for Weakly Supervised Semantic Segmentation"*, CVPR 2025.

**Datasets soportados:** MS COCO 2017 (80 clases), Cityscapes (19 clases), Mapillary Vistas v2 (124 clases).

---

## Tabla de Contenidos

1. [Vision General del Algoritmo](#1-vision-general-del-algoritmo)
2. [Estructura del Codigo](#2-estructura-del-codigo)
3. [Seccion 0 — Argumentos CLI](#3-seccion-0--argumentos-cli)
4. [Seccion 1 — Constantes e Hiperparametros](#4-seccion-1--constantes-e-hiperparametros)
5. [Seccion 2 — Datasets](#5-seccion-2--datasets)
6. [Seccion 3 — Arquitectura del Modelo](#6-seccion-3--arquitectura-del-modelo)
7. [Seccion 4 — Pipeline POT (Etapas I, II, III)](#7-seccion-4--pipeline-pot-etapas-i-ii-iii)
8. [Seccion 5 — Entrenamiento y Evaluacion](#8-seccion-5--entrenamiento-y-evaluacion)
9. [Seccion 6 — Ablation Study](#9-seccion-6--ablation-study)
10. [Seccion 7 — Experimento Individual](#10-seccion-7--experimento-individual)
11. [Seccion 8 — Main: Grid Search + Ablation](#11-seccion-8--main-grid-search--ablation)
12. [Script SLURM](#12-script-slurm)
13. [Analisis Comparativo por Dataset](#13-analisis-comparativo-por-dataset)
14. [Limitaciones y Diferencias con el Paper](#14-limitaciones-y-diferencias-con-el-paper)

---

## 1. Vision General del Algoritmo

### Que es WSSS?

**Weakly Supervised Semantic Segmentation (WSSS)** busca entrenar un modelo de segmentacion semantica usando unicamente **etiquetas a nivel de imagen** (que clases estan presentes), sin necesidad de mascaras de segmentacion pixel a pixel durante el entrenamiento. Esto reduce drasticamente el costo de anotacion.

### Que es POT?

POT aborda la limitacion principal de los metodos WSSS basados en prototipos: **un solo prototipo por clase no captura la variabilidad intra-clase** (e.g., caras vs. piernas de la clase "persona"). POT resuelve esto con tres etapas:

```
Imagen
  |
  v
[Encoder ResNet50] --> Feature maps F1, F2, F3, F4
  |
  v
[Clasificador + CAM] --> CAMs del clasificador (M^cls)
  |
  v
[ETAPA I: Feature Partitioning]
  |  Clustering K-Means de features confidentes por clase
  |  Genera K prototipos de cluster por clase
  v
[ETAPA II: Feature Allocation]
  |  Optimal Transport (Sinkhorn) con restriccion
  |  similarity-aware para asignar features a clusters
  v
[ETAPA III: Feature Activation]
  |  Regenera prototipos con features asignadas
  |  Calcula CAMs prototipicas por cluster
  |  Combina clusters con pesos del transport plan
  v
CAMs prototipicas (M^p*) --> Segmentacion
```

### Funcion de Perdida (Eq. 15)

```
L_total = L_cls + lambda * L_otcon
```

- **L_cls** (Eq. 16): Multi-label soft margin loss para clasificacion a nivel de imagen.
- **L_otcon** (Eq. 12): Perdida de consistencia OT que fuerza la coherencia entre las CAMs prototipicas (M^p*) y las CAMs del clasificador (M^cls), ponderada pixel a pixel segun la certeza del transport plan.
- **lambda = 3.0** (THETA): Factor de peso para L_otcon.

---

## 2. Estructura del Codigo

| Seccion | Lineas | Descripcion |
|---------|--------|-------------|
| 0 | 38-54 | Argumentos de linea de comandos |
| 1 | 57-118 | Constantes, hiperparametros y mapeos de clases |
| 2 | 120-304 | Clases Dataset (Cityscapes, COCO, Mapillary) |
| 3 | 307-362 | Arquitectura del modelo (Encoder + Clasificador + CAM) |
| 4 | 365-583 | Pipeline POT: Partitioning, Allocation, Activation, Losses |
| 5 | 586-708 | Funciones de entrenamiento y evaluacion |
| 6 | 711-792 | Estudio de ablacion |
| 7 | 795-940 | Funcion de experimento individual (grid search unit) |
| 8 | 943-1100 | Main: orquestador de grid search y ablation |

---

## 3. Seccion 0 — Argumentos CLI

**Funcion:** `parse_args()` (lineas 38-54)

Define los parametros de ejecucion del script:

| Argumento | Default | Descripcion |
|-----------|---------|-------------|
| `--dataset` | (requerido) | `cityscapes`, `coco`, o `mapillary_vistas_v2` |
| `--base-dir` | `.` | Directorio raiz donde estan las carpetas de datos |
| `--output-dir` | `./results` | Directorio de salida para resultados |
| `--epochs` | 6 | Epocas de entrenamiento por experimento |
| `--batch-size` | 4 | Tamano del batch |
| `--num-workers` | 8 | Workers del DataLoader |

**Ejemplo de uso:**
```bash
python pot_cityscapes_colab.py --dataset coco --base-dir . --epochs 6
```

---

## 4. Seccion 1 — Constantes e Hiperparametros

### Semilla de Reproducibilidad (lineas 61-65)

```python
SEED = 42
```

Se fija la semilla para `random`, `numpy`, `torch` y `torch.cuda` para garantizar resultados reproducibles.

### Hiperparametros del Paper (lineas 67-75)

Todos provienen de la Seccion 4.1 del paper:

| Constante | Valor | Paper Ref. | Descripcion |
|-----------|-------|------------|-------------|
| `K_CLUSTERS` | 3 | Sec. 4.1 | Numero de clusters K-Means por clase |
| `CAM_THRESHOLD` (tau) | 0.7 | Sec. 3.1 | Umbral para considerar un feature como "confidencial" |
| `THETA` (lambda) | 3.0 | Eq. 15 | Peso de L_otcon en la loss total |
| `LR_ENCODER` | 0.1 | Sec. 4.1 | Learning rate del encoder (ResNet50) |
| `LR_EXTRA` | 1.0 | Sec. 4.1 | Learning rate de capas adicionales (10x encoder) |
| `FEAT_DIM` | 2048 | Sec. 3 | Dimension de los feature vectors (D) |
| `SINKHORN_REG` | 0.1 | Sec. 3.2 | Regularizacion epsilon del algoritmo Sinkhorn |
| `SINKHORN_ITERS` | 100 | — | Iteraciones del algoritmo Sinkhorn |

### Mapeos de Clases (lineas 77-117)

**Cityscapes** (lineas 79-91): 19 clases con mapeo de label IDs originales (no contiguos: 7, 8, 11, ..., 33) a indices contiguos (0-18). Los IDs originales no incluidos (0-6, 9-10, etc.) se marcan como `255` (ignorar) durante la evaluacion.

**COCO** (lineas 93-117): 80 clases con category IDs no contiguos (1-90 con saltos). `COCO_CAT_ID_TO_IDX` mapea cada category ID a un indice 0-79.

**Mapillary**: No requiere mapeo — las mascaras ya usan indices 0-123 directamente.

---

## 5. Seccion 2 — Datasets

Las tres clases de Dataset heredan de `torch.utils.data.Dataset` y retornan la misma tupla `(image, img_label, mask_tensor)`:

| Retorno | Tipo | Shape | Descripcion |
|---------|------|-------|-------------|
| `image` | FloatTensor | `(3, H, W)` | Imagen RGB normalizada con ImageNet stats |
| `img_label` | FloatTensor | `(C,)` | Vector multi-hot: 1.0 si la clase esta presente |
| `mask_tensor` | LongTensor | `(H, W)` | Mascara GT con indices de clase (0..C-1), 255=ignorar |

### CityscapesWeakDataset (lineas 124-184)

**Proposito:** Cargar imagenes de Cityscapes con supervision debil.

**Estructura de archivos esperada:**
```
cityscapes/
  leftImg8bit/
    train/
      aachen/
        aachen_000000_000019_leftImg8bit.png
    val/
      ...
  gtFine/
    train/
      aachen/
        aachen_000000_000019_gtFine_labelIds.png
    val/
      ...
```

**Metodos clave:**

- **`_build_file_list()`** (lineas 137-152): Recorre las carpetas por ciudad, empareja imagenes (`_leftImg8bit.png`) con mascaras GT (`_gtFine_labelIds.png`).

- **`_label_ids_to_idx()`** (lineas 154-159): Convierte los label IDs originales de Cityscapes (7, 8, 11, ..., 33) a indices contiguos (0-18). Todos los demas pixeles se marcan como 255 (incluyendo unlabeled=0, ego vehicle=1, etc.).

- **`_get_image_label()`** (lineas 161-167): Genera el vector multi-hot `img_label` escaneando los valores unicos de la mascara convertida. Solo cuenta indices en rango `[0, 19)`.

- **`__getitem__()`** (lineas 172-184): Carga imagen + mascara, convierte IDs a indices, genera label de imagen, aplica transformaciones, redimensiona mascara con interpolacion NEAREST.

### COCOWeakDataset (lineas 187-244)

**Proposito:** Cargar imagenes de MS COCO 2017 con supervision debil.

**Estructura de archivos esperada:**
```
coco_dataset/
  annotations/
    instances_train2017.json
    instances_val2017.json
  train2017/
    000000000009.jpg
    ...
  val2017/
    ...
```

**Metodos clave:**

- **`__init__()`** (lineas 190-204): Carga las anotaciones COCO usando `pycocotools.coco.COCO`. Este paso toma ~12s para train (118K imagenes).

- **`__getitem__()`** (lineas 209-244):
  1. **Image-level label** (lineas 218-223): Itera sobre las anotaciones de la imagen y marca en el vector multi-hot las categorias presentes.
  2. **Mascara de segmentacion** (lineas 225-236): Genera mascara pixel-wise inicializada a 255 (fondo/ignorar). Pinta las mascaras de cada anotacion ordenadas por area descendente (objetos grandes primero, pequenos encima).

### MapillaryWeakDataset (lineas 247-304)

**Proposito:** Cargar imagenes de Mapillary Vistas v2.0 con supervision debil.

**Estructura de archivos esperada:**
```
mapillary_vistas_v2/
  config_v2.0.json
  training/
    images/
      *.jpg
    v2.0/
      labels/
        *.png
  validation/
    images/
      *.jpg
    v2.0/
      labels/
        *.png
```

**Metodos clave:**

- **`_build_file_list()`** (lineas 259-276): Busca imagenes en `{split}/images/` y mascaras en `{split}/v2.0/labels/`, emparejando por nombre sin extension.

- **`__getitem__()`** (lineas 289-304): Las mascaras de Mapillary v2.0 usan directamente valores de pixel 0-123 como indices de clase, por lo que no requieren conversion de IDs.

---

## 6. Seccion 3 — Arquitectura del Modelo

### HierarchicalProjection (lineas 311-328)

**Proposito:** Implementa la funcion de proyeccion lineal `L(F1, F2, F3, F4)` del paper (Eq. 2 y 8). Combina features multi-escala de las 4 capas del encoder en un unico mapa de features.

**Como funciona:**
1. Cada feature map `Fi` pasa por una convolucion 1x1 que proyecta a `out_dim=2048`.
2. Los feature maps de resoluciones diferentes (F1 tiene mayor resolucion que F4) se interpolan bilinealmente al tamano de F4.
3. Se suman los 4 mapas proyectados, seguido de BatchNorm + ReLU.

```
F1 (B,256,H1,W1)  --proj1--> (B,2048,H1,W1) --interpolate--> (B,2048,H4,W4)
F2 (B,512,H2,W2)  --proj2--> (B,2048,H2,W2) --interpolate--> (B,2048,H4,W4)
F3 (B,1024,H3,W3) --proj3--> (B,2048,H3,W3) --interpolate--> (B,2048,H4,W4)
F4 (B,2048,H4,W4) --proj4--> (B,2048,H4,W4)
                                                                    |
                                                                    v
                                                            sum --> BN --> ReLU
                                                                    |
                                                                    v
                                                           (B, 2048, H4, W4)
```

**Por que es necesario:** Las features de bajo nivel (F1, F2) contienen detalles espaciales finos (bordes, texturas), mientras que las de alto nivel (F3, F4) capturan semantica abstracta. La combinacion permite prototipos mas completos que representan tanto la forma como la semantica del objeto.

### POTEncoder (lineas 331-362)

**Proposito:** Modelo completo que integra encoder, clasificador y generacion de CAMs.

**Componentes:**

| Componente | Tipo | Parametros |
|------------|------|------------|
| `layer0` | Sequential(conv1, bn1, relu, maxpool) | Stem de ResNet50 |
| `layer1-4` | ResNet50 layers | Bloques residuales |
| `hier_proj` | HierarchicalProjection | Proyeccion multi-escala |
| `classifier` | Linear(2048, C, bias=False) | Clasificador de imagen |

**Forward pass** (lineas 347-362):

```python
def forward(self, x):
    # 1. Extraer features multi-escala del encoder
    f1 = layer1(layer0(x))   # (B, 256,  H/4,  W/4)
    f2 = layer2(f1)          # (B, 512,  H/8,  W/8)
    f3 = layer3(f2)          # (B, 1024, H/16, W/16)
    f4 = layer4(f3)          # (B, 2048, H/32, W/32)

    # 2. Proyeccion jerarquica
    feats = hier_proj(f1, f2, f3, f4)  # (B, 2048, H/32, W/32)

    # 3. Clasificacion (GAP + Linear)
    gap    = AdaptiveAvgPool2d(feats)   # (B, 2048)
    logits = classifier(gap)           # (B, C)

    # 4. Generacion de CAMs (Eq. 1)
    W = classifier.weight              # (C, 2048)
    cam_fg = ReLU(W^T * feats)         # (B, C, H, W) - CAMs foreground
    cam_fg = cam_fg / cam_fg.max()     # Normalizar a [0, 1]
    cam_bg = 1 - max(cam_fg)           # (B, 1, H, W) - CAM background
    cam_cls = cat([cam_bg, cam_fg])    # (B, C+1, H, W)

    return logits, cam_cls, feats, (f1, f2, f3, f4)
```

**Generacion de CAMs del clasificador (Eq. 1):**

La CAM de foreground para la clase `c` se calcula como:
```
CAM_fg[c] = ReLU(theta_c^T * F4)
```
Donde `theta_c` es la fila `c` de la matriz de pesos del clasificador. Esto funciona porque las neuronas del clasificador "miran" las mismas features espaciales, y los pesos indican que regiones del feature map son importantes para cada clase.

La CAM de background se define como el complemento:
```
CAM_bg = 1 - max_c(CAM_fg[c])
```
Regiones donde ninguna clase foreground tiene alta activacion se consideran fondo.

---

## 7. Seccion 4 — Pipeline POT (Etapas I, II, III)

### Funcion Auxiliar: mask_average_pool (lineas 369-373)

**Proposito:** Calcula el prototipo (vector representativo) promediando features solo donde la mascara es 1. Implementa `MAP(Mask * L(...))` del paper (Eq. 2).

```python
def mask_average_pool(features, mask):
    # features: (D, HW) - feature vectors de todos los pixeles
    # mask: (HW,) - mascara binaria indicando que pixeles usar
    # return: (D,) - prototipo promedio
```

Si la mascara esta vacia (ningun pixel confidencial), retorna el promedio global como fallback.

---

### ETAPA I: Feature Partitioning (lineas 376-444)

**Funcion:** `feature_partitioning(feats_flat, cam_cls, img_label, K, threshold)`

**Proposito:** Divide las features confidentes de cada clase en K clusters usando K-Means. Corresponde a la Seccion 3.1 del paper.

**Entrada:**
- `feats_flat`: (D, HW) — Features aplanadas del feature map
- `cam_cls`: (C+1, HW) — CAMs del clasificador aplanadas
- `img_label`: (C,) — Etiqueta multi-hot de la imagen
- `K`: Numero de clusters (default: 3)
- `threshold` (tau): Umbral de confianza (default: 0.7)

**Salida:**
- `cluster_protos`: (J+1, K, D) — K prototipos de cluster por clase (J foreground + 1 background)
- `cls_protos`: (J+1, D) — Prototipo unico por clase (promedio de features confidentes)
- `cluster_masks`: (HW, J+1, K) — Mascara de asignacion de clustering
- `present_classes`: Lista de indices de clases presentes en la imagen

**Proceso paso a paso:**

1. **Conversion a numpy** (linea 381): `feats_flat.detach().T.cpu().numpy()` — KMeans de sklearn requiere arrays numpy. Se usa `.detach()` porque KMeans es no-diferenciable.

2. **Background** (lineas 388-411):
   - Selecciona pixeles donde `CAM_bg > tau` (confidentes de ser fondo)
   - Calcula el prototipo de clase background: promedio de features confidentes
   - Si hay >= K pixeles confidentes: ejecuta KMeans con K=3 clusters
   - Si no: todos los K clusters usan el mismo prototipo (sin diversidad)

3. **Foreground** (lineas 413-439):
   - Para cada clase `c` presente en la imagen (`img_label[c] > 0.5`):
     - Selecciona pixeles donde `CAM_fg[c] > tau`
     - Misma logica de KMeans que para background
   - `class_idx = c + 1` porque indice 0 esta reservado para background

4. **Detach final** (lineas 441-444): Los prototipos retornados se desacoplan del grafo de autograd con `.detach()`. Esto es intencional: los prototipos solo se usan para calcular asignaciones (transport plan). Los gradientes fluyen en la Etapa III cuando se recomputan prototipos desde features vivas.

**Diagrama conceptual:**
```
Para cada clase presente en la imagen:

  Features del feature map (49 pixeles si img=224)
  |
  v
  Filtrar por CAM > 0.7 (e.g., 15 pixeles confidentes)
  |
  v
  KMeans(K=3) sobre esos 15 pixeles
  |
  v
  Cluster 0: 5 pixeles --> Prototipo P_{c,0} = promedio
  Cluster 1: 7 pixeles --> Prototipo P_{c,1} = promedio
  Cluster 2: 3 pixeles --> Prototipo P_{c,2} = promedio
```

---

### Similarity-Aware Constraint (lineas 447-461)

**Funciones:** `cosine_similarity_matrix()` y `compute_similarity_aware_constraint()`

**Proposito:** Calcula la restriccion marginal x del Optimal Transport (Eq. 4-5 del paper). Esta restriccion define **cuantas features deben asignarse a cada cluster prototipo**, priorizando prototipos mas similares al prototipo de clase del clasificador.

**Calculo (Eq. 4):**
```
x_{c,k} = sim(P_{c,k}, P_c^cls)
```
Donde `sim` es similitud coseno entre el prototipo del cluster k de clase c y el prototipo CAM del clasificador para clase c.

**Normalizacion (Eq. 5):**
```
x = softmax(flatten(X))
```
Se aplana la matriz de similitudes y se normaliza con softmax para obtener una distribucion de probabilidad.

**Efecto:** Los clusters con prototipos mas similares a la representacion del clasificador reciben mas features. Esto es diferente del OT vanilla que usa restriccion uniforme `v_j = 1/N`.

---

### ETAPA II: Feature Allocation (lineas 477-488)

**Funcion:** `feature_allocation(feats_flat, cluster_protos, cls_protos, present_classes)`

**Proposito:** Usa Optimal Transport (Sinkhorn) para asignar **todas** las features (no solo las confidentes) a los cluster prototipos. Corresponde a la Seccion 3.2 del paper.

**Proceso:**

1. **Calcular matriz de similitud S** (lineas 480-483):
   - `S[i,j]` = similitud coseno entre feature `i` y prototipo `j`
   - Dimension: `(HW, N)` donde `N = |present_classes| * K`

2. **Restriccion similarity-aware** (lineas 484-485):
   - Calcula `x` usando `compute_similarity_aware_constraint()`

3. **Sinkhorn OT** (linea 486):
   - Resuelve el problema de Optimal Transport con regularizacion entropica
   - Retorna el transport plan `T*` de dimension `(HW, N)`

4. **Asignacion greedy** (linea 487, Eq. 7):
   ```
   j* = argmax_j T*_{i,j}
   ```
   Cada feature se asigna al prototipo con mayor probabilidad en el transport plan.

**Nota sobre gradientes:** `feats_flat.detach()` se usa aqui porque el transport plan `T*` sirve como pesos fijos. Rastrear 100 iteraciones de Sinkhorn en autograd seria costoso e innecesario — los gradientes fluyen por la Etapa III.

### Algoritmo Sinkhorn (lineas 464-474)

**Funcion:** `sinkhorn_ot(S, x_constraint, reg, n_iter)`

**Proposito:** Resuelve el problema de Optimal Transport con regularizacion entropica (Eq. 6). Implementa el algoritmo de Sinkhorn-Knopp.

**Problema que resuelve (Eq. 6):**
```
T* = argmax_T sum_{i,j} T_{i,j} * S_{i,j}
sujeto a:
  T * 1_N = (1/M) * 1_M    (restriccion de fuente: uniforme)
  T^T * 1_M = x             (restriccion de destino: similarity-aware)
```

**Proceso:**
1. Convertir similitud a costo: `C = 1 - S` (linea 465)
2. Calcular kernel: `K = exp(-C / epsilon)` (linea 466)
3. Iteracion de Sinkhorn (lineas 471-473):
   ```
   a = u / (K @ b)
   b = v / (K^T @ a)
   ```
   Donde `u = 1/M` (uniforme) y `v = x` (similarity-aware constraint).
4. Transport plan final: `T = diag(a) * K * diag(b)` (linea 474)

---

### ETAPA III: Feature Activation (lineas 491-515)

**Funcion:** `feature_activation(feats_flat, cluster_protos, T_star, assignment, present_classes, H, W, K)`

**Proposito:** Regenera prototipos usando todas las features asignadas (no solo las confidentes) y calcula CAMs prototipicas ponderadas por el transport plan. Corresponde a la Seccion 3.3 del paper.

**Proceso en dos fases:**

**Fase 1: Regenerar prototipos (Eq. 8, lineas 496-502)**
```python
for c_idx in present_classes:
    for k in range(K):
        assign_mask = (assignment == proto_idx).float()
        updated_protos[c_idx, k] = mask_average_pool(feats_flat, assign_mask)
```
Se recalcula cada prototipo `P*_{c,k}` como el promedio de TODAS las features asignadas a ese cluster por el transport plan (no solo las confidentes). Esto es critico: usa `feats_flat` con gradientes, lo que permite que L_otcon retroalimente al encoder.

**Fase 2: CAMs prototipicas (Eq. 9-11, lineas 503-514)**
```python
for c_idx in present_classes:
    for k in range(K):
        sim_ck = cosine_similarity(feats_T, updated_protos[c_idx, k])  # Eq. 9
        cam_ck = ReLU(sim_ck)
        cam_c_weighted += T_star[:, proto_idx] * cam_ck  # Eq. 10: T* * cam
    # Eq. 11: sum over K clusters
    cam_proto_full[c_idx] = cam_c_weighted.reshape(H, W)
```

**Ecuaciones del paper:**
- **Eq. 9:** `M^p_{c,k} = ReLU(sim(P*_{c,k}, L(F1..F4)))` — CAM por cluster
- **Eq. 10:** `M^{p*}_{c,k} = T*_{c,k} . M^p_{c,k}` — Ponderacion por transport plan
- **Eq. 11:** `M^{p*}_c = sum_k M^{p*}_{c,k}` — Combinacion de K clusters

**Camino de gradientes:**
```
feats_flat (con grad)
  |
  v
mask_average_pool --> updated_protos (con grad)
  |
  v
cosine_similarity(feats_T, updated_protos) --> cam_ck (con grad)
  |
  v
T_star (sin grad, pesos fijos) * cam_ck --> cam_c_weighted (con grad)
  |
  v
cam_proto_full --> ot_consistency_loss --> backward --> encoder + hier_proj
```

---

### Funciones de Perdida

#### Binary Entropy (linea 518, Eq. 14)

```python
def binary_entropy(p, eps=1e-8):
    return -p * log(p) - (1-p) * log(1-p)
```

Mide la incertidumbre de la asignacion de un feature a una clase. Si `g(t_{i,c}) = 0.5` (maxima incertidumbre), la entropia es maxima.

#### OT Consistency Loss (lineas 523-548, Eq. 12-13)

**Funcion:** `ot_consistency_loss(cam_proto, cam_cls, T_star, img_label, present_classes, K)`

**Proposito:** Fuerza coherencia entre las CAMs prototipicas `M^{p*}` y las CAMs del clasificador `M^{cls}`. Usa pesos adaptativos por pixel segun la certeza del transport plan.

**Calculo del peso adaptativo w_{i,c} (Eq. 13):**
```
w_{i,c} = l_c * (1 - (1/log(|C|+1)) * H(g(t_{i,c})))
```
Donde:
- `l_c`: 1 si la clase c esta presente (0 si no)
- `g(t_{i,c}) = sum_k t_{i,c,k}`: Probabilidad de que el pixel i pertenezca a la clase c
- `H(.)`: Entropia binaria de esa probabilidad
- `1/log(|C|+1)`: Factor de escala

**Efecto:** Pixeles con alta certeza en el transport plan (g cerca de 0 o 1) reciben alto peso. Pixeles inciertos (g cerca de 0.5) reciben bajo peso.

**Calculo de la distancia (Eq. 12):**
```
L_otcon = (1/HW) * sum_i sum_c w_{i,c} * |M^{p*}_{i,c} - M^{cls}_{i,c}|
```
Se normaliza cada CAM por su maximo per-class (a rango [0,1]) antes de calcular la distancia L1.

#### Classification Loss (linea 551, Eq. 16)

```python
def classification_loss(logits, img_labels):
    return F.multilabel_soft_margin_loss(logits, img_labels)
```

Multi-label soft margin loss: calcula la perdida de clasificacion binaria independiente para cada clase, combinando sigmoid + BCE.

---

### Orquestador POT: pot_forward_single (lineas 555-568)

**Funcion:** `pot_forward_single(feats, cam_cls, img_label, H, W)`

**Proposito:** Ejecuta las 3 etapas de POT para una sola imagen y retorna las CAMs prototipicas junto con L_otcon.

```python
def pot_forward_single(feats, cam_cls, img_label, H, W):
    feats_flat = feats.reshape(D, -1)         # (D, HW)
    cam_flat = cam_cls.reshape(C+1, -1)       # (C+1, HW)

    # Etapa I: Feature Partitioning
    cluster_protos, cls_protos, _, present = feature_partitioning(...)

    # Etapa II: Feature Allocation
    T_star, assignment, _ = feature_allocation(...)

    # Etapa III: Feature Activation
    cam_proto_full, _ = feature_activation(...)

    # Calcular L_otcon
    loss_otcon = ot_consistency_loss(cam_proto_flat, cam_flat, T_star, ...)

    return cam_proto_full, loss_otcon
```

---

### CAM a Segmentacion (lineas 574-583)

**Funcion:** `cam_to_segmentation(cam_proto, threshold=0.3)`

**Proposito:** Convierte las CAMs prototipicas en un mapa de segmentacion discreto.

**Proceso:**
1. Normalizar cada canal (clase) por su maximo → rango [0, 1]
2. `argmax` sobre la dimension de clases → indice de la clase con mayor activacion
3. Pixeles con activacion maxima < 0.3 se asignan a background (clase 0)

**Nota:** Esta es una **simplificacion** del pipeline completo del paper, que usaria DenseCRF + IRN para generar pseudo-labels refinadas y luego entrenaria DeepLab-v2.

---

## 8. Seccion 5 — Entrenamiento y Evaluacion

### Polynomial LR Scheduler (linea 590, Sec. 4.1)

```python
def polynomial_lr(step, total_steps, power=0.9, base_lr=LR_ENCODER):
    factor = max(0.0, 1 - step / total_steps)
    return base_lr * (factor ** power)
```

Decrementa el learning rate segun una funcion polinomial con potencia 0.9, siguiendo trabajos previos en WSSS (SIPE, SFC).

### train_one_epoch (lineas 595-646)

**Proposito:** Entrena el modelo durante una epoca.

**Flujo de un batch:**

```
1. Cargar batch: (images, img_labels, _)
2. Actualizar LR:
   - LR_encoder = polynomial_lr(step)
   - LR_extra = LR_encoder * (1.0 / 0.1) = LR_encoder * 10
3. Forward pass: logits, cam_cls, feats, _ = model(images)
4. L_cls = multilabel_soft_margin_loss(logits, img_labels)
5. Para cada imagen del batch:
   - Ejecutar POT pipeline: pot_forward_single(feats[b], cam_cls[b], ...)
   - Acumular L_otcon
6. L_total = L_cls + 3.0 * L_otcon
7. Backward + clip gradients (max_norm=10) + optimizer step
```

**Learning rates duales (lineas 606-609):**
- Grupo 0 (encoder ResNet50): LR base = 0.1
- Grupo 1 (hier_proj + classifier): LR = 1.0 (10x mayor)

Esto sigue la convencion del paper: las capas adicionales necesitan aprender mas rapido que el encoder pre-entrenado.

**Manejo de excepciones (lineas 621-623):** Si `pot_forward_single` falla (e.g., KMeans sin suficientes datos), se imprime una advertencia en el primer batch y se continua con `loss_otcon_b = 0` para esa imagen.

### evaluate (lineas 649-708)

**Proposito:** Evalua el modelo en el conjunto de validacion calculando mIoU, Dice y Pixel Accuracy.

**Proceso por imagen:**
1. Forward pass del modelo (sin gradientes)
2. Ejecutar POT pipeline para obtener CAMs prototipicas
3. Interpolar CAMs al tamano de la mascara GT
4. Convertir CAMs a segmentacion con `cam_to_segmentation()`
5. `seg_fg = seg_pred - 1`: Convertir indices (0=bg, 1..C=fg) a (−1=bg, 0..C−1=fg) para alinear con los indices del GT
6. Filtrar pixeles validos: `mask_gt != 255`
7. Calcular IoU y Dice por clase

**Metricas:**

| Metrica | Formula | Descripcion |
|---------|---------|-------------|
| **mIoU** | `nanmean(IoU_c)` | Media de IoU por clase, ignorando clases ausentes |
| **Dice** | `nanmean(Dice_c)` | Media de Dice por clase |
| **PixelAcc** | `correct / total` | Fraccion de pixeles correctamente clasificados |

Donde:
```
IoU_c = TP_c / (TP_c + FP_c + FN_c)
Dice_c = 2*TP_c / (2*TP_c + FP_c + FN_c)
```

---

## 9. Seccion 6 — Ablation Study

### evaluate_ablation (lineas 715-792)

**Proposito:** Evalua el modelo bajo diferentes configuraciones del pipeline POT para estudiar la contribucion de cada componente.

**Parametros de configuracion:**

| Parametro | Descripcion |
|-----------|-------------|
| `use_multi_cluster` | Si es `True`, usa K=3 clusters. Si es `False`, usa K=1 (single-cluster). |
| `use_ot` | Si es `True`, usa Optimal Transport para asignar features. Si es `False`, asigna por similitud coseno directa al prototipo mas cercano. |
| `use_similarity_constraint` | Si es `True`, usa restriccion similarity-aware (SOT). Si es `False`, usa restriccion uniforme (OT vanilla). |

**Condiciones del estudio (Tab. 3-4 del paper):**

| Condicion | multi_cluster | use_ot | similarity | Que evalua |
|-----------|:---:|:---:|:---:|-------------|
| I — Baseline | No | No | — | CAM del clasificador sin POT |
| II — Multi-cluster, sin OT | Si | No | — | Efecto de multi-cluster sin transporte optimo |
| III — Multi-cluster + OT uniforme | Si | Si | No | OT vanilla vs. asignacion directa |
| IV — POT completo | Si | Si | Si | Framework completo con SOT + L_otcon |

**Nota:** Esta ablacion evalua diferentes pipelines de inferencia sobre el **mismo modelo entrenado** (el mejor del grid search). Una ablacion rigurosa entrenaria modelos separados por condicion.

---

## 10. Seccion 7 — Experimento Individual

### run_experiment (lineas 799-940)

**Proposito:** Ejecuta un experimento completo del grid search con una combinacion especifica de `(img_size, subset_size)`.

**Flujo:**

```
1. Crear transformaciones (train con augmentation, val sin)
2. Instanciar dataset segun --dataset
3. Crear subset si subset_size no es None
4. Crear DataLoaders (train shuffle=True, val shuffle=False)
5. Instanciar POTEncoder
6. Configurar optimizador SGD con dos grupos de parametros
7. Training loop: num_epochs iteraciones
   a. train_one_epoch() → L_cls, L_otcon, L_total
   b. evaluate() con n_samples=200 → mIoU, Dice, PixAcc
   c. Trackear best_miou
8. Evaluacion final completa (sin limite de muestras)
9. Guardar JSON con resultados, historia y hiperparametros
```

**Transformaciones de entrenamiento:**
- `Resize((img_size, img_size))`
- `RandomHorizontalFlip()` — Data augmentation
- `ColorJitter(0.3, 0.3, 0.3)` — Variacion de brillo, contraste, saturacion
- `ToTensor() + Normalize(ImageNet stats)`

**Transformaciones de validacion:**
- Solo `Resize`, `ToTensor`, `Normalize` (sin augmentation)

---

## 11. Seccion 8 — Main: Grid Search + Ablation

### main (lineas 947-1100)

**Proposito:** Orquesta todo el flujo: configuracion por dataset, grid search de hiperparametros, ablation study y reporte final.

**Grid search:**
```python
grid_img_sizes    = [224, 336, 448]
grid_subset_sizes = [500, 1000, 1500]
```
Total: 3 x 3 = **9 combinaciones** por dataset. Cada combinacion entrena un modelo desde cero.

**Proceso:**
1. Configurar dataset (num_classes, class_names, data_root)
2. Para cada `(img_size, subset_size)`:
   - Ejecutar `run_experiment()`
   - Guardar CSV parcial con resultados acumulados
   - Trackear el mejor modelo
3. Imprimir tabla resumen ordenada por mIoU descendente
4. Ejecutar ablation study sobre el mejor modelo
5. Imprimir IoU por clase del mejor modelo

**Salidas generadas:**
```
results/{dataset}/
  results_{dataset}_img{size}_subset{n}.json  # 9 archivos, uno por experimento
  grid_search_{dataset}.csv                   # Tabla comparativa
  ablation_{dataset}.json                     # Resultados del ablation study
```

---

## 12. Script SLURM

### slurm_pot.slurm

**Proposito:** Ejecutar el entrenamiento en un cluster HPC con SLURM.

**Recursos solicitados:**

| Recurso | Valor | Justificacion |
|---------|-------|---------------|
| GPUs | 1x NVIDIA A100-PCIE-40GB | Suficiente para batch_size=4 con ResNet50 |
| CPUs | 10 | 8 para DataLoader workers + 2 para KMeans/main thread |
| RAM | 64 GB | COCO annotations requieren ~12GB para cargar |
| Tiempo | 8 horas | Grid search de 9 experimentos con 6 epocas cada uno |

**Optimizaciones:**
```bash
export OMP_NUM_THREADS=1   # Evita que numpy/sklearn creen hilos internos
export MKL_NUM_THREADS=1   # que compitan con los workers del DataLoader
```

**Uso:**
```bash
sbatch slurm_pot.slurm cityscapes
sbatch slurm_pot.slurm coco
sbatch slurm_pot.slurm mapillary_vistas_v2
```

---

## 13. Analisis Comparativo por Dataset

### Por que COCO funciona y Cityscapes/Mapillary no

POT fue disenado exclusivamente para PASCAL VOC y MS COCO (Seccion 4.1 del paper). La razon fundamental es la **naturaleza de las etiquetas a nivel de imagen**:

| Factor | COCO (funciona) | Cityscapes (no funciona) | Mapillary (no funciona) |
|--------|:---:|:---:|:---:|
| Clases totales | 80 | 19 | 124 |
| Clases por imagen | 2-5 | 12-15 | 30-50 |
| Diversidad de labels | Alta (cada imagen tiene combinacion unica) | Baja (casi todas las imagenes tienen road, building, car, sky...) | Baja |
| L_cls informativa | Si: discrimina entre imagenes | No: todas las imagenes son similares | No |
| Feature map 7x7 (49 px) | ~10-15 px/clase | ~3-4 px/clase | ~1-2 px/clase |
| KMeans viable (K=3) | Si | Marginal | No (< 3 px/clase) |

### Resultados Experimentales

**COCO (mejor: img448_subset1000):**
- mIoU: **25.08%** — Razonable para WSSS simplificado con 1000 imagenes de entrenamiento
- L_otcon: Valores entre 0.08-0.27, con tendencia decreciente → aprendiendo

**Cityscapes (mejor: img448_subset1000):**
- mIoU: **2.88%** — Peor que aleatorio (~5.3%)
- L_cls se estanca en ~0.37-0.45 → el clasificador no logra discriminar entre imagenes
- Modelo colapsa: predice la misma clase dominante para todos los pixeles

**Mapillary (mejor: img224_subset500):**
- mIoU: **0.03%** — Esencialmente cero
- Con 124 clases, la clasificacion multi-label es imposible con image-level labels en escenas uniformes
- mIoU empeora con entrenamiento (0.47% → 0.01%) → colapso total del modelo

### Diagnostico Tecnico Detallado

**Problema 1: L_cls no discrimina**

En Cityscapes, el vector `img_label` de casi toda imagen es:
```
[1, 1, 1, 0, 0, 1, 0, 0, 1, 0, 1, 1, 0, 1, 0, 0, 0, 0, 0]
 road sidewalk building ...   vegetation   sky person  car
```

Todas las imagenes de conduccion tienen las mismas clases activas. L_cls recibe gradientes cercanos a cero porque `sigmoid(logit) ≈ label` para la mayoria de clases desde el inicio.

**Problema 2: Feature map insuficiente**

Con img_size=224, el feature map es 7x7=49 pixeles. Para Mapillary con 50 clases activas, cada clase tiene ~1 pixel en promedio. KMeans con K=3 requiere al menos 3 pixeles, por lo que la mayoria de clases caen al fallback (todos los clusters identicos), anulando el beneficio de multi-cluster.

**Problema 3: Desbalanceo extremo**

En datasets de conduccion, "road" puede ocupar 60-70% de los pixeles, pero en el feature map 7x7 solo tiene ~30 pixeles. Clases raras como "motorcycle" pueden tener 0 pixeles en el feature map.

---

## 14. Limitaciones y Diferencias con el Paper

### Simplificaciones de esta implementacion

| Aspecto | Paper (completo) | Esta implementacion |
|---------|-------------------|---------------------|
| Pseudo-labels | DenseCRF + IRN → mascaras refinadas | argmax directo sobre CAMs |
| Segmentador final | DeepLab-v2 entrenado sobre pseudo-labels | No implementado |
| Evaluacion | mIoU sobre set completo de val | mIoU sobre subsets parciales durante training |
| Multi-escala | Evaluacion con multi-scale + flip | Evaluacion single-scale |
| Datasets | PASCAL VOC 2012, MS COCO 2014 | COCO 2017, Cityscapes, Mapillary |
| Backbone | ResNet50 pre-trained ImageNet + SFC/CLIP-ES base | ResNet50 pre-trained ImageNet |

### Correcciones aplicadas al codigo original

| Problema | Fix | Impacto |
|----------|-----|---------|
| L_otcon no propagaba gradientes (`.detach()` en training) | Quitar detach en train_one_epoch, agregar detach selectivo en partitioning y allocation | L_otcon ahora retroalimenta encoder y hier_proj |
| Normalizacion incorrecta en L_otcon (`F.normalize(p=1, dim=0)`) | Reemplazar por normalizacion max per-class | L1 distance ahora coincide con Eq. 12 |
| `.cpu().numpy()` fallaba silenciosamente en tensores con grad | Agregar `.detach()` antes de `.cpu().numpy()` en feature_partitioning | POT pipeline ya no falla silenciosamente |
| `except Exception: pass` ocultaba errores | Agregar logging del primer error por batch | Errores ahora son visibles en logs |
| Ablation conditions II y III identicas | Agregar `use_similarity_constraint` flag, 4 condiciones distintas | Ablation ahora es informativo |
| SLURM: 2 GPUs sin DataParallel | Reducir a 1 GPU | Sin desperdicio de recursos |
| SLURM: Contention CPU por hilos internos | Agregar `OMP_NUM_THREADS=1`, `MKL_NUM_THREADS=1` | DataLoader workers y KMeans no compiten |
