# Integrantes:
# Samuel Jafet Juárez Baliño
# Iván Alejandro Cadena López

# Objetivo: Mostrar un ícono predefinido en una pantalla OLED utilizando MicroPython en un ESP32,
# permitiendo al usuario definir el tamaño de escala del ícono mediante un factor de aumento
# dado a través de una entrada en consola.

# Se importan las clases Pin y SoftI2C del módulo machine. Pin se usa para controlar los pines GPIO del ESP32,
# mientras que SoftI2C implementa el protocolo de comunicación I2C por software
from machine import Pin, SoftI2C
import ssd1306 # Se importa el módulo ssd1306 para controlar la pantalla OLED

# Configuración del I2C con los pines GPIO15 (SCL, línea de reloj) y GPIO4 (SDA, línea de datos)
i2c = SoftI2C(scl=Pin(15), sda=Pin(4))

# Configuración del pin GPIO16 como salida para resetear el OLED
pin = Pin(16, Pin.OUT)
pin.value(0) # Configura GPIO16 en bajo para resetear el OLED
pin.value(1) # Configura GPIO16 en alto para activar el OLED

oled_ancho = 128 # Se define el ancho del OLED
oled_alto = 64 # Se define el alto del OLED

# Se crea el objeto que representa la pantalla OLED, especificando sus dimensiones y el bus I2C para comunicarse con ella
oled = ssd1306.SSD1306_I2C(oled_ancho, oled_alto, i2c) 

# Matriz de puntos que representa al ícono
ICONO = [ 
 [ 0, 0, 1, 0, 0, 0, 1, 0, 0],
 [ 0, 0, 1, 0, 0, 0, 1, 0, 0],
 [ 0, 1, 1, 1, 1, 1, 1, 1, 0],
 [ 1, 1, 0, 0, 1, 0, 0, 1, 1],
 [ 1, 1, 1, 1, 1, 1, 1, 1, 1],
 [ 1, 0, 1, 0, 0, 0, 1, 0, 1],
 [ 1, 0, 1, 1, 1, 1, 1, 0, 1],
 [ 0, 0, 1, 1, 0, 1, 1, 0, 0],
 [ 0, 1, 1, 1, 0, 1, 1, 1, 0],
]

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

# Solicita al usuario el factor de aumento
aumento = int(input("Ingrese el factor de aumento del ícono(entero positivo): "))

# Llama a la función para aumentar el ícono
icono_aumentado = aumentar_icono(ICONO, aumento)

oled.fill(0)  # Limpia la pantalla

for y, fila in enumerate(icono_aumentado): # Recorre cada fila del ícono aumentado
   for x, c in enumerate(fila): # Recorre cada punto (columna) de la fila actual
        # Dibuja el píxel en la posición (x, y) con el color c (1 para encendido, 0 para apagado)
        oled.pixel(x, y, c)

# Actualiza la pantalla para mostrar el ícono dibujado
oled.show()