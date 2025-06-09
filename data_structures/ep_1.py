class Solution:
    def maxDepth(self,s: str) -> int:
        ##Se crea una pila y 2 counters, uno para contar el nivel en ese momento
        # y el otro para almacenar los niveles obtenidos y obtener el maximo
        counter = 0
        parenthesis_stack = []
        counter_stack = []
        if len(s) == 0: ##Si la longitud del string es 0 entonces se retorna 0
            return 0
        for i in s: ## Sino por cada letra en el string se configura una pila
            if i == '(': ## el parentesis izquiero se inserta en la pila
                parenthesis_stack.insert(0, i)
                counter += 1
            elif i == ')' and parenthesis_stack and parenthesis_stack[0] == '(':
                parenthesis_stack.pop(0) ##el derecho quita la info de la pila
                counter_stack.append(counter) #se suma al counter
                counter -= 1
        if len(parenthesis_stack) == 0:
            return max(counter_stack) ## se retorna la info de el maximo stack alcanzado de parentesis anidados


def maxDepth(s: str) -> int:
    ##Se crea una pila y 2 counters, uno para contar el nivel en ese momento
    # y el otro para almacenar los niveles obtenidos y obtener el maximo
    counter = 0
    parenthesis_stack = []
    counter_stack = []
    if len(s) == 0: ##Si la longitud del string es 0 entonces se retorna 0
        return 0
    for i in s: ## Sino por cada letra en el string se configura una pila
        if i == '(': ## el parentesis izquiero se inserta en la pila
            parenthesis_stack.insert(0, i)
            counter += 1
        elif i == ')' and parenthesis_stack and parenthesis_stack[0] == '(':
            parenthesis_stack.pop(0) ##el derecho quita la info de la pila
            counter_stack.append(counter) #se suma al counter
            counter -= 1
    if len(parenthesis_stack) == 0:
        return max(counter_stack) ## se retorna la info de el maximo stack alcanzado de parentesis anidados

maxDepth("abc()")