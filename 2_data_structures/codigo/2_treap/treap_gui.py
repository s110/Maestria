import tkinter as tk
from tkinter import simpledialog, messagebox
import random
import time
import math

# --- Clase Nodo del Treap ---
class Node:
    """Representa un nodo en el Treap."""
    def __init__(self, key, priority=None, parent=None):
        self.key = key
        # Asigna prioridad aleatoria si no se proporciona
        self.priority = priority if priority is not None else random.random()
        self.parent = parent
        self.left = None
        self.right = None
        # Atributos para visualización
        self.x = 0
        self.y = 0
        self.canvas_id = None
        self.text_id = None
        self.line_id = None
        self.color = "lightblue" # Color por defecto

    def __str__(self):
        # Representación corta para el texto del nodo
        return f"K:{self.key}\nP:{self.priority:.2f}"

# --- Clase Treap ---
class Treap:
    """Implementa la estructura de datos Treap."""
    def __init__(self, visualizer):
        self.root = None
        self.visualizer = visualizer # Referencia al objeto GUI para dibujar

    def _rotate_left(self, node):
        """Realiza una rotación izquierda en el nodo dado."""
        self.visualizer.log(f"Rotación Izquierda en nodo K:{node.key}")
        parent = node.parent
        right_child = node.right
        if right_child is None: return # No se puede rotar

        # Actualizar hijo derecho de node
        node.right = right_child.left
        if right_child.left:
            right_child.left.parent = node

        # Actualizar padre de right_child
        right_child.parent = parent
        if not parent:
            self.root = right_child
        elif node == parent.left:
            parent.left = right_child
        else:
            parent.right = right_child

        # Actualizar enlace entre node y right_child
        right_child.left = node
        node.parent = right_child
        self.visualizer.redraw_step_delay() # Mostrar estado tras rotación

    def _rotate_right(self, node):
        """Realiza una rotación derecha en el nodo dado."""
        self.visualizer.log(f"Rotación Derecha en nodo K:{node.key}")
        parent = node.parent
        left_child = node.left
        if left_child is None: return # No se puede rotar

        # Actualizar hijo izquierdo de node
        node.left = left_child.right
        if left_child.right:
            left_child.right.parent = node

        # Actualizar padre de left_child
        left_child.parent = parent
        if not parent:
            self.root = left_child
        elif node == parent.right:
            parent.right = left_child
        else:
            parent.left = left_child

        # Actualizar enlace entre node y left_child
        left_child.right = node
        node.parent = left_child
        self.visualizer.redraw_step_delay() # Mostrar estado tras rotación

    def insert(self, key):
        """Inserta una clave en el Treap con visualización paso a paso."""
        if self.search(key, visualize=False):
             self.visualizer.log(f"Clave {key} ya existe. No se inserta.")
             messagebox.showwarning("Inserción", f"La clave {key} ya existe en el Treap.")
             self.visualizer.reset_highlights()
             self.visualizer.redraw_tree()
             return

        self.visualizer.log(f"Iniciando inserción de K:{key}")
        self.visualizer.reset_highlights()

        if not self.root:
            self.root = Node(key)
            self.visualizer.log(f"Árbol vacío. K:{key} es la nueva raíz.")
            self.visualizer.highlight_node(self.root, "lightgreen")
            self.visualizer.redraw_tree()
            return

        # Fase 1: Inserción tipo BST
        current = self.root
        parent = None
        path_nodes = []
        while current:
            parent = current
            path_nodes.append(current)
            self.visualizer.highlight_node(current, "yellow")
            self.visualizer.redraw_step_delay(0.5) # Pausa corta para ver el camino
            if key < current.key:
                self.visualizer.log(f"K:{key} < K:{current.key}. Mover a la izquierda.")
                current = current.left
            else:
                self.visualizer.log(f"K:{key} > K:{current.key}. Mover a la derecha.")
                current = current.right

        new_node = Node(key, parent=parent)
        if key < parent.key:
            parent.left = new_node
            self.visualizer.log(f"Insertar K:{key} como hijo izquierdo de K:{parent.key}")
        else:
            parent.right = new_node
            self.visualizer.log(f"Insertar K:{key} como hijo derecho de K:{parent.key}")

        self.visualizer.highlight_node(new_node, "lightgreen")
        self.visualizer.redraw_step_delay()

        # Fase 2: Restaurar propiedad del Heap (rotaciones hacia arriba)
        self.visualizer.log("Verificando propiedad del Heap...")
        current = new_node
        while current.parent and current.priority > current.parent.priority:
            self.visualizer.highlight_node(current, "orange")
            self.visualizer.highlight_node(current.parent, "orange")
            self.visualizer.log(f"Violación Heap: P:{current.priority:.2f} (K:{current.key}) > P:{current.parent.priority:.2f} (K:{current.parent.key})")
            self.visualizer.redraw_step_delay()

            if current == current.parent.left:
                self._rotate_right(current.parent)
            else:
                self._rotate_left(current.parent)
            # 'current' sigue siendo el nodo insertado después de la rotación
            self.visualizer.highlight_node(current, "lightgreen") # Mantener resaltado el nodo insertado
            if current.left: self.visualizer.highlight_node(current.left, "lightblue")
            if current.right: self.visualizer.highlight_node(current.right, "lightblue")


        self.visualizer.log(f"Inserción de K:{key} completada.")
        self.visualizer.reset_highlights()
        self.visualizer.redraw_tree()

    def search(self, key, visualize=True):
        """Busca una clave en el Treap con visualización."""
        if visualize:
            self.visualizer.log(f"Iniciando búsqueda de K:{key}")
            self.visualizer.reset_highlights()

        current = self.root
        path_nodes = []
        while current:
            path_nodes.append(current)
            if visualize:
                self.visualizer.highlight_node(current, "yellow")
                self.visualizer.redraw_step_delay(0.5)

            if key == current.key:
                if visualize:
                    self.visualizer.highlight_node(current, "lightgreen")
                    self.visualizer.log(f"Clave K:{key} encontrada.")
                    self.visualizer.redraw_step_delay(1)
                    # No resetear aquí para que se vea el resultado
                return current
            elif key < current.key:
                if visualize: self.visualizer.log(f"K:{key} < K:{current.key}. Mover a la izquierda.")
                current = current.left
            else:
                if visualize: self.visualizer.log(f"K:{key} > K:{current.key}. Mover a la derecha.")
                current = current.right

        if visualize:
            self.visualizer.log(f"Clave K:{key} no encontrada.")
            messagebox.showinfo("Búsqueda", f"La clave {key} no se encontró en el Treap.")
            self.visualizer.reset_highlights() # Limpiar resaltados si no se encontró
            self.visualizer.redraw_tree()
        return None

    def delete(self, key):
        """Elimina una clave del Treap con visualización paso a paso."""
        self.visualizer.log(f"Iniciando eliminación de K:{key}")
        self.visualizer.reset_highlights()

        node_to_delete = self.search(key, visualize=True) # Usa la búsqueda visual

        if not node_to_delete:
            # El search ya muestra mensaje y limpia
            return

        self.visualizer.highlight_node(node_to_delete, "red") # Marcar para eliminar
        self.visualizer.log(f"Nodo K:{key} encontrado. Preparando para eliminar.")
        self.visualizer.redraw_step_delay()

        # Fase 1: Bajar el nodo usando rotaciones hasta que sea una hoja
        while node_to_delete.left or node_to_delete.right:
            self.visualizer.log(f"Nodo K:{key} no es hoja. Rotando hacia abajo.")
            self.visualizer.highlight_node(node_to_delete, "red") # Mantener rojo

            # Elegir hijo con mayor prioridad para rotar
            if node_to_delete.left and (not node_to_delete.right or node_to_delete.left.priority > node_to_delete.right.priority):
                # Rotar con hijo izquierdo (Rotación Derecha en el padre)
                self.visualizer.highlight_node(node_to_delete.left, "orange")
                self.visualizer.log(f"Rotar con hijo izquierdo (K:{node_to_delete.left.key}, P:{node_to_delete.left.priority:.2f})")
                self.visualizer.redraw_step_delay()
                self._rotate_right(node_to_delete)
            elif node_to_delete.right:
                # Rotar con hijo derecho (Rotación Izquierda en el padre)
                self.visualizer.highlight_node(node_to_delete.right, "orange")
                self.visualizer.log(f"Rotar con hijo derecho (K:{node_to_delete.right.key}, P:{node_to_delete.right.priority:.2f})")
                self.visualizer.redraw_step_delay()
                self._rotate_left(node_to_delete)
            else:
                 # Esto no debería pasar si la lógica while es correcta, pero por si acaso
                 break

            # 'node_to_delete' ahora está más abajo. Su padre cambió.
            # Necesitamos seguir trabajando con el mismo nodo lógico (el que tiene la clave 'key')
            # Después de la rotación, node_to_delete es ahora hijo del nodo que subió.
            # No necesitamos rebuscarlo, las referencias se mantienen.
            self.visualizer.highlight_node(node_to_delete, "red") # Re-resaltar en rojo
            if node_to_delete.parent: self.visualizer.highlight_node(node_to_delete.parent, "lightblue") # Limpiar padre
            if node_to_delete.left: self.visualizer.highlight_node(node_to_delete.left, "lightblue")
            if node_to_delete.right: self.visualizer.highlight_node(node_to_delete.right, "lightblue")
            self.visualizer.redraw_step_delay()


        # Fase 2: Eliminar el nodo (ahora es una hoja)
        self.visualizer.log(f"Nodo K:{key} es ahora una hoja. Eliminando...")
        self.visualizer.highlight_node(node_to_delete, "darkred") # Indicar eliminación final
        self.visualizer.redraw_step_delay()

        parent = node_to_delete.parent
        if not parent:
            self.root = None # Era la raíz y única hoja
        elif node_to_delete == parent.left:
            parent.left = None
        else:
            parent.right = None

        # Liberar nodo (opcional en Python, el GC lo hará)
        node_to_delete.parent = None

        self.visualizer.log(f"Eliminación de K:{key} completada.")
        self.visualizer.reset_highlights()
        self.visualizer.redraw_tree()


