# Problema de las n-Reinas
# El problema consiste en colocar n reinas en un tablero de ajedrez de n x n de tal manera que ninguna reina pueda atacar a otra.
# No pueden haber dos reinas en la misma fila, columna o diagonal.

import matplotlib.pyplot as plt
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
    # Un counter para contar el numero de iteraciones
    counter = 0
    while True:
    # se itera buscando mejores soluciones, caracteristica del hill climbing.
    # en este caso el valor minimo de fitness sirve para hallar el tablero correcto
        counter +=1
        vecinos_actuales = vecinos(tablero_actual)
        tablero_siguiente = min(vecinos_actuales, key=fitness)
        fitness_siguiente = fitness(tablero_siguiente)
        if fitness_siguiente >= fitness_actual:
                break  # Si no hay mejora, se detiene la búsqueda

        tablero_actual, fitness_actual = tablero_siguiente, fitness_siguiente

    return tablero_actual, fitness_actual,counter

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

def estadisticas_hill_climbing(num_reinas, numero_soluciones):
    # Generar un tablero inicial aleatorio
    n = num_reinas
    iteraciones_list=[]
    tiempo_list=[]
    fitness_list=[]
    # Resolver el problema
    for i in range(numero_soluciones):
        tablero_inicial = [random.randint(0, n - 1) for _ in range(n)]
        tiempo_inicial = time.time()
        solucion, fitness_final,numero_iteraciones = hill_climbing(tablero_inicial)
        tiempo_final = time.time()
        tiempo_ejecucion=tiempo_final-tiempo_inicial
        iteraciones_list.append(numero_iteraciones)
        tiempo_list.append(tiempo_ejecucion)
        fitness_list.append(fitness_final)
    return iteraciones_list, tiempo_list, fitness_list

valores_n = list(range(5, 86, 10))
resultados_iteraciones=[]
resultados_tiempo=[]
resultados_fitness=[]
valores_n_str=[str(x) for x in valores_n]
for i in valores_n:
    iteraciones,tiempo,fitness_valor=estadisticas_hill_climbing(i, 20)
    resultados_iteraciones.append(iteraciones)
    resultados_tiempo.append(tiempo)
    resultados_fitness.append(fitness_valor)
    print(f'Reinas: {i}')


plt.boxplot(resultados_tiempo, tick_labels=valores_n_str)
plt.xlabel('Número de Reinas (n)')
plt.ylabel('Tiempo de ejecución (s)')
plt.title('Tiempo de ejecución de Hill Climbing para el Problema de las n-Reinas')
plt.grid()
plt.savefig('grafico_variabilidad_tiempo_hillclimbing.png')

plt.boxplot(resultados_iteraciones, tick_labels=valores_n_str)
plt.xlabel('Número de Reinas (n)')
plt.ylabel('Número de iteraciones (n)')
plt.title('Número de iteraciones de Hill Climbing para el Problema de las n-Reinas')
plt.grid()
plt.savefig('grafico_variabilidad_intentos_hillclimbing.png')

plt.boxplot(resultados_fitness, tick_labels=valores_n_str)
plt.xlabel('Número de Reinas (n)')
plt.ylabel('Fitness final (n)')
plt.title('Fitness final de Hill Climbing para el Problema de las n-Reinas')
plt.grid()
plt.savefig('grafico_variabilidad_fitness_hillclimbing.png')

with open('resultados_hill_climbing.txt', 'w') as file:
    # Escribir encabezado
    file.write("Resultados Hill Climbing\n")
    file.write("=========================\n")

    # Escribir cada valor de n junto con los resultados
    for i, n in enumerate(valores_n):
        file.write(f"\nNúmero de reinas: {n}\n")
        file.write(f"Iteraciones: {resultados_iteraciones[i]}\n")
        file.write(f"Tiempo: {resultados_tiempo[i]}\n")
        file.write(f"Fitness: {resultados_fitness[i]}\n")
        file.write("-" * 30 + "\n")

print("Los resultados han sido guardados en 'resultados_hill_climbing.txt'.")