# Integrantes:
# Samuel Jafet Juárez Baliño
# Iván Alejandro Cadena López

# Fecha: 29/09/2025

# Objetivo: Desarrollar un videojuego estilo Space Invaders para ESP32 llamado "Los Bunkers" donde el jugador
# debe defender el planeta de invasores alienígenas. El juego utiliza un giroscopio MPU6050 para controlar la mira
# mediante movimientos físicos del ESP32, un botón para disparar, y una pantalla OLED para visualizar el juego.
# El objetivo es eliminar a los enemigos antes de que destruyan los búnkers defensivos.

# Se importan las clases Pin y SoftI2C del módulo machine. Pin se usa para controlar los pines GPIO del ESP32,
# mientras que SoftI2C implementa el protocolo de comunicación I2C por software
from machine import Pin, SoftI2C
from MPU6050 import MPU6050 # Se importa la clase MPU6050 para controlar el giroscopio/acelerómetro MPU6050
from ssd1306 import SSD1306_I2C # Se importa la clase SSD1306_I2C para controlar la pantalla OLED
from game_assets import enemy, qaim, aim, bunker, Aim, Enemy, Bunker # Se importan los sprites y clases del juego
import time # Se importa el módulo time para manejo de pausas y tiempos
import random # Se importa random para generar comportamiento aleatorio de los enemigos
import math # Se importa math para cálculos matemáticos (magnitud vectorial del acelerómetro)

# Configuración del I2C con los pines GPIO18 (SCL, línea de reloj) y GPIO19 (SDA, línea de datos)
i2c = SoftI2C(scl=Pin(18), sda=Pin(19))
# Inicialización de la pantalla OLED con resolución 128x64 píxeles usando I2C
oled = SSD1306_I2C(128, 64, i2c)

# Configuración de los pines de entrada del juego
button = Pin(16, Pin.IN, Pin.PULL_UP) # Botón de disparo en GPIO16 con resistencia pull-up interna
mpu = MPU6050() # Instancia del sensor MPU6050 (giroscopio + acelerómetro)

# Función de interrupción que se ejecuta cuando el jugador presiona el botón para disparar
def handle_shoot(pin):
    # Verifica colisiones entre la mira del jugador y los enemigos
    # Si hay colisión, incrementa puntos y resetea la posición del enemigo
    
    global enemies, points, player # Variables globales necesarias para el disparo
    
    # Itera sobre todos los enemigos activos en pantalla
    for enemy in enemies:
        # Verifica colisión usando el punto pivote de la mira (esquina superior izquierda)
        # Comprueba si el punto (player.x, player.y) está dentro del área del enemigo (8x8 píxeles)
        if (player.x > enemy.x and player.x < (enemy.x + 8)) and player.y > enemy.y and player.y < (enemy.y + 8):
            points += 1 # Incrementa la puntuación del jugador
            enemy.y = 0 # Resetea la posición vertical del enemigo (lo regresa al inicio)
            break # Sale del bucle después del primer impacto
        
        # Verifica colisión usando el punto del borde derecho de la mira (player.x+4, player.y+4)
        # Esto proporciona una segunda área de colisión para hacer el disparo más tolerante
        if (player.x+4 > enemy.x and player.x+4 < (enemy.x + 8)) and player.y+4 > enemy.y and player.y+4 < (enemy.y + 8):
            points += 1 # Incrementa la puntuación del jugador
            enemy.y = 0 # Resetea la posición vertical del enemigo
            break # Sale del bucle después del primer impacto

# Configura la interrupción del botón para que se active en el flanco descendente (cuando se presiona)
button.irq(trigger=Pin.IRQ_FALLING, handler=handle_shoot)

# Parámetros de configuración del giroscopio para el control de la mira
gyro_sensitivity = 0.5  # Sensibilidad del giroscopio (0.5 = normal, 1.0 = rápida)
gyro_deadzone = 0.02    # Zona muerta para evitar drift (movimiento no intencional por ruido del sensor)

# Variables globales del juego
player = Aim(0,0) # Objeto de la mira del jugador inicializado en posición (0,0)
playing = True # Bandera que controla si el juego está activo
bunkers = [] # Lista que almacenará todos los búnkers defensivos del juego
enemies = [] # Lista que almacenará todos los enemigos alienígenas del juego
points = 0 # Contador de puntos del jugador
eliminated = [] # Lista que almacena los rails (carriles) de búnkers destruidos

