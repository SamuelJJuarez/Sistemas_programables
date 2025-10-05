# Integrantes:
# Samuel Jafet Juárez Baliño
# Iván Alejandro Cadena López

# Fecha: 29/09/2025

# Objetivo: Desarrollar un programa que implemente un sistema de monitoreo continuo utilizando un sensor ultrasónico 
# y un sensor PIR (infrarrojo pasivo). El sistema deberá mostrar en la pantalla OLED la distancia a objetos en tiempo real,
# emitir beeps cuya frecuencia dependa de la distancia detectada, y ante la detección de una fuente de calor, activar una 
# rutina de alerta visual dinámica mediante interrupciones y reproducir una melodía personalizada.

# Se importan las clases Pin y SoftI2C del módulo machine. Pin se usa para controlar los pines GPIO del ESP32,
# mientras que SoftI2C implementa el protocolo de comunicación I2C por software
from machine import Pin, SoftI2C, PWM
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

# Configuración de buzzer activo para beeps de distancia (GPIO25)
buzzer_activo = Pin(25, Pin.OUT)

# Configuración de buzzer pasivo para melodías (GPIO26)
buzzer_pasivo_pin = Pin(26, Pin.OUT)

# Diccionario de frecuencias de notas musicales para la melodía, buscadas en internet
notas = {'V': 0, 'G3': 196, 'B3': 247, 'C4':262 ,'C#4': 277, 'D4': 294, 'E4': 330, 'F4': 349, 
         'F#4': 370, 'G4': 392, 'A4': 440, 'B4': 494}

# Diccionario de duraciones de notas musicales, en base a la duración de cada tipo de nota
duraciones = {'Redonda': 4, 'Blanca': 2, 'Negra': 1, 'NegraExt': 1.5, 'Corchea': 0.5, 'Semicorchea': 0.25, 'Fusa': 0.125}

# Función para calcular el retardo entre beeps basado en la distancia
def calcular_retardo_beeps(distancia):
    # Calcula el retardo entre beeps basándose en la distancia detectada
    # Fórmula aplicada: 
    # Si distancia < 50 cm: retardo = 0.1 segundos (beeps rápidos)
    # Si distancia >= 50 cm: retardo = distancia * 0.005 segundos (proporcional)
    
    # Ejemplos de la fórmula:
    # 50 cm → 0.25 segundos
    # 100 cm → 0.5 segundos  
    # 200 cm → 1.0 segundo
    # 400 cm → 2.0 segundos (máximo)
    
    if distancia < 50:
        return 0.1  # Beeps rápidos para objetos cercanos
    else:
        # Retardo proporcional: distancia * 0.005 para cumplir con los ejemplos
        # 100 cm * 0.005 = 0.5 segundos
        # 200 cm * 0.005 = 1.0 segundo
        retardo = distancia * 0.005
        return min(retardo, 2.0)  # Limita el retardo máximo a 2 segundos

# Función para generar un beep con buzzer activo
def generar_beep_activo():
    # El buzzer activo solo requiere encendido/apagado (HIGH/LOW)
    buzzer_activo.on()   # Enciende el buzzer
    time.sleep(0.1)      # Duración del beep: 100ms
    buzzer_activo.off()  # Apaga el buzzer

# Función para reproducir una nota musical con buzzer pasivo (PWM)
def tocar_nota(nota, duracion, tempo):
    # Reproduce una nota musical usando PWM en el buzzer pasivo
    # nota: clave del diccionario 'notas' (ej: 'C4', 'D4')
    # duracion: clave del diccionario 'duraciones' (ej: 'Negra', 'Corchea')
    # tempo: velocidad de reproducción en BPM (beats por minuto)

    frecuencia = notas[nota]  # Obtiene la frecuencia de la nota
    tiempo_sonido = duraciones[duracion] * (60 / tempo)  # Calcula duración en segundos en base al tempo

    if frecuencia == 0:  # Silencio (nota 'V')
        time.sleep(tiempo_sonido)  # Pausa sin sonido
    else:
        # Configura PWM en el buzzer pasivo con la frecuencia de la nota
        pwm = PWM(buzzer_pasivo_pin, freq=int(frecuencia), duty=512) 
        
        # Reproduce la nota durante el 80% del tiempo asignado
        time.sleep(tiempo_sonido * 0.8)
        
        # Detiene el PWM para terminar la nota
        pwm.deinit()
        
        # Pausa breve entre notas (20% del tiempo restante, para que se alcance a distinguir cada nota)
        time.sleep(tiempo_sonido * 0.2)

