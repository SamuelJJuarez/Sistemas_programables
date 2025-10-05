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
    Si hay colisión, incrementa puntos, resetea el enemigo y genera uno nuevo
    """
    global enemies, points, player, eliminated, kills_count
    
    # Itera sobre todos los enemigos activos en pantalla
    for enemy in enemies:
        # Verifica colisión usando el punto pivote de la mira
        if (player.x > enemy.x and player.x < (enemy.x + 8)) and player.y > enemy.y and player.y < (enemy.y + 8):
            points += 1 # Incrementa la puntuación
            kills_count += 1 # Incrementa contador de muertes para dificultad
            spawn_new_enemy() # Genera un nuevo enemigo en carril aleatorio
            enemy.y = 0 # Resetea posición del enemigo actual
            break
        
        # Verifica colisión usando el punto del borde derecho de la mira
        if (player.x+4 > enemy.x and player.x+4 < (enemy.x + 8)) and player.y+4 > enemy.y and player.y+4 < (enemy.y + 8):
            points += 1
            kills_count += 1
            spawn_new_enemy()
            enemy.y = 0
            break

# Configura la interrupción del botón de disparo
button.irq(trigger=Pin.IRQ_FALLING, handler=handle_shoot)

# Función para manejar el cambio de modo de control (giroscopio ↔ joystick)
def handle_mode_change(pin):
    """
    Cambia el modo de control entre giroscopio y joystick
    Incluye debouncing para evitar múltiples cambios
    """
    global control_mode, last_button_time
    
    current_time = time.ticks_ms()
    
    if time.ticks_diff(current_time, last_button_time) > 300:
        if control_mode == "gyro":
            control_mode = "joystick"
            print("Modo cambiado a: JOYSTICK")
        else:
            control_mode = "gyro"
            print("Modo cambiado a: GIROSCOPIO")
        
        last_button_time = current_time

# Configura la interrupción del botón del joystick
joystick_button.irq(trigger=Pin.IRQ_FALLING, handler=handle_mode_change)

# Parámetros de configuración del giroscopio (sensibilidad reducida para mejor control)
gyro_sensitivity = 0.2  # Reducida de 0.5 a 0.2 para movimiento más suave
gyro_deadzone = 0.05    # Aumentada de 0.02 a 0.05 para mayor estabilidad

# Variables de control del modo de entrada
control_mode = "gyro"  # Modo de control inicial
last_button_time = 0   # Timestamp del último cambio de modo

# Variables globales del juego
player = Aim(61, 26) # Mira inicializada en el centro de la pantalla
playing = True # Bandera que controla si el juego está activo
bunkers = [] # Lista de búnkers defensivos
enemies = [] # Lista de enemigos alienígenas
points = 0 # Contador de puntos
eliminated = [] # Lista de carriles con búnkers destruidos
kills_count = 0 # Contador de enemigos eliminados (para aumentar dificultad)
enemy_speed_base = 1 # Velocidad base de los enemigos
game_over_state = False # Bandera para el estado de game over
restart_requested = False # Bandera para solicitud de reinicio

# Función para generar un nuevo enemigo en un carril aleatorio válido
def spawn_new_enemy():
    """
    Genera un nuevo enemigo en un carril aleatorio que no esté eliminado
    Los enemigos nuevos aparecen en la parte superior (y=0)
    """
    global enemies, eliminated
    
    # Obtiene lista de carriles disponibles (no eliminados)
    available_rails = [i for i in range(1, 10) if i not in eliminated]
    
    # Si hay carriles disponibles, genera enemigo
    if available_rails:
        rail = random.choice(available_rails) # Selecciona carril aleatorio
        x_pos = (rail - 1) * 14 + 7 # Calcula posición X según el carril
        
        # Busca si ya existe un enemigo en ese carril
        for enemy in enemies:
            if enemy.rail == rail:
                enemy.y = 0 # Resetea su posición a la parte superior
                return
        
        # Si no existe, crea uno nuevo
        enemies.append(Enemy(rail, x_pos, 0))

# Función para calcular la velocidad del enemigo según las muertes acumuladas
def get_enemy_speed():
    """
    Calcula la velocidad de movimiento de los enemigos basándose en kills_count
    La velocidad aumenta progresivamente cada 5 enemigos eliminados
    Fórmula: velocidad = 1 + (kills // 5) * 0.5
    Ejemplos: 0-4 kills = velocidad 1, 5-9 kills = velocidad 1.5, 10-14 = velocidad 2
    """
    return 1 + (kills_count // 5) * 0.5

# Función para mostrar la pantalla de presentación del juego
def presentation():
    """
    Muestra las pantallas iniciales del juego
    """
    global oled
    
    # Pantalla 1: Título y créditos
    oled.fill(0)
    oled.text("Los bunkers",19,0)
    oled.text("Integrantes:",0,10)
    oled.text("Ivan A. Cadena",0,20)
    oled.text("Samuel J. Juarez",0,30)
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

    # Pantalla 4: Preparación
    oled.fill(0)
    oled.text("preparado?...",11,0)
    oled.show()
    time.sleep(2)

# Función para inicializar los búnkers defensivos
def init_bunkers():
    """
    Crea 9 búnkers distribuidos uniformemente en la parte inferior
    """
    cont = 1
    for field in range(0,127,14):
        bunkers.append(Bunker(cont,field+7,55))
        cont += 1

# Función para inicializar los enemigos alienígenas
def init_enemies():
    """
    Crea 9 enemigos distribuidos uniformemente en la parte superior
    """
    cont = 1
    for field in range(0,127,14):
        enemies.append(Enemy(cont,field+7,0))
        cont += 1

# Función para reiniciar el juego completamente
def reset_game():
    """
    Reinicia todas las variables y listas del juego a su estado inicial
    Permite al jugador comenzar una nueva partida
    """
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
    """
    Dibuja un sprite píxel por píxel
    """
    global oled
    
    for row in item:
        for pixel in row:
            oled.pixel(x,y,pixel)
            x += 1
        x -= len(row)
        y += 1

# Función para leer el joystick analógico
def read_joystick():
    """
    Lee el joystick y convierte valores a coordenadas de pantalla
    """
    x_raw = joystick_x.read()
    y_raw = joystick_y.read()
    
    center = 2048
    deadzone = 200
    
    x_diff = x_raw - center
    y_diff = y_raw - center
    
    if abs(x_diff) < deadzone:
        x_diff = 0
    if abs(y_diff) < deadzone:
        y_diff = 0
    
    if x_diff != 0:
        x_pos = int(((x_diff + 2048) / 4096) * 119) + 2
    else:
        x_pos = player.x  # Mantiene posición actual si está en zona muerta
    
    if y_diff != 0:
        y_pos = int(((y_diff + 2048) / 4096) * 47) + 2
    else:
        y_pos = player.y  # Mantiene posición actual
    
    x_pos = max(2, min(121, x_pos))
    y_pos = max(2, min(49, y_pos))
    
    return x_pos, y_pos

# Función para manejar el movimiento de la mira
def handle_aim():
    """
    Controla la mira según el modo activo
    """
    global mpu, player, gyro_deadzone, gyro_sensitivity, control_mode
    
    if control_mode == "gyro":
        # Modo giroscopio con sensibilidad ajustada
        gyro = mpu.read_gyro_data()
        gx, gy = gyro["x"], gyro["y"]

        if abs(gx) < gyro_deadzone: gx = 0
        if abs(gy) < gyro_deadzone: gy = 0

        # Actualiza posición con límites
        new_x = player.x + int(gy * gyro_sensitivity * 10)
        new_y = player.y + int(gx * gyro_sensitivity * 10)
        
        player.x = max(2, min(121, new_x))
        player.y = max(2, min(49, new_y))
        
    else:
        # Modo joystick
        player.x, player.y = read_joystick()

    # Acelerómetro para cambiar mira
    accel = mpu.read_accel_data()
    ax, ay, az = accel["x"], accel["y"], accel["z"]
    magnitude = math.sqrt(ax**2+ay**2+az**2)

    if magnitude > 1.3:
        render_item(player.x - 4, player.y - 4, qaim)
    else:
        render_item(player.x - 4, player.y - 4, aim)

# Función para dibujar búnkers activos
def display_bunkers():
    """
    Renderiza búnkers no destruidos
    """
    global bunkers, eliminated
    
    for bnkr in bunkers:
        if not bnkr.rail in eliminated:
            render_item(bnkr.x, bnkr.y, bunker)

# Función para dibujar y mover enemigos
def display_enemies():
    """
    Renderiza enemigos y controla su movimiento con velocidad progresiva
    """
    global enemies, eliminated
    
    current_speed = get_enemy_speed() # Obtiene velocidad actual según dificultad
    
    for enm in enemies:
        if enm.rail in eliminated:
            continue

        render_item(enm.x, enm.y, enemy)
    
    # Movimiento más controlado de enemigos
    # Solo mueve un enemigo aleatorio cada frame (velocidad reducida)
    idx = random.randint(0, len(enemies)-1)
    if not enemies[idx].rail in eliminated:
        # Aplica velocidad progresiva
        movement = int(random.randint(1,2) * current_speed)
        enemies[idx].y += movement

        if enemies[idx].y >= 55:
            eliminated.append(enemies[idx].rail)

# Función para mostrar pantalla de game over con opción de reinicio
def game_over():
    """
    Muestra pantalla de GAME OVER y espera a que el jugador presione para reintentar
    """
    global oled, playing, points, game_over_state, restart_requested
    
    game_over_state = True
    
    # Muestra mensaje de game over
    oled.fill(0)
    oled.text("GAME OVER",34,10)
    oled.text(f"Puntos: {points}",25,25)
    oled.text("Presiona boton",15,40)
    oled.text("para reintentar",15,50)
    oled.show()
    
    # Espera a que se presione el botón para reiniciar
    while game_over_state:
        if button.value() == 0:  # Botón presionado (pull-up, por eso es 0)
            time.sleep(0.3)  # Debouncing
            reset_game()  # Reinicia el juego
            break
        time.sleep(0.1)

# Inicialización del juego
init_bunkers()
init_enemies()
presentation()
        
# Bucle principal del juego
while True:
    if playing:
        oled.fill(0)
        
        # Verifica condición de game over
        if len(eliminated) == 9:
            game_over()
        else:
            # Juego activo
            display_bunkers()
            display_enemies()
            handle_aim()
            
            # Muestra puntuación en esquina
            oled.text(f"P:{points}", 0, 0)

        oled.show()
        time.sleep(0.05)
    else:
        # Si el juego terminó, espera reinicio
        time.sleep(0.1)