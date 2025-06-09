import matplotlib.pyplot as plt
import numpy as np

def graficar_reinas(positions):
    # Tamaño del tablero
    N = len(positions)

    # Crear el tablero de ajedrez
    fig, ax = plt.subplots(figsize=(N, N))
    ax.set_xlim(-0.5, N - 0.5)
    ax.set_ylim(-0.5, N - 0.5)
    ax.set_aspect('equal')  # Asegurar que las celdas sean cuadradas

    # Colorear las celdas del tablero
    for x in range(N):
        for y in range(N):
            color = 'white' if (x + y) % 2 == 0 else 'tab:gray'
            ax.add_patch(plt.Rectangle((x - 0.5, y - 0.5), 1, 1, color=color))

    # Ajustar el tamaño de la fuente según el tamaño del tablero
    fontsize = max(12, 24 - N // 2)  # Reducir el tamaño de la fuente a medida que N aumenta

    # Colocar las reinas en el tablero
    for x, y in positions:
        ax.text(y, x, "♛", ha="center", va="center", fontsize=fontsize, color="tab:red")

    # Configurar los ejes y el tablero
    ax.set_xticks(np.arange(N))
    ax.set_yticks(np.arange(N))
    ax.set_xticklabels([])
    ax.set_yticklabels([])
    ax.grid(False)
    plt.gca().invert_yaxis()
    plt.savefig('graficar_reinas_ejemplo_inicial.png')
    plt.show()


a=[[0, 0],
       [2,  1],
       [3, 2],
       [1, 3]]
graficar_reinas(a)