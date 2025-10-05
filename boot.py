# Integrantes:
# Samuel Jafet Juárez Baliño
# Iván Alejandro Cadena López

# Archivo: boot.py
# Propósito: Este archivo se ejecuta automáticamente al encender el ESP32, antes que main.py
# Función: Realizar configuraciones iniciales del sistema y preparar el entorno para la ejecución del programa principal

# Objetivo: Configurar el sistema del ESP32 para que funcione de manera autónoma sin necesidad de conexión
# a una computadora. Este archivo realiza configuraciones básicas y verificaciones iniciales antes de que
# el programa principal (main.py) tome el control del carrito motorizado.

import gc # Se importa el módulo gc (garbage collector) para gestión de memoria

# Ejecuta el recolector de basura para liberar memoria no utilizada
# Esto es importante en sistemas embebidos con memoria limitada como el ESP32
gc.collect()

# Mensaje de confirmación en la consola (útil durante desarrollo y depuración)
print("Sistema iniciado - boot.py ejecutado correctamente")
print("Cargando main.py...")

# Nota: El archivo main.py se ejecutará automáticamente después de boot.py
# No es necesario importarlo o llamarlo explícitamente