
"""def generar_factorial(numero:int):
    resultado=1
    [resultado:=resultado*x for x in range(1,numero+1)]
    return resultado

def factoriales():
    a=generar_factorial(int(input("ingresa fac")))
    print(a)

def es_primo(int):
    for i in range(2,int):
        if int%i==0:
            return False
    return True

def generar_primos(int):
    counter=0
    for i in range(2,int):
        if es_primo(i)==True:
            print(f"{i} es primo")
            counter+=1
    return counter

a=generar_primos(int(input("indica tu primo: ")))
print(f"hay {a} primos")"""

# Ejercicio 1

def cifrar_texto(cadena: str, numero: int):
    # Para ello se van a separar las letras y se van a evaluar segun su indice alfabetico
    texto_cifrado=[]
    # Se sabe que ord() encuentra el valor numerico de cada letra y que las mayusculas tienen
    # diferente valor numerico que las minusculas
    for letra in cadena:
        if letra.isalpha():
            valor_letra=ord(letra)
    # Se usa un valor base para hallar donde empezar
    # Haciendo pruebas se sabe que de la A a la Z (sin contar ñ) se tienen 26 caracteres
            if letra.islower():
                valor_letra_base=ord("a")
            else:
                valor_letra_base=ord("A")
    # Se usa chr para cambiar de nuevo a letra
            letra_shifteada=chr((valor_letra+numero-valor_letra_base)%26+valor_letra_base)
    # Se suma la cadena shifteada al texto cifrado, si no era letra se appendea pero de forma normal.
            texto_cifrado.append(letra_shifteada)
        else:
            texto_cifrado.append(letra)
    return print(''.join(texto_cifrado))




# Ejercicio 2

# Función auxiliar para verificar si un número es primo.
# Retorna: true si el número es primo, false en caso contrario.
def es_primo(int):
    for i in range(2,int):
        if int%i==0:
            return False
    return True

# Función para generar una lista de números primos menores a un número dado.
def generar_primos(numero:int):
    lista_primos=[]
    for i in range(2,numero):
        if es_primo(i)==True:
            lista_primos.append(i)
    return lista_primos

# Función para encontrar y devolver los pares de números primos gemelos.
# retorna una lista de tuplas y cada tupla contiene un par de números primos gemelos.
def primos_gemelos(numero:int):
    lista_primos=generar_primos(numero)
    lista_primos_gemelos=[]
    for i in range(len(lista_primos)-1):
        if lista_primos[i+1]-lista_primos[i]==2:
            lista_primos_gemelos.append((lista_primos[i],lista_primos[i+1]))
    return lista_primos_gemelos



# Ejercicio 3

def triangulo_pascal(altura: int):
    # El triangulo siempre inicia con 1 en su punta
    triangulo = [[1]]

    for i in range(1, altura):
    # El primer elemento siempre es 1
        nueva_fila = [1]
        for j in range(1, i):
    # Se suman los elementos de la fila anterior a la nueva
            nuevo_valor = triangulo[i - 1][j - 1] + triangulo[i - 1][j]
            nueva_fila.append(nuevo_valor)
    # Último elemento siempre es 1
        nueva_fila.append(1)
        triangulo.append(nueva_fila)

    # Se imprime el triangulo pero de forma piramidal
    for fila in triangulo:
            print(fila)

# Ejercicio 4
def analizar_frecuencia(cadena:str):
    # Se limpia la cadena de palabras para que las palabras esten todas en minusculas y en lista
    lista_palabras=cadena.lower().strip('.,').split()
    # Se crea el diccionario de frecuencia
    frecuencia= {}
    # Se hace un loop con condicional, si existe ya la palabra se le suma un punto
    # y si no se le pone el primer punto
    for palabra in lista_palabras:
        if palabra in frecuencia:
            frecuencia[palabra] += 1
        else:
            frecuencia[palabra] = 1
    # Se retorna el diccionario
    return frecuencia

# Ejercicio 5

import random

def numero_aleatorio():
    return random.randint(1,100)

def adivina_el_numero():
    numero_a_adivinar=numero_aleatorio()
    numero_intentos=10
    while numero_intentos >0:
        numero_adivinado = int(input(f"ingresa el numero que adivinaste ({numero_intentos} intentos): "))
        if numero_adivinado==numero_a_adivinar:
            return print(f"Has adivinado con {numero_a_adivinar}")
        elif numero_adivinado>numero_a_adivinar:
            print("Mas bajo")
            numero_intentos-=1
        elif numero_adivinado<numero_a_adivinar:
            print("Mas alto")
            numero_intentos-=1
    return (print("Se te acabaron los intentos!"))

