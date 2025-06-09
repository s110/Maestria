# Problema de las n-Reinas
# El problema consiste en colocar n reinas en un tablero de ajedrez de n x n de tal manera que ninguna reina pueda atacar a otra.
# No pueden haber dos reinas en la misma fila, columna o diagonal.

import random
import time

# El tablero es una lista de longitud n en donde el indice representa la columna y el valor de cada item representa la fila.
# Ejemplo: [2,1,0] significa que hay reinas en las posiciones (2,0),(1,1), y (0,2)

def fitness(tablero):
    # El fitness esta basado en buscar el numero de pares de reinas que se atacan entre si
    # El valor a retornar inicia en 0 ya que se va a evaluar el fitness con cada iteracion
    n = len(tablero)
    pares_reinas_atacan = 0

    # Contar conflictos en filas
    # Se inicia con una fila de 0s con longitud n, estas luego van a ser usadas para contar cuantas reinas hay en cada fila
    contar_filas = [0] * n
    for filas in tablero:
        contar_filas[filas] += 1
    # Las cantidades de reinas atacantes entre si se rige bajo la formula (count)(count-1)//2
    # Ejemplo: Si hay 4 reinas en una misma fila, entonces hay (4)(3)//2 = 6 pares de reinas atacandose
    pares_reinas_atacan += sum(count * (count - 1) // 2 for count in contar_filas if count > 1)

    # Contar conflictos en las diagonales
    # Si la diferencia absoluta de las filas de dos reinas es igual a la diferencia de sus indices de columna, entonces estan en la misma diagonal
    for i in range(n):
        for j in range(i + 1, n):
            if abs(tablero[i] - tablero[j]) == abs(i - j):
                pares_reinas_atacan += 1
    return pares_reinas_atacan

def vecinos(tablero):
    # Genera todos los tableros vecinos al mover una reina en una columna
    # Se inicia por un conjunto de vecinos vacio para resetear con cada iteracion
    n = len(tablero)
    vecinos= []
    for columna in range(n):
        for fila in range(n):
    #Se cambia una reina por cada fila y se añade esa como uno de los vecinos (puede ser un proceso medio costoso)
            if tablero[columna] != fila:
                nuevo_tablero = tablero[:]
                nuevo_tablero[columna] = fila
                vecinos.append(nuevo_tablero)
    return vecinos

def hill_climbing(tablero_inicial):
    # Aplica la búsqueda Hill Climbing para encontrar una solución. Se usa el fitness para evaluar la solucion
    tablero_actual = tablero_inicial
    fitness_actual = fitness(tablero_actual)
    # Un counter para mejorar la busqueda en caso de que pueda haber mejores iteraciones
    counter = 0
    while True:
    # se itera buscando mejores soluciones, caracteristica del hill climbing.
    # en este caso el valor minimo de fitness sirve para hallar el tablero correcto
        vecinos_actuales = vecinos(tablero_actual)
        tablero_siguiente = min(vecinos_actuales, key=fitness)
        fitness_siguiente = fitness(tablero_siguiente)
    # se printea el fitness evaluado luego de ver a los vecinos para visualizar las mejoras
        print(f'Fitness actual: {fitness_siguiente}')
        if fitness_siguiente >= fitness_actual:
            counter +=1
            if counter ==3:
                break  # Si no hay mejora, se detiene la búsqueda

        tablero_actual, fitness_actual = tablero_siguiente, fitness_siguiente

    return tablero_actual, fitness_actual

def print_tablero(tablero):
    # Printea el tablero de ajedrez con las reinas en sus posiciones.
    n = len(tablero)
    for fila in range(n):
        linea = ""
        for columna in range(n):
            if tablero[columna] == fila:
                linea += "R "
            else:
                linea += ". "
        print(linea)
    print()

# Generar un tablero inicial aleatorio
n = int(input("¿Cuantas reinas se van a analizar?: "))  # Cambia el valor de n para tableros de diferente tamaño
tablero_inicial = [random.randint(0, n - 1) for _ in range(n)]

# Resolver el problema
tiempo_inicial = time.time()
solucion, fitness_final = hill_climbing(tablero_inicial)
tiempo_final = time.time()

# Mostrar los resultados
print("Tablero inicial:",tablero_inicial)
print_tablero(tablero_inicial)
print("Tablero solución:",solucion)
print_tablero(solucion)
print("Fitness (pares de reinas atacándose):", fitness_final)
print("Tiempo de ejecución: {:.4f} segundos".format(tiempo_final - tiempo_inicial))