import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.optimize import curve_fit

# --- 1. CARGA DE DATOS ---
# Rutas a tus archivos (Verifica que sean correctas)
file_1nodo = (
    r"6_proyecto_final/data/exp2/resultados_heat_1nodo_[1 2 4 8 16 32]tasks.csv"
)
df_1nodo = pd.read_csv(file_1nodo)
df_1nodo["Config"] = "1 Nodo (Intra-comm)"

file_2nodo = r"6_proyecto_final/data/exp2/resultados_heat_2nodo_[2 4 8 16 32]tasks.csv"
df_2nodo = pd.read_csv(file_2nodo)
df_2nodo["Config"] = "2 Nodos (Inter-comm)"

df = pd.concat([df_1nodo, df_2nodo], ignore_index=True)

# --- 2. CÁLCULO DE MÉTRICAS (SOLUCIÓN ITERATIVA ROBUSTA) ---
FLOPS_PER_CELL_ITER = 10
results = []  # Lista para acumular los resultados

# En lugar de .apply(), iteramos manualmente. Esto NUNCA falla.
# Agrupamos por Config y N
for (config, n_val), group in df.groupby(["Config", "N"]):
    # Trabajamos con una copia para no afectar el original
    group = group.copy()

    # Buscamos el tiempo base (Secuencial 1 Nodo) para ESTE n_val específico
    base_row = df_1nodo[(df_1nodo["N"] == n_val) & (df_1nodo["Procesos"] == 1)]

    if not base_row.empty:
        t_seq = base_row["WallTime"].values[0]
        group["Speedup"] = t_seq / group["WallTime"]
        group["Eficiencia"] = group["Speedup"] / group["Procesos"]
    else:
        group["Speedup"] = np.nan
        group["Eficiencia"] = np.nan

    # Cálculo de GFLOPS
    total_ops = (n_val**2) * group["Iter_Reales"] * FLOPS_PER_CELL_ITER
    group["GFLOPS"] = total_ops / group["WallTime"] / 1e9

    # Aseguramos que las columnas N y Config existan explícitamente
    group["N"] = n_val
    group["Config"] = config

    results.append(group)

# Reconstruimos el DataFrame final uniendo los pedazos
df_processed = pd.concat(results, ignore_index=True)

# --- 3. DEFINICIÓN DEL MODELO Y AJUSTE ---


def theoretical_time(P, c1, c2, c3):
    # T(P) = Computo + Comunicacion + Latencia
    return c1 * (1 / P) + c2 * (1 / np.sqrt(P)) + c3 * np.log2(P)


# Seleccionamos el N más grande disponible
N_target = max(df_processed["N"].unique())
print(f"--- Usando coeficientes MANUALES para N={N_target} ---")

# Coeficientes manuales
manual_coeffs_1n = [384, 0, 3.4]
manual_coeffs_2n = [350, 7, 0.2]

# --- 4. GRAFICACIÓN ---
plt.style.use("seaborn-v0_8-whitegrid")
fig_time, ax_time = plt.subplots(figsize=(7, 6))
fig_speed, ax_speed = plt.subplots(figsize=(7, 6))
fig_eff, ax_eff = plt.subplots(figsize=(7, 6))

# Mapa de colores consistente
colors = plt.cm.tab10.colors
N_vals = sorted(df_processed["N"].unique())
color_map = {N: colors[i % len(colors)] for i, N in enumerate(N_vals)}

