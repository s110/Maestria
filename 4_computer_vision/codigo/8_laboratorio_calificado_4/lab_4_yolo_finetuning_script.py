from ultralytics import YOLO
from pathlib import Path
import pandas as pd
import itertools

param_grid = {
    # Hiperparámetros a variar
    'freeze': [22, 10, 0],
    'optimizer': ['SGD', 'AdamW'],
    'lr0': [0.01, 0.001],
    'batch': [8, 16, 32],
}

BASE_PATH = Path("/home/sebastian.lopez/CV/02_laboratorio_4/")
OUTPUT_DIR = BASE_PATH.joinpath("runs","detect")

keys, values = zip(*param_grid.items())
combinations = [dict(zip(keys, v)) for v in itertools.product(*values)]

print(f"Total de experimentos a correr: {len(combinations)}")
print(f"Los resultados se guardarán en: {OUTPUT_DIR}")

all_results = []

for i, config in enumerate(combinations):
    run_name = f"Grid_Exp_{i}"
    print(f"\n=== Iniciando {run_name} ===")

    model = YOLO("yolov8n.pt")

    # ENTRENAMIENTO
    model.train(
        data="bccd.yaml",
        epochs=50,
        imgsz=640,
        name=run_name,
        project=OUTPUT_DIR,
        patience=10,
        device=0,
        verbose=False,
        **config
    )

    # VALIDACIÓN
    metrics = model.val(split="val", verbose=False, project=OUTPUT_DIR, name=f"{run_name}_val")

    # Extraer métricas globales
    res = {
        'Experiment': run_name,
        **config,
        'mAP50': metrics.box.map50,
        'mAP50-95': metrics.box.map,
        'Precision': metrics.box.mp,
        'Recall': metrics.box.mr
    }

    # Extraer métricas POR CLASE
    class_maps = metrics.box.maps
    for class_id, class_name in model.names.items():
        res[f"{class_name}_mAP95"] = class_maps[class_id]

    all_results.append(res)

    # Guardar CSV parcial en la ruta base
    csv_path = BASE_PATH/ "resultados_parciales_gridsearch.csv"
    pd.DataFrame(all_results).to_csv(csv_path, index=False)

# RESULTADOS FINALES
df = pd.DataFrame(all_results)
df = df.sort_values(by="mAP50-95", ascending=False)
final_csv_path = BASE_PATH / "resultados_finales_gridsearch.csv"
df.to_csv(final_csv_path, index=False)

print(f"\nProceso finalizado. CSV guardado en: {final_csv_path}")