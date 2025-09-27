# Integrantes:
# Samuel Jafet Juárez Baliño
# Iván Alejandro Cadena López

# Objetivo: Desarrollar un programa que implemente un sistema de control por infrarrojos utilizando un receptor IR
# y una pantalla OLED. El sistema deberá mostrar un menú interactivo que permita al usuario visualizar los códigos
# de los botones presionados, escalar un ícono de alerta dinámicamente, mostrar información del equipo y controlar
# el flujo del programa mediante comandos IR del control remoto.

# Se importan las clases Pin y SoftI2C del módulo machine. Pin se usa para controlar los pines GPIO del ESP32,
# mientras que SoftI2C implementa el protocolo de comunicación I2C por software
from machine import Pin, SoftI2C
import time  # Se importa el módulo time para manejo de pausas y tiempos
from ir_rx import NEC_16 # Se importa la clase NEC_16 para manejar la recepción de señales IR
from ssd1306 import SSD1306_I2C # Se importa el módulo ssd1306 para controlar la pantalla OLED
from logo import LOGO # Importa el logo desde el archivo logo.py

# Diccionario que mapea los códigos hexadecimales de los botones del control remoto a sus nombres descriptivos
buttons = {
    0x45:"1", # Código del botón "1"
    0x46:"2", # Código del botón "2"
    0x47:"3", # Código del botón "3"
    0x44:"4", # Código del botón "4"
    0x40:"5", # Código del botón "5"
    0x43:"6", # Código del botón "6"
    0x7:"7", # Código del botón "7"
    0x15:"8", # Código del botón "8"
    0x9:"9", # Código del botón "9"
    0x19:"0", # Código del botón "0"
    0x16:"*", # Código del botón "*"
    0x18:"UP", # Código de la flecha hacia arriba
    0x52:"DOWN", # Código de la flecha hacia abajo
    0xd:"#", # Código del botón "#"
    0x1c:"OK", # Código del botón "OK"
    0x8:"LEFT", # Código de la flecah izquierda 
    0x5a:"RGHT" # Código de la flecha derecha
}

# Configuración del I2C con los pines GPIO18 (SCL, línea de reloj) y GPI19 (SDA, línea de datos)
i2c = SoftI2C(scl=Pin(18), sda=Pin(19))

# Inicialización de la pantalla OLED con resolución 128x64 píxeles usando I2C
oled = SSD1306_I2C(128, 64, i2c)

# Variables globales
continuar = True # Bandera para mantener el programa en ejecución
opcion = "0" # Variable para almacenar la opción seleccionada en el menú

# Matriz de píxeles que representa el símbolo de alerta (7x7 píxeles)
icon = [
    [1,1,0,1,0,1,1],
    [1,0,1,1,1,0,1],
    [1,0,1,1,1,0,1],
    [1,0,1,1,1,0,1],
    [1,0,0,1,0,0,1],
    [1,0,0,0,0,0,1],
    [1,1,0,1,0,1,1],
]
scale = 1 # Variable global que controla el factor de escala del ícono

# Función para escalar la matriz de alerta aumentando su tamaño por un factor específico
def scale_matrix(matriz, factor):
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
def draw_symbol(oled, originx, originy, pic):
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

# Función para mostrar el menú principal en la pantalla OLED
def menu():
    global oled # Permite acceder a la variable global oled desde dentro de la función
    
    # Limpiar oled
    oled.fill(0)

    # Introduccion del programa 
    oled.text("control IFR menu",0,0)
    oled.text("****************",0,10) 
    oled.text("1.- ver teclas",0,20)  # Opción 1: mostrar códigos de botones
    oled.text("2.- escalar icon",0,30) # Opción 2: escalar ícono
    oled.text("3.- ver info.",0,40) # Opción 3: mostrar información del equipo
    oled.text("4.- salir",0,50)  # Opción 4: salir del programa
    oled.show() # Actualiza la pantalla para mostrar el menú

