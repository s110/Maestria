class Cola:
    def __init__(self):
        self.items = []  # Lista para almacenar los elementos de la cola

    def esta_vacia(self):
        """Verifica si la cola está vacía."""
        return len(self.items) == 0

    def encolar(self, item):
        """Agrega un elemento al final de la cola."""
        self.items.append(item)

    def desencolar(self):
        """Elimina y devuelve el primer elemento de la cola."""
        if self.esta_vacia():
            raise IndexError("La cola está vacía")
        return self.items.pop(0)  # Elimina el primer elemento de la lista

    def ver_frente(self):
        """Devuelve el primer elemento de la cola sin eliminarlo."""
        if self.esta_vacia():
            raise IndexError("La cola está vacía")
        return self.items[0]

    def tamaño(self):
        """Devuelve el número de elementos en la cola."""
        return len(self.items)

    def __str__(self):
        """Representación en cadena de la cola."""
        return str(self.items)