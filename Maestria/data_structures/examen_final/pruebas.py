# Representación del grafo (juguetes conectados)
# A está conectado con B y C
# B está conectado con A y D
# etc.
graph = {
    'A': ['B', 'C'],
    'B': ['A', 'D', 'E'],
    'C': ['A', 'F'],
    'D': ['B'],
    'E': ['B', 'F'],
    'F': ['C', 'E']
}

# --- BFS ---
import collections # Necesitamos esto para la "fila" (deque)

def bfs(graph, start_node):
    """Realiza una Búsqueda en Anchura (BFS)"""
    visited = set() # Para guardar los juguetes que ya vimos
    queue = collections.deque([start_node]) # La fila, empezamos con el juguete inicial
    visited.add(start_node)
    result_order = [] # Para guardar el orden en que visitamos los juguetes

    print(f"Iniciando BFS desde: {start_node}")

    while queue: # Mientras haya juguetes en la fila...
        current_node = queue.popleft() # Sacamos el primer juguete de la fila
        print(f" Visitando: {current_node}")
        result_order.append(current_node)

        # Miramos todos los vecinos del juguete actual
        for neighbor in graph.get(current_node, []):
            if neighbor not in visited: # Si es un vecino nuevo...
                print(f"  Encontrado vecino no visitado: {neighbor}. Añadiendo a la fila.")
                visited.add(neighbor) # Lo marcamos como visto
                queue.append(neighbor) # Lo añadimos al final de la fila

    print("BFS terminado.")
    return result_order

# --- DFS ---
def dfs(graph, start_node):
    """Realiza una Búsqueda en Profundidad (DFS) usando recursión"""
    visited = set() # Para guardar los juguetes que ya vimos
    result_order = [] # Para guardar el orden en que visitamos los juguetes

    print(f"Iniciando DFS desde: {start_node}")

    # Función auxiliar recursiva (la que hace la magia de ir profundo)
    def dfs_recursive(node):
        print(f" Visitando: {node}")
        visited.add(node) # Marcamos el juguete actual como visto
        result_order.append(node)

        # Miramos todos los vecinos del juguete actual
        for neighbor in graph.get(node, []):
            if neighbor not in visited: # Si es un vecino nuevo...
                print(f"  Yendo más profundo hacia: {neighbor}")
                dfs_recursive(neighbor) # ¡Llamamos a la función de nuevo para ir más profundo!
            # else:
                # print(f"  Vecino {neighbor} ya visitado.")
        print(f" Regresando desde: {node}") # Ocurre cuando ya no hay más vecinos por visitar desde aquí

    dfs_recursive(start_node) # Empezamos la exploración profunda
    print("DFS terminado.")
    return result_order

# --- Probando las funciones ---
print("--- Ejecutando BFS ---")
bfs_result = bfs(graph, 'A')
print("Orden BFS:", bfs_result) # Salida esperada: ['A', 'B', 'C', 'D', 'E', 'F'] (o similar, E y D podrían intercambiarse)

print("\n--- Ejecutando DFS ---")
dfs_result = dfs(graph, 'A')
print("Orden DFS:", dfs_result) # Salida esperada: ['A', 'B', 'D', 'E', 'F', 'C'] (o similar, depende del orden de vecinos)
