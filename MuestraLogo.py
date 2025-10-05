# Integrantes:
# Samuel Jafet Juárez Baliño
# Iván Alejandro Cadena López

# Objetivo: Mostrar el logotipo del Instituto Tecnológico de León en una pantalla OLED utilizando MicroPython en un ESP32,
# cuyo código puede ser reutilizado para mostrar cualquier imagen en formato de matriz de bits, solamente
# modificando la matriz importada del archivo logo.py con los datos correspondientes a la imagen deseada.


# Se importan las clases Pin y SoftI2C del módulo machine. Pin se usa para controlar los pines GPIO del ESP32,
# mientras que SoftI2C implementa el protocolo de comunicación I2C por software
from machine import Pin, SoftI2C
import ssd1306 # Se importa el módulo ssd1306 para controlar la pantalla OLED
from logo import LOGO # Se importa el logo desde el archivo logo.py

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

oled.fill(0)  # Limpia la pantalla llenándola de negro (valor 0)

# Recorre cada fila del logo
for y, fila in enumerate(LOGO):
    x = 0 # Inicializa la posición horizontal (columna) en 0 para cada nueva fila

    # Recorre cada byte de la fila actual (cada byte representa 8 píxeles horizontales)
    for byte in fila:
        # Procesa cada bit del byte actual (de izquierda a derecha, bits 7 a 0)  
        for bit in range(8):
            # Extrae el valor del bit específico usando desplazamiento de bits y operación AND
            # (byte >> (7 - bit)) desplaza el byte hacia la derecha para posicionar el bit deseado en la posición 0
            # & 1 aplica una máscara para obtener solo el valor del bit menos significativo (0 o 1)
            pixel = (byte >> (7 - bit)) & 1  
             # Dibuja el píxel en la posición (x, y) con el valor extraído (0 para apagado, 1 para encendido)
            oled.pixel(x, y, pixel)
            x += 1 # Incrementa la posición horizontal para el siguiente píxel

# Actualiza la pantalla para mostrar el logo dibujado
oled.show()