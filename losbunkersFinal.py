# Integrantes:
# Samuel Jafet Juárez Baliño
# Iván Alejandro Cadena López

# Fecha: 30/09/2025

# Objetivo: Desarrollar un videojuego estilo Space Invaders para ESP32 llamado "Los Bunkers" donde el jugador
# debe defender el planeta de invasores alienígenas. El juego utiliza un giroscopio MPU6050 o un joystick analógico
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
mpu = MPU6050() # Instancia del sensor MPU6050

# Configuración del joystick analógico (ejes x, y)
joystick_x = ADC(Pin(34)) # Eje x del joystick conectado al GPIO34
joystick_x.atten(ADC.ATTN_11DB) # Configura atenuación para rango 0-3.3V
joystick_x.width(ADC.WIDTH_12BIT) # Resolución de 12 bits (valores 0-4095)

joystick_y = ADC(Pin(35)) # Eje y del joystick conectado al GPIO35
joystick_y.atten(ADC.ATTN_11DB) # Configura atenuación para rango 0-3.3V
joystick_y.width(ADC.WIDTH_12BIT) # Resolución de 12 bits (valores 0-4095)

# Botón del joystick (SW) para cambiar modo de control
joystick_button = Pin(32, Pin.IN, Pin.PULL_UP) # Botón SW del joystick en GPIO32

