ffrom machine import Pin, SoftI2C
from MPU6050 import MPU6050
from ssd1306 import SSD1306_I2C
from game_assets import enemy, qaim, aim, bunker, Aim, Enemy, Bunker
import time, random, math

#configuracion del oled
i2c = SoftI2C(scl=Pin(18), sda=Pin(19))
oled = SSD1306_I2C(128, 64, i2c)

#pines de entrada
button = Pin(16, Pin.IN, Pin.PULL_UP)
mpu = MPU6050()

#interrupcion de boton
def handle_shoot(pin):
    global enemies, points, player
    #iterar sobre los enemigos
    for enemy in enemies:
        #verificar colision de punto pivote
        if (player.x > enemy.x and player.x < (enemy.x + 8)) and player.y > enemy.y and player.y < (enemy.y + 8):
            points += 1
            enemy.y = 0
            break
        #verificar colision de punto borde
        if (player.x+4 > enemy.x and player.x+4 < (enemy.x + 8)) and player.y+4 > enemy.y and player.y+4 < (enemy.y + 8):
            points += 1
            enemy.y = 0
            break


button.irq(trigger=Pin.IRQ_FALLING, handler=handle_shoot)

#parametros de giroscopio
gyro_sensitivity = 0.5  # Ajusta la sensibilidad
gyro_deadzone = 0.02    # Zona muerta para evitar drift

#objetos de juego
player = Aim(0,0)
playing = True
bunkers = []
enemies = []
points = 0
eliminated = []

def presentation():
    global oled
    
    #limpiar la pantalla
    oled.fill(0)

    #texto de titulo
    oled.text("Los bunkers",19,0)
    oled.text("Integrantes:",0,10)
    oled.text("Ivan A. Cadena",0,20)
    oled.text("Samuel J. Juarez",0,30)
    #mostrar pantalla
    oled.show()
    time.sleep(0.1)

    #historia del juego
    oled.fill(0)
    oled.text("Historia:",0,0)
    oled.text("Los aliens invad",0,10)
    oled.text("en la tierra y t",0,20)
    oled.text("u objetivo es de",0,30)
    oled.text("tenerlos usando",0,40)
    oled.text("el space shooter",0,50)
    #ostrar por pantalla
    oled.show()
    time.sleep(0.2)

    oled.fill(0)
    oled.text("preparado?...",11,0)
    oled.show()
    time.sleep(0.1)

def init_bunkers():
    cont = 1
    for field in range(0,127,14):
        bunkers.append(Bunker(cont,field+7,55))
        cont += 1

def init_enemies():
    cont = 1
    for field in range(0,127,14):
        enemies.append(Enemy(cont,field+7,0))
        cont += 1

#funcion para dibujar la figura
def render_item(x, y, item):
    global oled
    #iterar en la matriz
    for row in item:
        #pixel a pixel
        for pixel in row:
            #pintar el pixel
            oled.pixel(x,y,pixel)
            x += 1
        x -= len(row)
        y += 1

#manejar el movimiento de la mirilla
def handle_aim():
    global mpu, player, gyro_deadzone, gyro_sensitivity
    
    #lectura del giroscopio
    gyro = mpu.read_gyro_data()
    gx, gy = gyro["x"], gyro["y"]

    # Zona muerta (para ignorar ruido)
    if abs(gx) < gyro_deadzone: gx = 0
    if abs(gy) < gyro_deadzone: gy = 0

    # Aplicar sensibilidad y actualizar mirilla
    player.x = int(min(abs(gy)*gyro_sensitivity,119)) + 2
    player.y = int(min(abs(gx)*gyro_sensitivity,47)) + 2

    #leer de acelerometro
    accel = mpu.read_accel_data()
    ax, ay, az = accel["x"], accel["y"], accel["z"]

    #calcular magnitud
    magnitude = math.sqrt(ax**2+ay**2+az**2)

    if magnitude > 1.3:
        #dibujar la mirilla
        render_item(player.x - 2, player.y - 2, qaim)
        gyro_sensitivity = 1.0
    else:
        #dibujar la mirilla
        render_item(player.x - 2, player.y - 2, aim)
        gyro_sensitivity = 0.5

#dibujar los bunkers en pantalla
def display_bunkers():
    global bunkers, eliminated
    for bnkr in bunkers:
        #si no esta en la lista de eliminados
        if not bnkr.rail in eliminated:
            render_item(bnkr.x, bnkr.y, bunker)

#dibujar los enemigos en pantalla
def display_enemies():
    global enemies, eliminated
    for enm in enemies:
        #si no esta en la lista de eliminados
        if enm.rail in eliminated:
            continue

        #dibujar el enemigo
        render_item(enm.x, enm.y, enemy)
        
        #mover al azar a un enemigo
        idx = random.randint(0,8)
        if not enemies[idx].rail in eliminated:
            enemies[idx].y += random.randint(1,3)

            #ya choco
            if enemies[idx].y >= 55:
                eliminated.append(enemies[idx].rail)

#mostrar pantalla de game over
def game_over():
    global oled, playing, points

    #mostrar mensaje de juego terminado
    oled.text("GAME OVER",34,10)
    oled.text(f"puntuacion: {points}",0,20)
    playing = False
    time.sleep(0.1)

#inicializaciones
init_bunkers()
init_enemies()

#pantalla de inicio
presentation()
        
#ciclo principal
while playing:
    #limpiar pantalla oled
    oled.fill(0)
    
    #verificar game over
    if len(eliminated) == 9:
        game_over()
    else:
        #juego principal
        display_bunkers()
        display_enemies()
        handle_aim()

    #mostrar en oled
    oled.show()
    
    #retraso de programa
    time.sleep(0.05)