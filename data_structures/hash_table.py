class TablaHash:
    def __init__(self, tamaño):
        self.tamaño = tamaño
        self.tabla = [[] for _ in range(tamaño)]

    def _hash(self, clave):
        return hash(clave) % self.tamaño

    def insertar(self, clave, valor):
        indice = self._hash(clave)
        for kvp in self.tabla[indice]:
            if kvp[0] == clave:
                kvp[1] = valor
                return
        self.tabla[indice].append([clave, valor])

    def obtener(self, clave):
        indice = self._hash(clave)
        for kvp in self.tabla[indice]:
            if kvp[0] == clave:
                return kvp[1]
        return None

    def eliminar(self, clave):
        indice = self._hash(clave)
        for i, kvp in enumerate(self.tabla[indice]):
            if kvp[0] == clave:
                del self.tabla[indice][i]
                return