# Función para reproducir la melodía completa cuando se detecta movimiento PIR
def reproducir_melodia_pir():
    # Reproduce un fragmento de la canción "Secrets" de OneRepublic
    # Esta melodía se activa cuando el sensor PIR detecta movimiento
    # Secuencia de notas de la melodía
    notas_melodia = ['D4', 'F#4', 'A4', 'F#4', 'D4', 'F#4', 'A4', 'F#4',
                     'D4', 'F#4', 'A4', 'F#4', 'D4', 'F#4', 'A4', 'F#4',
                     'C#4', 'F#4', 'A4', 'F#4', 'A4', 'F#4', 'C#4', 'F#4',
                     'C#4', 'F#4', 'A4', 'F#4', 'A4', 'F#4', 'C#4', 'F#4',
                     'B3', 'D4', 'B4', 'D4', 'B4', 'D4', 'B3', 'D4',
                     'B3', 'D4', 'B4', 'D4', 'B4', 'D4', 'B3', 'D4',
                     'G3', 'D4', 'B4', 'D4', 'B4', 'D4', 'B4', 'D4',
                     'V', 'V', 'A4', 'A4', 'A4', 'A4', 'A4',
                     'A4', 'F#4', 'V', 'V',
                     'V', 'V', 'A4', 'A4', 'A4', 'A4',
                     'A4', 'F#4', 'E4', 'V',
                     'V', 'V', 'A4', 'A4', 'A4', 'A4', 'A4',
                     'A4', 'F#4', 'V', 'V',
                     'V', 'V', 'A4', 'A4', 'A4', 'A4', 'A4',
                     'A4', 'D4', 'D4', 'B3']

    # Duración correspondiente para cada nota de la melodía
    duracion_melodia = ['Corchea', 'Corchea', 'Corchea', 'Corchea', 'Corchea', 'Corchea', 'Corchea', 'Corchea',
                        'Corchea', 'Corchea', 'Corchea', 'Corchea', 'Corchea', 'Corchea', 'Corchea', 'Corchea',
                        'Corchea', 'Corchea', 'Corchea', 'Corchea', 'Corchea', 'Corchea', 'Corchea', 'Corchea',
                        'Corchea', 'Corchea', 'Corchea', 'Corchea', 'Corchea', 'Corchea', 'Corchea', 'Corchea',
                        'Corchea', 'Corchea', 'Corchea', 'Corchea', 'Corchea', 'Corchea', 'Corchea', 'Corchea',
                        'Corchea', 'Corchea', 'Corchea', 'Corchea', 'Corchea', 'Corchea', 'Corchea', 'Corchea',
                        'Corchea', 'Corchea', 'Corchea', 'Corchea', 'Corchea', 'Corchea', 'Corchea', 'Corchea',
                        'Negra', 'Corchea', 'Corchea', 'Corchea', 'Corchea', 'Corchea', 'Corchea',
                        'Negra', 'Negra', 'Negra', 'Negra',
                        'Negra', 'Negra', 'Corchea', 'Corchea', 'Corchea', 'Corchea',
                        'Negra', 'Negra', 'Negra', 'Negra',
                        'Negra', 'Corchea', 'Corchea', 'Corchea', 'Corchea', 'Corchea', 'Corchea',
                        'Negra', 'Negra', 'Negra', 'Negra',
                        'Negra', 'Corchea', 'Corchea', 'Corchea', 'Corchea', 'Corchea', 'Corchea',
                        'Negra', 'Negra', 'Corchea', 'NegraExt']

    # Reproduce cada nota de la melodía con su duración correspondiente
    for i in range(len(notas_melodia)):
        nota = notas_melodia[i]      # Nota actual de la secuencia
        duracion = duracion_melodia[i]  # Duración de la nota actual
        tocar_nota(nota, duracion, 150)  # Reproduce la nota con tempo de 150 

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
    # originx, originy: coordenadas de origen donde comenzar a dibujar
    # pic: matriz bidimensional que representa la imagen a dibujar
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

# Configuración del I2C con los pines GPIO18 (SDA, línea de datos) y GPIO19 (SCL, línea de reloj)
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