# --- Clase Visualizer (GUI) ---
class TreapVisualizer:
    def __init__(self, master):
        self.master = master
        self.master.title("Visualizador de Treap")
        self.master.geometry("1000x750")

        self.treap = Treap(self)

        # Frame para controles
        control_frame = tk.Frame(master, pady=10)
        control_frame.pack(side=tk.TOP, fill=tk.X)

        # --- Controles ---
        tk.Label(control_frame, text="Clave:").pack(side=tk.LEFT, padx=5)
        self.key_entry = tk.Entry(control_frame, width=10)
        self.key_entry.pack(side=tk.LEFT, padx=5)
        self.key_entry.bind("<Return>", self.insert_node) # Enter para insertar

        insert_button = tk.Button(control_frame, text="Insertar", command=self.insert_node)
        insert_button.pack(side=tk.LEFT, padx=5)

        delete_button = tk.Button(control_frame, text="Eliminar", command=self.delete_node)
        delete_button.pack(side=tk.LEFT, padx=5)

        search_button = tk.Button(control_frame, text="Buscar", command=self.search_node)
        search_button.pack(side=tk.LEFT, padx=5)

        # --- Canvas para dibujar ---
        self.canvas = tk.Canvas(master, bg="white", width=980, height=600)
        self.canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=5)

        # --- Log / Status Bar ---
        self.log_text = tk.StringVar()
        log_label = tk.Label(master, textvariable=self.log_text, relief=tk.SUNKEN, anchor=tk.W)
        log_label.pack(side=tk.BOTTOM, fill=tk.X)
        self.log("Visualizador de Treap iniciado.")

        # --- Constantes de dibujo ---
        self.node_radius = 25
        self.level_height = 80
        self.h_spacing = 40 # Espaciado horizontal mínimo

        self.highlighted_nodes = {} # Para rastrear nodos resaltados

    def log(self, message):
        """Muestra un mensaje en la barra de estado."""
        print(message) # También imprime en consola para depuración
        self.log_text.set(message)

    def get_key_input(self):
        """Obtiene y valida la clave de la entrada."""
        try:
            key = int(self.key_entry.get())
            return key
        except ValueError:
            messagebox.showerror("Error", "La clave debe ser un número entero.")
            return None

    def insert_node(self, event=None): # event=None para que funcione con botón y Enter
        """Maneja el evento de inserción."""
        key = self.get_key_input()
        if key is not None:
            self.treap.insert(key)
            self.key_entry.delete(0, tk.END) # Limpiar entrada

    def delete_node(self):
        """Maneja el evento de eliminación."""
        key = self.get_key_input()
        if key is not None:
            self.treap.delete(key)
            self.key_entry.delete(0, tk.END)

    def search_node(self):
        """Maneja el evento de búsqueda."""
        key = self.get_key_input()
        if key is not None:
            self.treap.search(key, visualize=True)
            # No limpiar entrada para referencia
            # No limpiar resaltado aquí, se hace en la próxima acción o si no se encuentra

    def highlight_node(self, node, color):
        """Cambia el color de un nodo en el canvas."""
        if node and node.canvas_id:
            self.canvas.itemconfig(node.canvas_id, fill=color)
            node.color = color # Actualizar color base del nodo si es necesario
            self.highlighted_nodes[node] = color # Registrar resaltado

    def reset_highlights(self):
        """Devuelve todos los nodos a su color base."""
        for node, _ in self.highlighted_nodes.items():
             if node and node.canvas_id:
                 self.canvas.itemconfig(node.canvas_id, fill="lightblue") # Color base
                 node.color = "lightblue"
        self.highlighted_nodes.clear()


    def redraw_step_delay(self, delay=0.8):
         """Redibuja el árbol y espera."""
         self.redraw_tree()
         self.master.update() # Forzar actualización de la GUI
         time.sleep(delay) # Pausa para visualización (bloquea la GUI)

    def redraw_tree(self):
        """Limpia el canvas y redibuja el árbol completo."""
        self.canvas.delete("all")
        if not self.treap.root:
            self.log("Árbol vacío.")
            return

        # Calcular posiciones antes de dibujar
        self._calculate_positions(self.treap.root, 0, self.canvas.winfo_width())
        # Dibujar recursivamente
        self._draw_node_recursive(self.treap.root)

    def _calculate_positions(self, node, level, available_width):
        """Calcula las coordenadas X, Y para cada nodo (pre-order)."""
        if not node:
            return

        node.y = self.level_height // 2 + level * self.level_height

        # Asignación simple de X basada en el nivel y un factor de dispersión
        # Esto es básico y puede causar solapamientos
        center_x = available_width / 2

        # Intentar un cálculo de X más distribuido (aún simple)
        # Calcula el ancho necesario para los subárboles (muy simplificado)
        left_width = self._get_subtree_width(node.left) * self.h_spacing
        right_width = self._get_subtree_width(node.right) * self.h_spacing

        total_needed = left_width + right_width + self.h_spacing
        scale_factor = min(1.0, available_width / total_needed if total_needed > 0 else 1.0)

        left_width *= scale_factor
        right_width *= scale_factor

        if node.parent:
             if node == node.parent.left:
                 node.x = node.parent.x - max(self.h_spacing * scale_factor, right_width + self.h_spacing / 2 * scale_factor)
             else: # node == node.parent.right
                 node.x = node.parent.x + max(self.h_spacing * scale_factor, left_width + self.h_spacing / 2 * scale_factor)
        else: # root
             node.x = center_x


        # Ajustar si se sale de los límites (simple)
        node.x = max(self.node_radius, min(self.canvas.winfo_width() - self.node_radius, node.x))


        # Calcular para hijos recursivamente, pasando el ancho disponible ajustado
        if node.left:
             # El ancho disponible para la izquierda es desde el borde izquierdo hasta justo antes del nodo padre
             left_available = node.x - self.node_radius
             self._calculate_positions(node.left, level + 1, left_available)
        if node.right:
             # El ancho disponible para la derecha es desde justo después del nodo padre hasta el borde derecho
             right_available = self.canvas.winfo_width() - (node.x + self.node_radius)
             self._calculate_positions(node.right, level + 1, right_available)


    def _get_subtree_width(self, node):
         """Estima el 'ancho' de un subárbol (número de nodos). Muy simple."""
         if not node:
             return 0
         # Podría ser más sofisticado (ej. max(depth_left, depth_right) o contar nodos)
         # Contar nodos es una aproximación simple
         count = 1 + self._get_subtree_width(node.left) + self._get_subtree_width(node.right)
         return count


    def _draw_node_recursive(self, node):
        """Dibuja un nodo y sus conexiones recursivamente."""
        if not node:
            return

        # Coordenadas para el óvalo
        x1 = node.x - self.node_radius
        y1 = node.y - self.node_radius
        x2 = node.x + self.node_radius
        y2 = node.y + self.node_radius

        # Dibujar línea al padre (si no es la raíz)
        if node.parent:
            node.line_id = self.canvas.create_line(
                node.parent.x, node.parent.y + self.node_radius, # Salir de abajo del padre
                node.x, node.y - self.node_radius, # Entrar por arriba del hijo
                fill="black", width=1.5
            )

        # Dibujar el nodo (óvalo)
        current_color = self.highlighted_nodes.get(node, node.color) # Usar color resaltado si existe
        node.canvas_id = self.canvas.create_oval(x1, y1, x2, y2, fill=current_color, outline="black", width=2)

        # Dibujar el texto (clave y prioridad)
        node.text_id = self.canvas.create_text(node.x, node.y, text=str(node), font=("Arial", 9))

        # Dibujar hijos recursivamente
        self._draw_node_recursive(node.left)
        self._draw_node_recursive(node.right)


# --- Ejecución Principal ---
if __name__ == "__main__":
    root = tk.Tk()
    app = TreapVisualizer(root)
    # Dibujar el estado inicial (árbol vacío)
    app.redraw_tree()
    root.mainloop()
