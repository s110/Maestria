class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

def tieneCaminoSuma(raiz: TreeNode | None, sumaObjetivo: int) -> bool:
    """
    Determina si existe un camino raíz-hoja en el árbol binario
    cuya suma de nodos sea igual a sumaObjetivo.

    Args:
        raiz: El nodo raíz del árbol binario. Puede ser None si el árbol está vacío.
        sumaObjetivo: El entero objetivo para la suma del camino.

    Returns:
        True si existe dicho camino, False en caso contrario.
    """
    # Si el árbol está vacío, no puede haber un camino.
    if not raiz:
        return False

    # Verifica si el nodo actual es una hoja
    es_hoja = not raiz.left and not raiz.right

    # Si es una hoja, comprueba si su valor completa la suma objetivo
    if es_hoja:
        return raiz.val == sumaObjetivo

    # Si no es una hoja, calcula la suma restante para los subárboles
    suma_restante = sumaObjetivo - raiz.val

    # Comprueba recursivamente en el subárbol izquierdo O en el derecho
    # Se necesita que al menos uno de los subárboles contenga un camino válido.
    encontrado_izq = False
    if raiz.left:
        encontrado_izq = tieneCaminoSuma(raiz.left, suma_restante)

    # Si ya se encontró en la izquierda, no es necesario buscar en la derecha
    if encontrado_izq:
        return True

    encontrado_der = False
    if raiz.right:
        encontrado_der = tieneCaminoSuma(raiz.right, suma_restante)

    return encontrado_der # Retorna True si se encontró en la derecha, False si no

# --- Función auxiliar para construir el árbol desde la lista de entrada ---
# Esta función interpreta la lista en formato de nivel por nivel (como LeetCode)
def construirArbol(lista):
    if not lista:
        return None

    nodos = [TreeNode(val) if val is not None else None for val in lista]
    puntero_hijo = 1
    for i, nodo_actual in enumerate(nodos):
        if nodo_actual is not None:
            # Asignar hijo izquierdo si existe en la lista
            if puntero_hijo < len(nodos):
                nodo_actual.left = nodos[puntero_hijo]
                puntero_hijo += 1
            # Asignar hijo derecho si existe en la lista
            if puntero_hijo < len(nodos):
                nodo_actual.right = nodos[puntero_hijo]
                puntero_hijo += 1
            # Optimización: si ya no hay más nodos hijos por asignar, salir
            if puntero_hijo >= len(nodos):
                break
    return nodos[0] # El primer elemento es la raíz