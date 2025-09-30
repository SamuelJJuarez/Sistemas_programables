# Integrantes:
# Samuel Jafet Juárez Baliño
# Iván Alejandro Cadena López

# Objetivo: Desarrollar un videojuego estilo Space Invaders para ESP32 llamado "Los Bunkers" donde el jugador
# debe defender la Tierra de invasores alienígenas. El juego utiliza un giroscopio MPU6050 o un joystick analógico
# para controlar la mira mediante movimientos físicos, un botón para disparar, y una pantalla OLED para visualizar el juego.
# El jugador puede alternar entre control por giroscopio o joystick presionando el botón SW del joystick.

# Se importan las clases Pin, SoftI2C y ADC del módulo machine. Pin se usa para controlar los pines GPIO,
# SoftI2C implementa el protocolo de comunicación I2C por software, y ADC permite leer señales analógicas
from machine import Pin, SoftI2C, ADC
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

# Configuración del joystick analógico (ejes X e Y)
joystick_x = ADC(Pin(34)) # Eje X del joystick conectado al GPIO34
joystick_x.atten(ADC.ATTN_11DB) # Configura atenuación para rango 0-3.3V
joystick_x.width(ADC.WIDTH_12BIT) # Resolución de 12 bits (valores 0-4095)

joystick_y = ADC(Pin(35)) # Eje Y del joystick conectado al GPIO35
joystick_y.atten(ADC.ATTN_11DB) # Configura atenuación para rango 0-3.3V
joystick_y.width(ADC.WIDTH_12BIT) # Resolución de 12 bits (valores 0-4095)

# Botón del joystick (SW) para cambiar modo de control
joystick_button = Pin(32, Pin.IN, Pin.PULL_UP) # Botón SW del joystick en GPIO32

# Función de interrupción que se ejecuta cuando el jugador presiona el botón para disparar
def handle_shoot(pin):
    """
    Maneja el evento de disparo del jugador
    Verifica colisiones entre la mira del jugador y los enemigos
    Si hay colisión, incrementa puntos y resetea la posición del enemigo
    """
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

# Configura la interrupción del botón de disparo para que se active en el flanco descendente (cuando se presiona)
button.irq(trigger=Pin.IRQ_FALLING, handler=handle_shoot)

# Función para manejar el cambio de modo de control (giroscopio ↔ joystick)
def handle_mode_change(pin):
    """
    Cambia el modo de control entre giroscopio y joystick
    Se ejecuta cuando el usuario presiona el botón SW del joystick
    Incluye debouncing para evitar múltiples cambios por rebotes mecánicos
    """
    global control_mode, last_button_time
    
    # Obtiene el tiempo actual en milisegundos
    current_time = time.ticks_ms()
    
    # Verifica que hayan pasado al menos 300ms desde el último cambio (debouncing)
    if time.ticks_diff(current_time, last_button_time) > 300:
        # Alterna entre los dos modos de control
        if control_mode == "gyro":
            control_mode = "joystick"
            print("Modo cambiado a: JOYSTICK")
        else:
            control_mode = "gyro"
            print("Modo cambiado a: GIROSCOPIO")
        
        # Actualiza el timestamp del último cambio
        last_button_time = current_time

# Configura la interrupción del botón del joystick para cambiar de modo
joystick_button.irq(trigger=Pin.IRQ_FALLING, handler=handle_mode_change)

# Parámetros de configuración del giroscopio para el control de la mira
gyro_sensitivity = 0.5  # Sensibilidad del giroscopio (0.5 = normal, 1.0 = rápida)
gyro_deadzone = 0.02    # Zona muerta para evitar drift (movimiento no intencional por ruido del sensor)

# Variables de control del modo de entrada
control_mode = "gyro"  # Modo de control: "gyro" para giroscopio, "joystick" para joystick analógico
last_button_time = 0   # Timestamp del último cambio de modo (para evitar rebotes del botón)

# Variables globales del juego
player = Aim(0,0) # Objeto de la mira del jugador inicializado en posición (0,0)
playing = True # Bandera que controla si el juego está activo
bunkers = [] # Lista que almacenará todos los búnkers defensivos del juego
enemies = [] # Lista que almacenará todos los enemigos alienígenas del juego
points = 0 # Contador de puntos del jugador
eliminated = [] # Lista que almacena los rails (carriles) de búnkers destruidos

