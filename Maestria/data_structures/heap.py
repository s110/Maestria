import heapq

# Min-Heap en Python
class MinHeap:
    def __init__(self):
        self.heap = []

    def insertar(self, valor):
        heapq.heappush(self.heap, valor)

    def eliminar_min(self):
        return heapq.heappop(self.heap)

    def ver_min(self):
        return self.heap[0] if self.heap else None

    def esta_vacio(self):
        return len(self.heap) == 0

# Max-Heap en Python (usando valores negativos)
class MaxHeap:
    def __init__(self):
        self.heap = []

    def insertar(self, valor):
        heapq.heappush(self.heap, -valor)

    def eliminar_max(self):
        return -heapq.heappop(self.heap)

    def ver_max(self):
        return -self.heap[0] if self.heap else None

    def esta_vacio(self):
        return len(self.heap) == 0