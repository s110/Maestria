#Pregunta 1: Matrices y Estructuras de Control
#si pidieran que el usuario cree el laberinto cambiaria la variable de abajo por un input de matrices.
laberinto=[
    ['#','#','#','#','#'],
    ['#',' ',' ',' ','#'],
    ['#',' ','espada',' ','#'],
    ['#','escudo',' ','pocion','#'],
    ['#','#','#',' ',' '],
]
#El print por lineas separadas mediante list comprehension
#[print(laberinto[x],'\n') for x in range(len(laberinto))]


#[['#','#','#','#','#'],['#',' ',' ',' ','#'],['#',' ',' ',' ','#'],['#',' ',' ',' ','#'],['#','#','#','#','#'],]

#Pregunta 2: Slicing y Mostrar el Laberinto
#Asumiendo que la posicion (1,1) es con lenguaje de programacion en
# python, entonces iniciaria en la segunda fila y columna
x=1
y=1
laberinto[x][y]='P'
[print(laberinto[x],'\n') for x in range(len(laberinto))]

#definir el inventario como un dic vacio
inventario={}
#definir la actualizacion del inventario
def actualizar_inventario(objeto):
    if objeto in inventario:
        inventario[objeto]+=1
    else:
        inventario[objeto]=1

#Para hallar los objetos unicos
objetos_unicos=[]

for i in range(len(laberinto)):
    for x in range(len(laberinto[i])):
        if laberinto[x][i]!=' ' and laberinto[x][i]!='#' and laberinto[x][i]!='P':
            objetos_unicos.append(laberinto[x][i])
objetos_unicos=list(set(objetos_unicos))

objetos_unicos_en_inventario=[]

#esta es la funcion de movimiento
while True:
    posicion_nueva=input('A donde te quieres mover?')
    if posicion_nueva=='arriba':
        if laberinto[x-1][y]=='#':
            print('Hay una pared! Intenta otro movimiento')
        elif laberinto[x-1][y]!=' ':
            print(f'Haz encontrado una {laberinto[x-1][y]}')
            actualizar_inventario(laberinto[x-1][y])
            laberinto[x][y] = ' '
            x = x - 1
            laberinto[x][y] = 'P'
        else:
            laberinto[x][y]=' '
            x=x-1
            laberinto[x][y] = 'P'
    elif posicion_nueva == 'abajo':
        if laberinto[x+1][y]=='#':
            print('Hay una pared! Intenta otro movimiento')
        elif laberinto[x+1][y]!=' ':
            print(f'Haz encontrado una {laberinto[x+1][y]}')
            actualizar_inventario(laberinto[x + 1][y])
            laberinto[x][y] = ' '
            x = x + 1
            laberinto[x][y] = 'P'
        else:
            laberinto[x][y] = ' '
            x = x + 1
            laberinto[x][y] = 'P'
    elif posicion_nueva == 'izquierda':
        if laberinto[x][y-1]=='#':
            print('Hay una pared! Intenta otro movimiento')
        elif laberinto[x][y-1]!=' ':
            print(f'Haz encontrado una {laberinto[x][y-1]}')
            actualizar_inventario(laberinto[x][y-1])
            laberinto[x][y] = ' '
            y = y - 1
            laberinto[x][y] = 'P'
        else:
            laberinto[x][y] = ' '
            y = y - 1
            laberinto[x][y] = 'P'
    elif posicion_nueva == 'derecha':
        if laberinto[x][y+1]=='#':
            print('Hay una pared! Intenta otro movimiento')
        elif laberinto[x][y+1]!=' ':
            print(f'Haz encontrado una {laberinto[x][y+1]}')
            actualizar_inventario(laberinto[x][y + 1])
            laberinto[x][y] = ' '
            y = y + 1
            laberinto[x][y] = 'P'
        else:
            laberinto[x][y] = ' '
            y = y + 1
            laberinto[x][y] = 'P'
    #[print(laberinto[x], '\n') for x in range(len(laberinto))]
    #objetos_unicos_en_inventario=[objeto for objeto in inventario if objeto in objetos_unicos]
    #print(set(objetos_unicos_en_inventario))

#Pregunta 4: Listas por Comprensión y Sets


