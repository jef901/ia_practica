def calcular_promedio(lista_numeros):
    suma = 0
    for num in lista_numeros:
        suma += num
    
    if len(lista_numeros) == 0:
        return "Error: La lista no puede estar vacía"
    
    resultado = suma / len(lista_numeros)
    return resultado

print(calcular_promedio([]))