for N_val in N_vals:
    color = color_map[N_val]

    # Filtramos datos del DataFrame procesado
    d1 = df_processed[
        (df_processed["Config"] == "1 Nodo (Intra-comm)") & (df_processed["N"] == N_val)
    ]
    d2 = df_processed[
        (df_processed["Config"] == "2 Nodos (Inter-comm)")
        & (df_processed["N"] == N_val)
    ]

    # 1. Plot Tiempo
    ax_time.plot(
        d1["Procesos"], d1["WallTime"], "o-", color=color, label=f"1N N={N_val}"
    )
    if not d2.empty:
        ax_time.plot(
            d2["Procesos"], d2["WallTime"], "x--", color=color, label=f"2N N={N_val}"
        )

    # 2. Plot Speedup
    ax_speed.plot(
        d1["Procesos"], d1["Speedup"], "o-", color=color, label=f"1N N={N_val}"
    )
    if not d2.empty:
        ax_speed.plot(
            d2["Procesos"], d2["Speedup"], "x--", color=color, label=f"2N N={N_val}"
        )

    # 3. Plot Eficiencia
    ax_eff.plot(
        d1["Procesos"], d1["Eficiencia"], "o-", color=color, label=f"1N N={N_val}"
    )
    if not d2.empty:
        ax_eff.plot(
            d2["Procesos"], d2["Eficiencia"], "x--", color=color, label=f"2N N={N_val}"
        )

# --- PLOT CURVAS TEÓRICAS (Solo para el N_target) ---
x_theory = np.linspace(1, 32, 50)

# Recuperamos el tiempo base secuencial para graficar las curvas relativas correctamente
base_row_target = df_1nodo[(df_1nodo["N"] == N_target) & (df_1nodo["Procesos"] == 1)]

if not base_row_target.empty:
    base_seq_time = base_row_target["WallTime"].values[0]

    # Teoría 1 Nodo (MANUAL)
    y_time_1n = theoretical_time(x_theory, *manual_coeffs_1n)
    y_speed_1n = base_seq_time / y_time_1n
    ax_time.plot(
        x_theory, y_time_1n, "k-", alpha=0.5, linewidth=1, label="Modelo 1-Nodo"
    )
    ax_speed.plot(x_theory, y_speed_1n, "k-", alpha=0.5, linewidth=1)

    # Teoría 2 Nodos (MANUAL)
    y_time_2n = theoretical_time(x_theory, *manual_coeffs_2n)
    y_speed_2n = base_seq_time / y_time_2n
    ax_time.plot(
        x_theory, y_time_2n, "r:", alpha=0.8, linewidth=2, label="Modelo 2-Nodos"
    )
    ax_speed.plot(x_theory, y_speed_2n, "r:", alpha=0.8, linewidth=2)

# --- DECORACIÓN Y GUARDADO INDIVIDUAL ---

# 1. Tiempo
ax_time.set_yscale("log")
ax_time.set_title(f"Wall time (Modelos ajustados a N={N_target})")
ax_time.legend(
    fontsize="x-small",
    ncol=2,
    frameon=True,
    facecolor="white",
    framealpha=1,
)
ax_time.set_ylabel("Tiempo (s)")
ax_time.set_xlabel("Procesos (P)")
fig_time.tight_layout()
fig_time.savefig("6_proyecto_final/plot_walltime.png", dpi=300)

# 2. Speedup
ax_speed.plot([1, 32], [1, 32], "k--", alpha=0.3, label="Ideal Lineal")
ax_speed.set_title("Speedup")
ax_speed.set_xlabel("Procesos (P)")
ax_speed.legend(
    fontsize="x-small",
    ncol=2,
    loc="upper left",
    frameon=True,
    facecolor="white",
    framealpha=1,
)
fig_speed.tight_layout()
fig_speed.savefig("6_proyecto_final/plot_speedup.png", dpi=300)

# 3. Eficiencia
ax_eff.set_title("Eficiencia")
ax_eff.set_ylim(0, 1.3)
ax_eff.set_xlabel("Procesos (P)")
ax_eff.legend(
    fontsize="x-small",
    ncol=2,
    loc="lower left",
    frameon=True,
    facecolor="white",
    framealpha=1,
)
fig_eff.tight_layout()
fig_eff.savefig("6_proyecto_final/plot_efficiency.png", dpi=300)

# plt.show()

print("\n--- ¡Éxito! Gráficas generadas correctamente. ---")