# Función de interrupción que se ejecuta cuando el jugador presiona el botón para disparar
def handle_shoot(pin):
    # Maneja el evento de disparo del jugador
    # Si hay colisión, incrementa puntos, genera nuevo enemigo y solo resetea el enemigo impactado
    global enemies, points, player, eliminated, kills_count
    
    # Calcula el tamaño de la mira según si está en modo rápido
    aim_size = 8 if not quick_move_active else 12
    
    # Itera sobre todos los enemigos activos en pantalla
    for enemy in enemies:
        # Verifica colisión considerando el tamaño dinámico de la mira
        if (player.x > enemy.x - aim_size//2 and player.x < (enemy.x + 8 + aim_size//2)) and \
           (player.y > enemy.y - aim_size//2 and player.y < (enemy.y + 8 + aim_size//2)):
            points += 1
            kills_count += 1
            # Solo resetea este enemigo específico a posición inicial más abajo
            enemy.y = -5  # Posición negativa para que aparezca gradualmente
            spawn_new_enemy()  # Genera uno nuevo
            break

# Configura la interrupción del botón de disparo
button.irq(trigger=Pin.IRQ_FALLING, handler=handle_shoot)

# Función para manejar el cambio de modo de control (giroscopio o joystick)
def handle_mode_change(pin):
    # Cambia el modo de control entre giroscopio y joystick
    # Incluye validación para evitar múltiples cambios
    global control_mode, last_button_time
    
    current_time = time.ticks_ms() # Tiempo actual en milisegundos

    # Cambia modo solo si han pasado más de 300 ms desde el último cambio
    if time.ticks_diff(current_time, last_button_time) > 300:
        # Alterna entre modos
        if control_mode == "gyro": 
            control_mode = "joystick"
            print("Modo cambiado a: JOYSTICK")
        else:
            control_mode = "gyro"
            print("Modo cambiado a: GIROSCOPIO")
        
        last_button_time = current_time # Actualiza el tiempo del último cambio

# Configura la interrupción del botón del joystick
joystick_button.irq(trigger=Pin.IRQ_FALLING, handler=handle_mode_change)

# Parámetros de configuración del giroscopio
gyro_sensitivity = 3  # Factor de movimiento por lectura del giroscopio
gyro_deadzone = 0.08    # Zona muerta para evitar drift del giroscopio

# Variables de control del modo de entrada
control_mode = "gyro"  # Modo de control inicial
last_button_time = 0   # Timestamp del último cambio de modo
quick_move_active = False  # Bandera para detectar movimiento rápido y agrandar mira

# Variables globales del juego
player = Aim(61, 26) # Mira inicializada en el centro de la pantalla
playing = True # Bandera que controla si el juego está activo
bunkers = [] # Lista de búnkers defensivos
enemies = [] # Lista de enemigos alienígenas
points = 0 # Contador de puntos
eliminated = [] # Lista de carriles con búnkers destruidos
kills_count = 0 # Contador de enemigos eliminados 
enemy_speed_base = 1 # Velocidad base de los enemigos
game_over_state = False # Bandera para el estado de game over
restart_requested = False # Bandera para solicitud de reinicio

# Función para generar un nuevo enemigo en un carril aleatorio válido
def spawn_new_enemy():
    # Genera un nuevo enemigo en un carril aleatorio que no esté eliminado
    # Los enemigos nuevos aparecen fuera de pantalla (y=-20) para una entrada gradual
    global enemies, eliminated
    
    # Obtiene lista de carriles disponibles
    available_rails = [i for i in range(1, 10) if i not in eliminated]
    
    # Si hay carriles disponibles, genera enemigo
    if available_rails:
        rail = random.choice(available_rails)
        x_pos = (rail - 1) * 14 + 7
        
        # Crea nuevo enemigo fuera de pantalla y lo añade a la lista
        enemies.append(Enemy(rail, x_pos, -20))

# Función para calcular la velocidad del enemigo según las muertes acumuladas
def get_enemy_speed():
    # La velocidad aumenta progresivamente cada 5 enemigos eliminados
    # Fórmula: velocidad = 1 + (kills // 5) * 0.5
    # Ejemplos: 0-4 kills = velocidad 1, 5-9 kills = velocidad 1.5, 10-14 = velocidad 2
    return 1 + (kills_count // 5) * 0.5

# Función para mostrar la pantalla de presentación del juego
def presentation():
    global oled
    
    # Pantalla 1: Título y créditos
    oled.fill(0)
    oled.text("Los bunkers",19,0)
    oled.text("Integrantes:",0,10)
    oled.text("Ivan A. Cadena",0,20)
    oled.text("Samuel J. Juarez",0,30)
    oled.text("1/10/2025",0,40)
    oled.show()
    time.sleep(3)

    # Pantalla 2: Historia del juego
    oled.fill(0)
    oled.text("Historia:",0,0)
    oled.text("Los aliens invad",0,10)
    oled.text("en la tierra y t",0,20)
    oled.text("u objetivo es de",0,30)
    oled.text("tenerlos usando",0,40)
    oled.text("el space shooter",0,50)
    oled.show()
    time.sleep(3)

    # Pantalla 3: Instrucciones
    oled.fill(0)
    oled.text("Controles:",0,0)
    oled.text("Boton SW: Cambiar",0,10)
    oled.text("modo control",0,20)
    oled.text("Gyro/Joystick",0,30)
    oled.text("Boton: Disparar",0,40)
    oled.show()
    time.sleep(3)

    # Pantalla 4: Entrada al juego
    oled.fill(0)
    oled.text("preparado?...",11,0)
    oled.show()
    time.sleep(2)

# Función para inicializar los búnkers defensivos
def init_bunkers():
    # Crea 9 búnkers distribuidos uniformemente en la parte inferior
    cont = 1
    for field in range(0,127,14):
        bunkers.append(Bunker(cont,field+7,55))
        cont += 1

# Función para inicializar los enemigos alienígenas
def init_enemies():
    # Crea 9 enemigos distribuidos uniformemente en la parte superior
    cont = 1
    for field in range(0,127,14):
        enemies.append(Enemy(cont,field+7,0))
        cont += 1

# Función para reiniciar el juego completamente
def reset_game():
    # Permite al jugador comenzar una nueva partida
    global bunkers, enemies, points, eliminated, playing, game_over_state
    global kills_count, restart_requested, player
    
    # Limpia todas las listas
    bunkers.clear()
    enemies.clear()
    eliminated.clear()
    
    # Resetea variables
    points = 0
    kills_count = 0
    playing = True
    game_over_state = False
    restart_requested = False
    player.x = 61
    player.y = 26
    
    # Reinicializa búnkers y enemigos
    init_bunkers()
    init_enemies()
    
    print("Juego reiniciado")

# Función para renderizar sprites en pantalla
def render_item(x, y, item):
    global oled
    
    # Dibuja un ítem (matriz) en las coordenadas (x,y)
    for row in item:
        # Dibuja cada fila de la matriz
        for pixel in row:
            # Dibuja cada píxel de la fila
            oled.pixel(x,y,pixel)
            x += 1 # Avanza al siguiente píxel en x
        x -= len(row) # Regresa al inicio de la fila
        y += 1 # Baja a la siguiente fila

# Función para aumentar el tamaño de una matriz
def aumentar_matriz(matriz, factor):
    # matriz: matriz bidimensional original
    # factor: número de veces que se repetirá cada píxel
    # Retorna: matriz ampliada

    # Si el factor es menor que 1, no se aumenta
    if factor < 1:
        return matriz
    
    nuevo_icono = [] # Nueva matriz aumentada
    
    # Repite cada fila y cada columna según el factor
    for fila in matriz:
        nueva_fila = []
        # Repite cada píxel en la fila
        for c in fila:
            nueva_fila.extend([c] * factor)
        for _ in range(factor): # Repite la fila completa
            nuevo_icono.append(nueva_fila)
    
    return nuevo_icono # Retorna la matriz aumentada

# Función para leer el joystick analógico
def read_joystick():
    global player
    
    x_raw = joystick_x.read()
    y_raw = joystick_y.read()
    
    center = 2048 # Valor central del joystick
    deadzone = 300  # Zona muerta 
    
    x_diff = x_raw - center # Diferencia desde el centro
    y_diff = y_raw - center # Diferencia desde el centro
    
    # Movimiento incremental: solo se mueve si está fuera de zona muerta
    move_speed = 2  # Velocidad de movimiento del jugador
    
    if abs(x_diff) > deadzone:
        # Mueve hacia la dirección del joystick
        if x_diff > 0:
            player.x = min(121, player.x + move_speed)
        else:
            player.x = max(2, player.x - move_speed)
    
    if abs(y_diff) > deadzone:
        if y_diff > 0:
            player.y = min(49, player.y + move_speed)
        else:
            player.y = max(2, player.y - move_speed)
    
    return player.x, player.y

# Función para manejar el movimiento de la mira
def handle_aim():
    # Detecta movimientos rápidos para agrandar la mira y aumentar área de impacto
    global mpu, player, gyro_deadzone, gyro_sensitivity, control_mode, quick_move_active
    
    if control_mode == "gyro":
        # Modo giroscopio con movimiento incremental controlado
        gyro = mpu.read_gyro_data()
        gx, gy = gyro["x"], gyro["y"]

        # Zona muerta para evitar drift
        if abs(gx) < gyro_deadzone: gx = 0
        if abs(gy) < gyro_deadzone: gy = 0

        # Movimiento incremental con velocidad fija
        if gy != 0:
            # Movimiento horizontal
            if gy > 0:
                player.x = min(121, player.x + gyro_sensitivity)
            else:
                player.x = max(2, player.x - gyro_sensitivity)
        
        if gx != 0:
            # Movimiento vertical
            if gx > 0:
                player.y = min(49, player.y + gyro_sensitivity)
            else:
                player.y = max(2, player.y - gyro_sensitivity)
        
        # Lee acelerómetro para detectar movimiento rápido y agrandar mira
        accel = mpu.read_accel_data()
        ax, ay, az = accel["x"], accel["y"], accel["z"]
        magnitude = math.sqrt(ax**2+ay**2+az**2)

        # Si detecta movimiento rápido, agranda la mira
        if magnitude > 1.3:
            quick_move_active = True
            # Mira agrandada para cubrir más área
            aim_large = aumentar_matriz(qaim, 3)  
            render_item(player.x - 6, player.y - 6, aim_large)
        else:
            quick_move_active = False
            # Mira normal
            render_item(player.x - 4, player.y - 4, aim) 
    else:
        # Modo joystick
        player.x, player.y = read_joystick()

    

# Función para dibujar búnkers activos
def display_bunkers():
    global bunkers, eliminated
    # Dibuja todos los búnkers que no han sido eliminados
    for bnkr in bunkers: 
        if not bnkr.rail in eliminated: # Solo dibuja si no está eliminado
            render_item(bnkr.x, bnkr.y, bunker)

# Función para dibujar y mover enemigos
def display_enemies():
    global enemies, eliminated
    
    current_speed = get_enemy_speed() # Obtiene velocidad actual según dificultad
    # Dibuja todos los enemigos que no han sido eliminados
    for enm in enemies: 
        if enm.rail in eliminated: # Si el carril está eliminado, no dibuja
            continue

        render_item(enm.x, enm.y, enemy)
    
    # Solo mueve un enemigo aleatorio cada frame
    idx = random.randint(0, len(enemies)-1)
    if not enemies[idx].rail in eliminated: # Solo mueve si no está eliminado
        # Aplica velocidad progresiva
        movement = int(random.randint(1,2) * current_speed)
        enemies[idx].y += movement # Mueve el enemigo seleccionado

        if enemies[idx].y >= 55: # Si llega a la línea de búnkers
            # Elimina el búnker en ese carril
            eliminated.append(enemies[idx].rail)

# Función para mostrar pantalla de game over con opción de reinicio
def game_over():
    global oled, playing, points, game_over_state, restart_requested
    
    game_over_state = True # Activa estado de game over
    
    # Muestra mensaje de game over
    oled.fill(0) # Limpia pantalla
    oled.text("GAME OVER",34,10)
    oled.text(f"Puntos: {points}",25,25)
    oled.text("Presiona boton",15,40)
    oled.text("para reintentar",15,50)
    oled.show() # Actualiza pantalla
    
    # Espera a que se presione el botón para reiniciar
    while game_over_state:
        if button.value() == 0:  # Botón presionado (pull-up, por eso es 0)
            time.sleep(0.3)  # Debouncing
            reset_game()  # Reinicia el juego
            break
        time.sleep(0.1)

# Inicialización del juego
init_bunkers() # Crea búnkers
init_enemies() # Crea enemigos
presentation() # Muestra presentación
        
# Bucle principal del juego
while True:
    if playing: # Si el juego está activo
        # Limpia pantalla cada frame
        oled.fill(0)
        
        # Verifica condición de game over
        if len(eliminated) == 9: # Si se eliminaron todos los búnkers
            game_over() # Muestra pantalla de game over
        else: 
            # Juego activo
            display_bunkers() # Dibuja búnkers
            display_enemies() # Dibuja y mueve enemigos
            handle_aim() # Maneja y dibuja la mira del jugador
            
            # Muestra puntuación en esquina
            oled.text(f"P:{points}", 0, 0)

        oled.show() # Actualiza pantalla
        time.sleep(0.05)
    else:
        # Si el juego terminó, espera reinicio
        time.sleep(0.1)