class NodoArbol:
    def __init__(self, valor):
        self.valor = valor
        self.izquierdo = None
        self.derecho = None

class ArbolBinario:
    def __init__(self, raiz):
        self.raiz = NodoArbol(raiz)

    def insertar_izquierdo(self, nodo, valor):
        if nodo.izquierdo is None:
            nodo.izquierdo = NodoArbol(valor)
        else:
            nuevo_nodo = NodoArbol(valor)
            nuevo_nodo.izquierdo = nodo.izquierdo
            nodo.izquierdo = nuevo_nodo

    def insertar_derecho(self, nodo, valor):
        if nodo.derecho is None:
            nodo.derecho = NodoArbol(valor)
        else:
            nuevo_nodo = NodoArbol(valor)
            nuevo_nodo.derecho = nodo.derecho
            nodo.derecho = nuevo_nodo

    def imprimir_arbol(self, nodo, nivel=0):
        if nodo:
            self.imprimir_arbol(nodo.derecho, nivel + 1)
            print(' ' * 4 * nivel + '->', nodo.valor)
            self.imprimir_arbol(nodo.izquierdo, nivel + 1)