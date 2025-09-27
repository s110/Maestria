import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import missingno as msno
import kagglehub
from kagglehub import KaggleDatasetAdapter

# Simulando la ruta de Kaggle
# Si ejecutas esto fuera de Kaggle, necesitarás descargar el archivo AmesHousing.csv
# y ajustar la ruta a donde lo hayas guardado.
file_path = 'prevek18/ames-housing-dataset'

try:
    df = pd.read_csv(file_path)
    print("Dataset cargado exitosamente.")
except FileNotFoundError:
    print(f"Error: El archivo no se encontró en {file_path}. Por favor, asegúrate de que el dataset esté disponible en la ruta especificada o ajústala.")
    print("Si estás fuera de Kaggle, descarga el dataset de: https://www.kaggle.com/datasets/prevek18/ames-housing-dataset")
    print("Y guarda 'AmesHousing.csv' en una ruta accesible.")
    # Si falla, puedes intentar cargar un dataset de ejemplo para que el resto del código no falle completamente
    df = pd.DataFrame(np.random.rand(10, 5), columns=['colA', 'colB', 'colC', 'colD', 'colE'])
    df.iloc[0, 0] = np.nan
    df.iloc[2, 1] = np.nan
    df.iloc[5, 3] = np.nan
    print("Cargado un DataFrame de ejemplo para demostración.")

print(f"Dimensiones del dataset: {df.shape}")
df.head()