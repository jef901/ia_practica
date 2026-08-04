def calcular_promedio(lista_numeros):
    if not lista_numeros:
        return "Error: La lista no puede estar vacía"
    
    suma = 0
    for num in lista_numeros:
        suma += num
    
    resultado = suma / len(lista_numeros)
    return resultado

print(calcular_promedio([1, 2, 3, 4, 5]))  # Ahora imprimirá el promedio: 3.0