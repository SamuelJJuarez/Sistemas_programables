# Integrantes:
# Samuel Jafet Juárez Baliño
# Iván Alejandro Cadena López

# Objetivo: Desarrollar un programa que implemente un sistema de monitoreo continuo utilizando un sensor ultrasónico 
# y un sensor PIR (infrarrojo pasivo). El sistema deberá mostrar en la pantalla OLED la distancia a objetos en tiempo real y, 
# ante la detección de una fuente de calor, activar una rutina de alerta visual dinámica mediante interrupciones. 

# Se importan las clases Pin y SoftI2C del módulo machine. Pin se usa para controlar los pines GPIO del ESP32,
# mientras que SoftI2C implementa el protocolo de comunicación I2C por software
from machine import Pin, SoftI2C
from hcsr04 import HCSR04  # Se importa la clase HCSR04 para controlar el sensor ultrasónico HC-SR04
from logo import LOGO # Importa el logo desde el archivo logo.py
import ssd1306 # Se importa el módulo ssd1306 para controlar la pantalla OLED
import time # Se importa el módulo time para manejo de pausas y tiempos

# Variable que actúa como bandera para indicar cuando el sensor PIR detecta movimiento
motion_detected = False

# Matriz de píxeles que representa el símbolo de alerta (7x7 píxeles)
# Cada 1 representa un píxel encendido (blanco) y cada 0 un píxel apagado (negro)
alert = [
    [1,1,0,1,0,1,1],
    [1,0,1,1,1,0,1],
    [1,0,1,1,1,0,1],
    [1,0,1,1,1,0,1],
    [1,0,0,1,0,0,1],
    [1,0,0,0,0,0,1],
    [1,1,0,1,0,1,1],
]

# Función para escalar la matriz de alerta aumentando su tamaño por un factor específico
def escale_matrix(matriz, factor):
    salida = [] # Lista que almacenará la matriz escalada
    # Recorre cada fila de la matriz original
    for fila in matriz: 
        nueva_fila = [] # Crea una nueva fila para la matriz escalada
        # Recorre cada columna o valor de la fila actual
        for valor in fila:
            nueva_fila.extend([valor] * factor) # Extiende la nueva fila repitiendo cada píxel tantas veces como indique el factor
        # Repite la fila expandida tantas veces como indique el factor
        for _ in range(factor):  
            salida.append(list(nueva_fila)) # Agrega la nueva fila a la matriz del ícono aumentado

    return salida # Devuelve la matriz aumentada

# Función para dibujar una imagen (matriz de píxeles) en la pantalla OLED en una posición específica
def draw_simbol(oled, originx, originy, pic):
    # Coordenadas iniciales
    x = originx 
    y = originy

    # Recorre cada fila de la matriz de píxeles
    for r in range(len(pic)):
        # Recorre cada columna de la fila actual
        for c in range(len(pic[r])):
            # Dibuja el píxel en la posición (x, y) con el valor correspondiente de la matriz (1 o 0)
            oled.pixel(x,y,pic[r][c])
            x += 1 # Incrementa la coordenada x para la siguiente columna
        x = originx # Reinicia la coordenada x al inicio de la fila
        y += 1 # Incrementa la coordenada y para la siguiente fila

# Función que maneja la interrupción generada por el sensor PIR
def handle_interrupt(pin):
    global motion_detected # Se llama a la variable global
    motion_detected = True # Establece la bandera a True cuando se detecta movimiento

# Configuración del pin de interrupción para el sensor PIR conectado al GPIO17
pir_interrupt = Pin(17, Pin.IN) # Configura el pin GPIO17 como entrada
# Configura la interrupción para que se active en el flanco de subida (cuando el PIR detecta movimiento)
pir_interrupt.irq(trigger=Pin.IRQ_RISING, handler=handle_interrupt)

# Configuración del sensor ultrasónico HC-SR04 con pin trigger en GPIO13 y echo en GPIO12
ultra = HCSR04(trigger_pin=13,echo_pin=12)

# Configuración del I2C con los pines GPIO18 (SCL, línea de reloj) y GPI19 (SDA, línea de datos)
i2c = SoftI2C(sda=Pin(18),scl=Pin(19))

# Inicialización de la pantalla OLED con resolución 128x64 píxeles usando I2C
oled = ssd1306.SSD1306_I2C(128, 64, i2c)