# Función para mostrar la pantalla de presentación del juego
def presentation():
    """
    Muestra las pantallas iniciales del juego:
    - Título y créditos de los desarrolladores
    - Historia del juego
    - Mensaje de preparación
    """
    global oled # Variable global de la pantalla OLED
    
    # Pantalla 1: Título y créditos
    oled.fill(0) # Limpia la pantalla
    oled.text("Los bunkers",19,0) # Título del juego centrado
    oled.text("Integrantes:",0,10) # Etiqueta de integrantes
    oled.text("Ivan A. Cadena",0,20) # Primer integrante
    oled.text("Samuel J. Juarez",0,30) # Segundo integrante
    oled.show() # Actualiza la pantalla
    time.sleep(3) # Pausa para visualizar

    # Pantalla 2: Historia del juego
    oled.fill(0) # Limpia la pantalla
    oled.text("Historia:",0,0) # Título de la sección
    oled.text("Los aliens invad",0,10) # "Los aliens invaden"
    oled.text("en la tierra y t",0,20) # "en la tierra y tu"
    oled.text("u objetivo es de",0,30) # "tu objetivo es de-"
    oled.text("tenerlos usando",0,40)  # "tenerlos usando"
    oled.text("el space shooter",0,50) # "el space shooter"
    oled.show() # Actualiza la pantalla
    time.sleep(3) # Pausa para leer la historia

    # Pantalla 3: Instrucciones de control
    oled.fill(0) # Limpia la pantalla
    oled.text("Controles:",0,0)
    oled.text("Boton SW: Cambiar",0,10)
    oled.text("modo control",0,20)
    oled.text("Gyro/Joystick",0,30)
    oled.text("Boton: Disparar",0,40)
    oled.show()
    time.sleep(3)

    # Pantalla 4: Mensaje de preparación
    oled.fill(0) # Limpia la pantalla
    oled.text("preparado?...",11,0) # Mensaje centrado
    oled.show() # Actualiza la pantalla
    time.sleep(2) # Pausa breve antes de comenzar

# Función para inicializar los búnkers defensivos en sus posiciones
def init_bunkers():
    """
    Crea 9 búnkers distribuidos uniformemente en la parte inferior de la pantalla
    Cada búnker se coloca en un carril específico (1-9) con separación de 14 píxeles
    """
    cont = 1 # Contador para asignar número de carril a cada búnker
    for field in range(0,127,14):
        bunkers.append(Bunker(cont,field+7,55))
        cont += 1

# Función para inicializar los enemigos alienígenas en sus posiciones iniciales
def init_enemies():
    """
    Crea 9 enemigos distribuidos uniformemente en la parte superior de la pantalla
    Cada enemigo se coloca en un carril específico (1-9) con separación de 14 píxeles
    """
    cont = 1 # Contador para asignar número de carril a cada enemigo
    for field in range(0,127,14):
        enemies.append(Enemy(cont,field+7,0))
        cont += 1

# Función para renderizar/dibujar un sprite (matriz de píxeles) en la pantalla OLED
def render_item(x, y, item):
    """
    Dibuja un sprite en la pantalla OLED píxel por píxel
    x, y: coordenadas de inicio donde dibujar el sprite
    item: matriz bidimensional que representa el sprite (8x8 píxeles)
    """
    global oled
    
    for row in item:
        for pixel in row:
            oled.pixel(x,y,pixel)
            x += 1
        x -= len(row)
        y += 1

