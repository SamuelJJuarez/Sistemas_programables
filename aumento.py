# Función para aumentar el tamaño del ícono
def aumentar_icono(icono, factor):
    # Se valida que el factor sea un número positivo, si no lo es lanza una excepción
    if factor < 1:
        raise ValueError("El factor de aumento debe ser un entero positivo.")
    
    nuevo_icono = [] # Se inicializa una lista vacía para almacenar el ícono aumentado

    # Ahora con un ciclo for se recorre cada fila de la matriz original
    for fila in icono:
        nueva_fila = [] # Se crea una nueva fila para el ícono aumentado
        # Se recorre cada punto (columna) de la fila actual
        for c in fila:
            nueva_fila.extend([c] * factor)  # Extiende la nueva fila repitiendo cada píxel tantas veces como indique el factor
        # Repite la fila expandida tantas veces como indique el factor
        for _ in range(factor):   
            nuevo_icono.append(nueva_fila) # Agrega la nueva fila a la matriz del ícono aumentado

    return nuevo_icono # Devuelve la matriz del ícono aumentado