# Función para imprimir el logo del Tecnológico
def imprimir_logo():
    oled.fill(0)# Limpia la pantalla
    # Recorre cada fila del logo
    for y, fila in enumerate(LOGO):
        x = 0 # Inicializa la posición horizontal (columna) en 0 para cada nueva fila
        # Recorre cada byte de la fila actual (cada byte representa 8 píxeles horizontales)
        for byte in fila:
            # Procesa cada bit del byte actual (de izquierda a derecha, bits 7 a 0)
            for bit in range(8):
                # Extrae el valor del bit específico usando desplazamiento de bits y operación AND
                pixel = (byte >> (7 - bit)) & 1
                # Dibuja el píxel en la posición (x, y) con el valor extraído (0 para apagado, 1 para encendido)
                oled.pixel(x, y, pixel)
                x += 1 # Incrementa la posición horizontal para el siguiente píxel
    oled.show() # Actualiza la pantalla para mostrar el logo
    time.sleep(5) # Pausa de 5 segundos para que el logo sea visible

def mostrar_info():
    oled.fill(0) # Limpia la pantalla
    oled.text('Sist.Programables', 0, 0)
    oled.text('ISC', 0, 10)
    oled.text('Equipo:', 0, 20)
    oled.text('Samuel J. Juarez B.', 0, 30)
    oled.text('Ivan A. Cadena L.', 0, 40)
    oled.text('22/09/2025', 0, 50)
    oled.show() # Actualiza la pantalla para mostrar la información
    time.sleep(5) # Pausa de 5 segundos para que la información sea visible

def mostrar_objetivo():
    oled.fill(0) # Limpia la pantalla
    oled.text("Objetivo:",0,0)
    oled.text("Aprender a como",0,10)
    oled.text("se puede medir",0,20)
    oled.text("distancia y ",0,30)
    oled.text("presencia con",0,40)
    oled.text("PIR y ultrasonico",0,50)
    oled.show() # Actualiza la pantalla para mostrar el objetivo
    time.sleep(5) # Pausa de 5 segundos para que el objetivo sea visible

imprimir_logo() # Muestra el logo del Tecnológico
mostrar_info() # Muestra la información del equipo  
mostrar_objetivo() # Muestra el objetivo de la práctica

# Bucle principal del programa
while True:
    # Verifica si la bandera de movimiento detectado está activada
    if motion_detected:
        oled.fill(0) # Limpia la pantalla

        # Efecto de parpadeo de pantalla: enciende y apaga la pantalla 3 veces
        for i in range(3):
            oled.fill(1) # Llena la pantalla de blanco (efecto flash)
            oled.show()
            time.sleep(0.2) # Mantiene el flash por 200ms
            oled.fill(0) # Limpia la pantalla (negro)
            oled.show()
            time.sleep(0.2) # Mantiene negro por 200m

        # Animación del símbolo de alerta: muestra el símbolo con diferentes tamaños
        for tamaño in [2, 3, 4, 3, 2]: # Efecto de crecimiento y encogimiento
            oled.fill(0) # Limpia la pantalla
            # Calcula la posición central para el símbolo según su tamaño
            posx = (128 - (7 * tamaño)) // 2
            posy = 5
            # Dibuja el símbolo de alerta escalado en el centro superior
            draw_simbol(oled, posx, posy, escale_matrix(alert, tamaño))

        oled.fill(0) # Limpia la pantalla
        draw_simbol(oled,50,0,escale_matrix(alert,4)) # Dibuja el símbolo de alerta escalado en la pantalla
        oled.text("Presencia",0,30) 
        oled.text("detectada!!!!",0,40)
        oled.show() # Actualiza la pantalla para mostrar el símbolo y el mensaje de alerta
        time.sleep(5) # Pausa de 5 segundos para que la alerta sea visible
        motion_detected = False # Reinicia la bandera de movimiento detectado
    else: # Si no se ha detectado movimiento
        oled.fill(0) # Limpia la pantalla
        oled.text("Detectando",0,0) 
        oled.text("presencia...",0,10)
    
        # Mide la distancia usando el sensor ultrasónico HC-SR04
        distancia = ultra.distance_cm() 
        oled.text("Objeto cercano a",0,47) 
        if distancia <= 0 or distancia >= 250: # Verifica si la distancia medida es inválida
            oled.text("Error de lectura",0,55)
        else: # Si la distancia es válida, la muestra en la pantalla
            oled.text(f"{distancia} cm",0,55)
        oled.show() # Actualiza la pantalla para mostrar la distancia medida

    # Pausa de 0.5 segundos antes de la siguiente iteración del bucle
    time.sleep(0.5)