# Función para mostrar información del equipo
def mostrar_info():
    oled.fill(0) # Limpia la pantalla
    oled.text('Sist.Programables', 0, 0)    # Materia
    oled.text('ISC', 0, 10)                 # Carrera
    oled.text('Equipo:', 0, 20)             # Etiqueta del equipo
    oled.text('Samuel J. Juarez B.', 0, 30) # Primer integrante
    oled.text('Ivan A. Cadena L.', 0, 40)   # Segundo integrante
    oled.text('29/09/2025', 0, 50)          # Fecha del proyecto
    oled.show() # Actualiza la pantalla para mostrar la información
    time.sleep(5) # Pausa de 5 segundos para que la información sea visible

# Función para mostrar el objetivo del proyecto
def mostrar_objetivo():
    oled.fill(0) # Limpia la pantalla
    oled.text("Objetivo:",0,0)                     
    oled.text("Sistema de monitoreo",0,10)         
    oled.text("con sensor PIR,",0,20)               
    oled.text("ultrasonico y buzzer",0,30)          
    oled.text("con melodias y beeps",0,40)          
    oled.text("proporcionales",0,50)                
    oled.show() # Actualiza la pantalla para mostrar el objetivo
    time.sleep(5) # Pausa de 5 segundos para que el objetivo sea visible

# Secuencia de presentación inicial
imprimir_logo() # Muestra el logo del Tecnológico
mostrar_info() # Muestra la información del equipo  
mostrar_objetivo() # Muestra el objetivo de la práctica

# Bucle principal del programa
while True:
    # Verifica si la bandera de movimiento detectado está activada
    if motion_detected:
        
        # Rutina de alerta visual con efectos de pantalla
        oled.fill(0) # Limpia la pantalla

        # Reproduce la melodía completa en paralelo con la alerta visual
        reproducir_melodia_pir()

        # Efecto de parpadeo de pantalla: enciende y apaga la pantalla 3 veces
        for i in range(3):
            oled.fill(1) # Llena la pantalla de blanco (efecto flash)
            oled.show()
            time.sleep(0.2) # Mantiene el flash por 200ms
            oled.fill(0) # Limpia la pantalla (negro)
            oled.show()
            time.sleep(0.2) # Mantiene negro por 200ms

        # Animación del símbolo de alerta: muestra el símbolo con diferentes tamaños
        for tamaño in [2, 3, 4, 3, 2]: # Efecto de crecimiento y encogimiento
            oled.fill(0) # Limpia la pantalla
            # Calcula la posición central para el símbolo según su tamaño
            posx = (128 - (7 * tamaño)) // 2
            posy = 5
            # Dibuja el símbolo de alerta escalado en el centro superior
            draw_simbol(oled, posx, posy, escale_matrix(alert, tamaño))
            oled.show()
            time.sleep(0.3) # Duración de cada frame de la animación

        # Muestra mensaje final de alerta
        oled.fill(0) # Limpia la pantalla
        draw_simbol(oled,50,0,escale_matrix(alert,4)) # Dibuja el símbolo de alerta escalado en la pantalla
        oled.text("Presencia",0,30)      # Mensaje de alerta línea 1
        oled.text("detectada!!!!",0,40)  # Mensaje de alerta línea 2
        oled.show() # Actualiza la pantalla para mostrar el símbolo y el mensaje de alerta
        time.sleep(5) # Pausa de 5 segundos para que la alerta sea visible
        motion_detected = False # Reinicia la bandera de movimiento detectado
        
    else: # Modo normal: monitoreo continuo cuando no hay movimiento detectado
        oled.fill(0) # Limpia la pantalla
        oled.text("Detectando",0,0)      
        oled.text("presencia...",0,10)   
    
        # Mide la distancia usando el sensor ultrasónico HC-SR04
        distancia = ultra.distance_cm() 
        oled.text("Objeto cercano a",0,30)  # Etiqueta de distancia
        
        if distancia <= 0 or distancia >= 250: # Verifica si la distancia medida es inválida
            oled.text("Error de lectura",0,40)   # Mensaje de error
            oled.text("No hay beeps",0,50)       # Indica que no hay sonido por error
        else: # Si la distancia es válida
            oled.text(f"{distancia:.1f} cm",0,40)  # Muestra la distancia medida
            
            # Calcula y muestra el retardo de beeps
            retardo = calcular_retardo_beeps(distancia)
            oled.text(f"Beep cada {retardo:.2f}s",0,50)  # Muestra intervalo de beeps
            
            # Genera beep con buzzer activo basado en la distancia
            generar_beep_activo()
            
            # Aplica el retardo calculado antes del siguiente beep
            time.sleep(retardo)
            
        oled.show() # Actualiza la pantalla para mostrar la información

    # Pausa mínima del bucle principal para estabilidad del sistema
    time.sleep(0.1)