# Función para leer y procesar los valores del joystick analógico
def read_joystick():
    """
    Lee los valores analógicos del joystick y los convierte a coordenadas de pantalla
    Aplica calibración considerando el punto central del joystick (aproximadamente 2048)
    Implementa zona muerta para evitar movimiento no intencional
    Retorna: tupla (x, y) con las coordenadas calculadas
    """
    # Lee los valores ADC de ambos ejes (0-4095)
    x_raw = joystick_x.read()
    y_raw = joystick_y.read()
    
    # Define el punto central del joystick (en reposo, aproximadamente 2048)
    center = 2048
    # Define la zona muerta (valores cercanos al centro se ignoran)
    deadzone = 200
    
    # Calcula la desviación respecto al centro
    x_diff = x_raw - center
    y_diff = y_raw - center
    
    # Aplica zona muerta: si la desviación es menor al deadzone, se considera 0
    if abs(x_diff) < deadzone:
        x_diff = 0
    if abs(y_diff) < deadzone:
        y_diff = 0
    
    # Mapea los valores del joystick a coordenadas de pantalla
    if x_diff != 0:
        x_pos = int(((x_diff + 2048) / 4096) * 119) + 2
    else:
        x_pos = 61  # Centro horizontal
    
    if y_diff != 0:
        y_pos = int(((y_diff + 2048) / 4096) * 47) + 2
    else:
        y_pos = 26  # Centro vertical
    
    # Limita las coordenadas
    x_pos = max(2, min(121, x_pos))
    y_pos = max(2, min(49, y_pos))
    
    return x_pos, y_pos

# Función para manejar el movimiento de la mira según el modo de control activo
def handle_aim():
    """
    Controla la mira del jugador según el modo activo (giroscopio o joystick)
    - Modo giroscopio: Lee MPU6050 y usa inclinación del ESP32
    - Modo joystick: Lee valores analógicos del joystick
    También detecta movimientos rápidos para cambiar tipo de mira
    """
    global mpu, player, gyro_deadzone, gyro_sensitivity, control_mode
    
    if control_mode == "gyro":
        # ===== MODO GIROSCOPIO =====
        gyro = mpu.read_gyro_data()
        gx, gy = gyro["x"], gyro["y"]

        # Zona muerta
        if abs(gx) < gyro_deadzone: gx = 0
        if abs(gy) < gyro_deadzone: gy = 0

        # Calcula posición
        player.x = int(min(abs(gy)*gyro_sensitivity,119)) + 2
        player.y = int(min(abs(gx)*gyro_sensitivity,47)) + 2
        
    else:
        # ===== MODO JOYSTICK =====
        player.x, player.y = read_joystick()

    # Lee acelerómetro para cambiar tipo de mira (funciona en ambos modos)
    accel = mpu.read_accel_data()
    ax, ay, az = accel["x"], accel["y"], accel["z"]
    magnitude = math.sqrt(ax**2+ay**2+az**2)

    if magnitude > 1.3:
        render_item(player.x - 2, player.y - 2, qaim)
        if control_mode == "gyro":
            gyro_sensitivity = 1.0
    else:
        render_item(player.x - 2, player.y - 2, aim)
        if control_mode == "gyro":
            gyro_sensitivity = 0.5

# Función para dibujar todos los búnkers activos
def display_bunkers():
    """
    Renderiza todos los búnkers que no han sido destruidos
    """
    global bunkers, eliminated
    
    for bnkr in bunkers:
        if not bnkr.rail in eliminated:
            render_item(bnkr.x, bnkr.y, bunker)

# Función para dibujar y mover los enemigos
def display_enemies():
    """
    Renderiza todos los enemigos activos y controla su movimiento descendente
    """
    global enemies, eliminated
    
    for enm in enemies:
        if enm.rail in eliminated:
            continue

        render_item(enm.x, enm.y, enemy)
        
        idx = random.randint(0,8)
        if not enemies[idx].rail in eliminated:
            enemies[idx].y += random.randint(1,3)

            if enemies[idx].y >= 55:
                eliminated.append(enemies[idx].rail)

# Función para mostrar pantalla de game over
def game_over():
    """
    Muestra el mensaje de GAME OVER y la puntuación final
    """
    global oled, playing, points

    oled.text("GAME OVER",34,10)
    oled.text(f"puntuacion: {points}",0,20)
    playing = False
    time.sleep(3)

# Inicialización
init_bunkers()
init_enemies()
presentation()
        
# Bucle principal del juego
while playing:
    oled.fill(0)
    
    if len(eliminated) == 9:
        game_over()
    else:
        display_bunkers()
        display_enemies()
        handle_aim()

    oled.show()
    time.sleep(0.05)