# Función para mostrar la pantalla de presentación del juego
def presentation():
    global oled # Variable global de la pantalla OLED
    
    # Pantalla 1: Título y créditos
    oled.fill(0) # Limpia la pantalla
    oled.text("Los bunkers",19,0) 
    oled.text("Integrantes:",0,10) 
    oled.text("Ivan A. Cadena",0,20) 
    oled.text("Samuel J. Juarez",0,30)
    oled.text("Fecha: 29/09/25",0,40)
    oled.text("Sist.Programables",0,50)
    oled.show() # Actualiza la pantalla
    time.sleep(3) # Pausa breve para visualizar

    # Pantalla 2: Historia del juego
    oled.fill(0) # Limpia la pantalla
    oled.text("Historia:",0,0) 
    oled.text("Los aliens invad",0,10) 
    oled.text("en la tierra y t",0,20) 
    oled.text("u objetivo es de",0,30) 
    oled.text("tenerlos usando",0,40) 
    oled.text("el space shooter",0,50)
    oled.show() # Actualiza la pantalla
    time.sleep(3) # Pausa para leer la historia

    # Pantalla 3: Mensaje de preparación
    oled.fill(0) # Limpia la pantalla
    oled.text("¿Preparado?...",11,0) # Mensaje centrado
    oled.show() # Actualiza la pantalla
    time.sleep(1) # Pausa breve antes de comenzar

# Función para inicializar los búnkers defensivos en sus posiciones
def init_bunkers():
    # Crea 9 búnkers distribuidos uniformemente en la parte inferior de la pantalla
    # Cada búnker se coloca en un carril específico (1-9) con separación de 14 píxeles

    cont = 1 # Contador para asignar número de carril a cada búnker
    # Itera desde 0 hasta 127 (ancho de pantalla) con pasos de 14 píxeles
    for field in range(0,127,14):
        # Crea un búnker en el carril 'cont', posición X = field+7, posición Y = 55 (cerca del fondo)
        bunkers.append(Bunker(cont,field+7,55))
        cont += 1 # Incrementa el contador de carril

# Función para inicializar los enemigos alienígenas en sus posiciones iniciales
def init_enemies():
    # Crea 9 enemigos distribuidos uniformemente en la parte superior de la pantalla
    # Cada enemigo se coloca en un carril específico (1-9) con separación de 14 píxeles

    cont = 1 # Contador para asignar número de carril a cada enemigo
    # Itera desde 0 hasta 127 (ancho de pantalla) con pasos de 14 píxeles
    for field in range(0,127,14):
        # Crea un enemigo en el carril 'cont', posición X = field+7, posición Y = 0 (parte superior)
        enemies.append(Enemy(cont,field+7,0))
        cont += 1 # Incrementa el contador de carril

# Función para renderizar/dibujar un sprite (matriz de píxeles) en la pantalla OLED
def render_item(x, y, item):
    # x, y: coordenadas de inicio donde dibujar el sprite
    # item: matriz bidimensional que representa el sprite (8x8 píxeles)

    global oled # Variable global de la pantalla OLED
    
    # Itera sobre cada fila de la matriz del sprite
    for row in item:
        # Itera sobre cada píxel de la fila actual
        for pixel in row:
            # Dibuja el píxel en la posición (x, y) con el valor del pixel (0 o 1)
            oled.pixel(x,y,pixel)
            x += 1 # Avanza a la siguiente posición horizontal
        x -= len(row) # Regresa x al inicio de la fila
        y += 1 # Avanza a la siguiente fila (incrementa y)

# Función para manejar el movimiento de la mira usando el giroscopio MPU6050
def handle_aim():
    # El giroscopio controla la posición (inclinación del ESP32)
    # El acelerómetro detecta movimientos rápidos para cambiar el tipo de mira

    global mpu, player, gyro_deadzone, gyro_sensitivity # Variables globales necesarias
    
    # Lee los datos del giroscopio (velocidad angular en los ejes X, Y, Z)
    gyro = mpu.read_gyro_data()
    gx, gy = gyro["x"], gyro["y"] # Obtiene valores de los ejes X e Y

    # Aplica zona muerta para ignorar ruido del sensor (pequeñas variaciones no intencionales)
    if abs(gx) < gyro_deadzone: gx = 0 # Si el valor es muy pequeño, lo considera 0
    if abs(gy) < gyro_deadzone: gy = 0 # Si el valor es muy pequeño, lo considera 0

    # Calcula la posición de la mira aplicando sensibilidad y limitando al área de pantalla
    # El eje Y del giroscopio controla la posición horizontal (X) de la mira
    # min() limita el valor máximo para que no se salga de la pantalla
    player.x = int(min(abs(gy)*gyro_sensitivity,119)) + 2 # Rango: 2-121 píxeles (deja margen)
    # El eje X del giroscopio controla la posición vertical (Y) de la mira
    player.y = int(min(abs(gx)*gyro_sensitivity,47)) + 2 # Rango: 2-49 píxeles (deja margen)

    # Lee los datos del acelerómetro (aceleración en los ejes X, Y, Z)
    accel = mpu.read_accel_data()
    ax, ay, az = accel["x"], accel["y"], accel["z"] # Obtiene valores de los tres ejes

    # Calcula la magnitud del vector de aceleración usando el teorema de Pitágoras en 3D
    # magnitude = √(ax² + ay² + az²)
    magnitude = math.sqrt(ax**2+ay**2+az**2)

    # Si la magnitud es mayor a 1.3 (movimiento rápido/brusco del ESP32)
    if magnitude > 1.3:
        # Dibuja la mira mejorada con mayor precisión
        render_item(player.x - 2, player.y - 2, qaim)
        gyro_sensitivity = 1.0 # Aumenta la sensibilidad para movimientos más amplios
    else:
        # Dibuja la mira normal para movimientos suaves
        render_item(player.x - 2, player.y - 2, aim)
        gyro_sensitivity = 0.5 # Sensibilidad normal

