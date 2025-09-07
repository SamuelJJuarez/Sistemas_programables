# Integrantes:
# Samuel Jafet Juárez Baliño
# Iván Alejandro Cadena López

# Objetivo: Mostrar texto referente a los integrantes del equipo y la materia en una pantalla OLED utilizando MicroPython en un ESP32,
# permitiendo un efecto de desplazamiento horizontal (scroll) del texto para los nombres u textos cuyo
# ancho exceda el espacio habitual de la pantalla.

# Se importan las clases Pin y SoftI2C del módulo machine. Pin se usa para controlar los pines GPIO del ESP32,
# mientras que SoftI2C implementa el protocolo de comunicación I2C por software
from machine import Pin, SoftI2C
import ssd1306 # Se importa el módulo ssd1306 para controlar la pantalla OLED
from time import sleep # Se importa sleep para crear pausas en segundos

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

# Función para crear efecto de desplazamiento horizontal del texto (scroll)
def scroll_text(text, y=0, delay=0.05):
    global oled # Permite acceder a la variable global oled desde dentro de la función
    global oled_ancho # Permite acceder a la variable global oled_ancho desde dentro de la función
    
    # Calcula el ancho aproximado del texto en píxeles (8 píxeles por carácter)
    ancho_texto = len(text) * 8  

    # Bucle que mueve el texto desde la derecha hacia la izquierda
    # Inicia desde oled_ancho (fuera del borde derecho) hasta -ancho_texto (completamente fuera del borde izquierdo)
    for x in range(oled_ancho, -ancho_texto, -1):
        # Limpia una franja horizontal de 8 píxeles de alto en la posición y especificada
        oled.fill_rect(0, y, oled_ancho, 8, 0)
        oled.text(text, x, y) # Dibuja el texto en la nueva posición (x, y)
        oled.show() # Actualiza la pantalla para mostrar el texto en su nueva posición
        sleep(delay) # Pausa para controlar la velocidad del desplazamiento


oled.fill(0) # Limpia toda la pantalla
# Dibuja texto estático en diferentes posiciones de la pantalla
oled.text('Sist.Programables', 0, 0)
oled.text('ISC', 0, 10)
oled.text('Equipo:', 0, 20)
oled.text('03/09/2025', 0, 50)
oled.show() # Actualiza la pantalla para mostrar el texto estático

# Ejecuta el efecto de scroll para mostrar los nombres de los integrantes del equipo
scroll_text('Samuel Jafet Juarez Balino', y=30, delay=0.001)
scroll_text('Ivan Alejandro Cadena Lopez', y=40, delay=0.001)