# Función para mostrar información de los botones presionados en el control remoto
def show_buttons(data):
    # Variable global del oled
    global oled

    # Limpia la pantalla y prepara la interfaz para mostrar detección de botones
    oled.fill(0)
    oled.text("detectando IR...",0,0)

    # Verifica si el código recibido corresponde a un botón conocido
    if data in buttons.keys():
        # Muestra el nombre del botón y su código hexadecimal
        oled.text(f"boton: {buttons[data]}",0,12)
        oled.text(f"cod: {hex(data)}",0,24)
        oled.show() # Actualiza la pantalla para mostrar la información del botón

# Función para mostrar y controlar el escalado del ícono de alerta
def show_icon(data):
    # Variables globales necesarias para el control del ícono
    global oled
    global scale
    global icon

    # Limpia la pantalla
    oled.fill(0)

    # Verifica si el botón presionado no es DOWN ni UP
    if buttons[data] != "DOWN" and buttons[data] != "UP":
        # Dibuja el ícono con la escala actual sin modificarla
        draw_symbol(oled, 0, 0, scale_matrix(icon, scale))
        oled.show()
        return # Sale de la función sin cambiar la escala

    # Manejo del botón UP: incrementa la escala si hay espacio en pantalla
    if buttons[data] == "UP":
        scale = scale + 1 if (len(icon)*scale) < 64 else scale

    # Manejo del botón DOWN: decrementa la escala con límite mínimo de 1
    if buttons[data] == "DOWN":
        scale = scale - 1 if scale > 1 else scale

    # Dibuja el ícono con la nueva escala calculada
    draw_symbol(oled, 0, 0, scale_matrix(icon, scale))
    oled.show() # Actualiza la pantalla para mostrar el ícono escalado
    
# Función para mostrar información del equipo
def show_info():
    global oled
    oled.fill(0) # Limpia la pantalla
    oled.text('Sist.Programables', 0, 0)
    oled.text('ISC', 0, 10)
    oled.text('Equipo:', 0, 20)
    oled.text('Samuel J. Juarez B.', 0, 30)
    oled.text('Ivan A. Cadena L.', 0, 40)
    oled.text('22/09/2025', 0, 50)
    oled.show() # Actualiza la pantalla para mostrar la información

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

# Función para mostrar mensaje de despedida al salir del programa
def despedida():
    # Variable global del oled
    global oled

    # Mensaje de despedida
    oled.fill(0) # Limpia la pantalla
    oled.text("Desactivando",0,0)
    oled.text("sistema...",0,10)
    oled.show() # Actualiza la pantalla para mostrar el mensaje

# Función callback que se ejecuta automáticamente cuando se recibe una señal infrarroja
def ir_callback(data, addr, ctrl):
    # Variable global para guardar la opción
    global opcion

    # Verifica si el código recibido es inválido
    if data == -0x1:
        return # Sale de la función si el código es inválido

    # Si estamos en el menú principal, guarda la opción seleccionada
    if opcion == "0": 
        opcion = buttons[data] # Convierte el código a nombre de botón

    # Manejo del botón *: regresa al menú principal desde cualquier opción
    if buttons[data] == "*":
        opcion = "0"
        menu() # Muestra el menú principal
        return # Sale de la función

    # Opción 1: Mostrar códigos y nombres de botones presionados
    if opcion == "1":
        show_buttons(data)
        return

     # Opción 2: Controlar escalado del ícono con PREV/NEXT
    if opcion == "2":
        show_icon(data)
        return

    # Opción 3: Mostrar información del equipo
    if opcion == "3":
        imprimir_logo()
        time.sleep(2)
        show_info()
        time.sleep(2)
        return
    
    # Opción 4: Salir del programa
    if opcion == "4":
        global continuar
        continuar = False
        despedida()
        return

# Configuración del receptor de infrarrojos en el pin GPIO21 con la función callback
receptor = NEC_16(Pin(21, Pin.IN), callback=ir_callback)

# Muestra el menú principal al iniciar el programa
menu()

# Bucle principal del programa que mantiene el sistema activo
while continuar:
    # Retraso del programa
    time.sleep(0.5)