# Función para dibujar todos los búnkers activos en pantalla
def display_bunkers():
    # Los búnkers destruidos están en la lista 'eliminated' y no se dibujan

    global bunkers, eliminated # Variables globales de búnkers y eliminados
    
    # Itera sobre todos los búnkers del juego
    for bnkr in bunkers:
        # Verifica si el carril del búnker no está en la lista de eliminados
        if not bnkr.rail in eliminated:
            # Dibuja el búnker en su posición (x, y)
            render_item(bnkr.x, bnkr.y, bunker)

# Función para dibujar y mover los enemigos en pantalla
def display_enemies():
    # Los enemigos se mueven aleatoriamente hacia abajo
    # Si un enemigo llega a la posición Y=55 (búnkers), destruye el búnker correspondiente

    global enemies, eliminated # Variables globales de enemigos y eliminados
    
    # Itera sobre todos los enemigos del juego
    for enm in enemies:
        # Si el carril del enemigo está en la lista de eliminados, lo salta (búnker destruido)
        if enm.rail in eliminated:
            continue # Continúa con el siguiente enemigo

        # Dibuja el enemigo en su posición actual (x, y)
        render_item(enm.x, enm.y, enemy)
        
        # Selecciona un enemigo al azar para moverlo (genera variedad en el movimiento)
        idx = random.randint(0,8) # Índice aleatorio entre 0 y 8 (9 enemigos)
        # Verifica que el enemigo seleccionado no esté en la lista de eliminados
        if not enemies[idx].rail in eliminated:
            # Mueve el enemigo hacia abajo una cantidad aleatoria de píxeles (1-3)
            enemies[idx].y += random.randint(1,3)

            # Verifica si el enemigo llegó a la posición de los búnkers (y >= 55)
            if enemies[idx].y >= 55:
                # Agrega el carril del enemigo a la lista de eliminados (búnker destruido)
                eliminated.append(enemies[idx].rail)

# Función para mostrar la pantalla de fin de juego
def game_over():
    # Detiene el bucle principal del juego cambiando la bandera 'playing' a False

    global oled, playing, points # Variables globales necesarias

    # Muestra mensaje de juego terminado centrado
    oled.text("GAME OVER",34,10) # "GAME OVER" en posición (34, 10)
    oled.text(f"puntuacion: {points}",0,20) # Puntuación final del jugador
    playing = False # Detiene el bucle principal del juego
    time.sleep(2) # Breve pausa para visualizar el mensaje

# Inicialización de los objetos del juego
init_bunkers() # Crea los 9 búnkers defensivos
init_enemies() # Crea los 9 enemigos alienígenas

# Muestra la pantalla de presentación antes de comenzar el juego
presentation()
        
# Bucle principal del juego que se ejecuta mientras 'playing' sea True
while playing:
    # Limpia la pantalla OLED para el nuevo frame
    oled.fill(0)
    
    # Verifica la condición de fin de juego (todos los búnkers destruidos)
    if len(eliminated) == 9:
        game_over() # Muestra pantalla de GAME OVER
    else:
        # Si el juego continúa, ejecuta la lógica principal
        display_bunkers() # Dibuja los búnkers activos
        display_enemies() # Dibuja y mueve los enemigos
        handle_aim() # Lee el giroscopio y dibuja la mira

    # Actualiza la pantalla OLED con todos los elementos dibujados
    oled.show()
    
    # Pausa de 50ms entre frames (aproximadamente 20 FPS)
    time.sleep(0.05)