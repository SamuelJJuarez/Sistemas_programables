# Integrantes:
# Samuel Jafet Juárez Baliño
# Iván Alejandro Cadena López

# Objetivo: Desarrollar un programa que permita medir y visualizar en tiempo real los niveles de
# luminosidad, temperatura y humedad de un ambiente, utilizando sensores y una pantalla OLED.
# El sistema presenta un menú interactivo por consola para seleccionar qué parámetro visualizar durante 20 segundos.

# Se importan las clases Pin y SoftI2C del módulo machine. Pin se usa para controlar los pines GPIO del ESP32,
# mientras que SoftI2C implementa el protocolo de comunicación I2C por software
from machine import Pin, SoftI2C, ADC
import ssd1306 # Se importa el módulo ssd1306 para controlar la pantalla OLED
import dht # Se importa el módulo dht para manejar el sensor DHT11
from time import sleep, ticks_ms, ticks_diff # Se importa sleep para crear pausas y ticks_ms/ticks_diff para medir tiempos
from logo import LOGO  # Importa el logo desde el archivo logo.py

# Configuración del I2C con los pines GPIO18 (SCL, línea de reloj) y GPI19 (SDA, línea de datos)
i2c = SoftI2C(scl=Pin(18), sda=Pin(19))

# Configuración del pin GPIO16 como salida para resetear el OLED
pin_reset = Pin(16, Pin.OUT)
pin_reset.value(0)  # Configura GPIO16 en bajo para resetear el OLED
pin_reset.value(1)  # Configura GPIO16 en alto para activar el OLED

oled_ancho = 128 # Se define el ancho del OLED
oled_alto = 64 # Se define el alto del OLED
# Se crea el objeto que representa la pantalla OLED, especificando sus dimensiones y el bus I2C para comunicarse con ella
oled = ssd1306.SSD1306_I2C(oled_ancho, oled_alto, i2c)

# Configuración de sensor de luminosidad (LDR) conectado al pin GPIO2
ldr = ADC(Pin(2))
ldr.atten(ADC.ATTN_11DB) # Se configura la atenuación para medir voltajes de 0-3.3V
ldr.width(ADC.WIDTH_12BIT) # Se configura la resolución a 12 bits (valores de 0 a 4095)

# Configuración de sensor DHT11 para temperatura y humedad conectado al pin GPIO15
sensor_dht = dht.DHT11(Pin(15))

# Variable global para almacenar los datos de la gráfica en tiempo real
buffer_grafica = [32] * oled_ancho  # Buffer para almacenar datos de la gráfica

# Función para leer el nivel de luminosidad del sensor LDR
def leer_luminosidad():
    lectura = ldr.read() # Lee el valor analógico del LDR (0-4095)
    # Mapea el valor del ADC (0-4095) a porcentaje (0-100)
    porcentaje = int((lectura / 4095) * 100)
    return porcentaje

# Función para leer temperatura y humedad del sensor DHT11
def leer_temperatura_humedad():
    try:
        sensor_dht.measure() # Inicia la medición del sensor DHT11
        temperatura = sensor_dht.temperature() # Obtiene la temperatura en grados Celsius
        humedad = sensor_dht.humidity() # Obtiene la humedad relativa en porcentaje
        return temperatura, humedad
    except:
        # Retorna None para temperatura y humedad en caso de error de comunicación con el sensor
        return None, None

# Función para mapear un valor de un rango a otro rango
def map_value(val, in_min, in_max, out_min, out_max):
    # Aplica regla de tres para convertir un valor de un rango de entrada a un rango de salida
    # valor_salida = (valor_entrada - min_entrada) * (max_salida - min_salida) / (max_entrada - min_entrada) + min_salida
    return int((val - in_min) * (out_max - out_min) / (in_max - in_min) + out_min)

# Función para mostrar el menú principal en consola y OLED
def mostrar_menu():
    # Se muestra en consola el menú de opciones
    print("\n" + "="*40)
    print("SISTEMA DE MONITOREO AMBIENTAL")
    print("="*40)
    print("1. Luminosidad")
    print("2. Temperatura") 
    print("3. Humedad")
    print("4. Integrantes")
    print("0. Salir")
    print("="*40)
    
    # Se muestra en la pantalla OLED el menú de opciones
    oled.fill(0) # Limpia la pantalla
    oled.text("MONITOREO AMBIENTAL", 0, 0)
    oled.hline(0, 10, oled_ancho, 1)
    oled.text("1. Luminosidad", 0, 15)
    oled.text("2. Temperatura", 0, 25)
    oled.text("3. Humedad", 0, 35)
    oled.text("4. Integrantes", 0, 45)
    oled.text("Ver consola", 0, 55)
    oled.show() # Actualiza la pantalla para mostrar el menú enviando con la función text()

# Función para leer la opción seleccionada por el usuario en consola
def leer_opcion_consola():
    try:
        opcion = input("\nSeleccione una opción (0-4): ") # Solicita entrada del usuario
        return int(opcion) # Convierte la entrada a entero y la retorna
    except ValueError:
        # Envía mensaje de error si la entrada no es un valor numérico
        print("Error: Ingrese un número válido")
        return -1 # Retorna -1 para indicar que hubo una entrada inválida

# Función genérica para mostrar gráficas en tiempo real durante 20 segundos
def mostrar_grafica(tipo_sensor, funcion_lectura, rango_min, rango_max, unidad, delay=0.5):

    # Función genérica para mostrar gráficas de sensores en tiempo real
    # Parámetros:
    # tipo_sensor: String con el tipo de lectura para mostrar en pantalla
    # funcion_lectura: Función que lee el valor del sensor
    # rango_min: Valor mínimo del rango del sensor
    # rango_max: Valor máximo del rango del sensor  
    # unidad: String con la unidad de medida (%, °C)
    # delay: Tiempo de pausa entre lecturas en segundos
    
    print(f"Monitoreando {tipo_sensor.lower()}...")
    inicio = ticks_ms() # Marca el tiempo de inicio en milisegundos
    buffer_local = [32] * oled_ancho # Buffer local para almacenar los datos de la gráfica
    
    # Bucle que se ejecuta durante 20 segundos (20000 ms)
    while ticks_diff(ticks_ms(), inicio) < 20000:
        valor = funcion_lectura() # Lee el valor actual del sensor usando la función proporcionada
        
        # Verifica que la lectura sea válida (esto para el caso del DHT11)
        if valor is not None:
            # Limita el valor al rango especificado y lo mapea a coordenadas y (10-54)
            # Los valores más altos se mapean a valores de y más pequeños (parte superior de la gráfica)
            valor_limitado = min(max(valor, rango_min), rango_max) # Limita el valor al rango definido
            y = map_value(valor_limitado, rango_min, rango_max, 54, 10) # Mapea el valor al rango de píxeles verticales
            
            # Actualiza buffer circular: se agrega el nuevo valor al final y elimina el primero
            buffer_local.append(y)
            buffer_local.pop(0)
            
            # Limpia la pantalla y dibuja la interfaz
            oled.fill(0)
            oled.text(tipo_sensor.upper(), 0, 0) # Título de la gráfica en mayúsculas
            
            # Formatea y muestra el valor actual según el tipo de dato
            if isinstance(valor, float):
                texto_valor = "{:.1f}{}".format(valor, unidad) # Un decimal para flotantes
            else:
                texto_valor = "{}{}".format(valor, unidad) # Sin decimales para enteros
                
            # Posiciona el texto del valor en la esquina superior derecha
            pos_x = 128 - len(texto_valor) * 8 - 5  # Calcula posición para alinear a la derecha
            oled.text(texto_valor, max(pos_x, 70), 0) # Mínimo en posición 70
            
            # Dibuja los ejes de la gráfica
            oled.hline(0, 54, oled_ancho, 1)  # Eje x  en la parte inferior
            oled.vline(0, 10, 45, 1)          # Eje y en el lado izquierdo
            
            # Etiquetas de escala en el eje y
            oled.text(str(rango_max), 105, 10) # Valor máximo en la parte superior
            oled.text(str(rango_min), 110, 50) # Valor mínimo en la parte inferior
            
            # Dibuja la gráfica conectando puntos consecutivos con líneas
            for x in range(1, oled_ancho):
                oled.line(x-1, buffer_local[x-1], x, buffer_local[x], 1)
            
            # Actualiza la pantalla para mostrar todos los elementos dibujados
            oled.show()
            
            # Muestra el valor también en consola
            if isinstance(valor, float):
                print(f"{tipo_sensor}: {valor:.1f}{unidad}")
            else:
                print(f"{tipo_sensor}: {valor}{unidad}")
                
        else:
            # Maneja el caso de error en la lectura del sensor DHT11
            oled.fill(0)
            oled.text("Error DHT11", 20, 30) # Mensaje de error específico para DHT11
            oled.show()
            print(f"Error leyendo {tipo_sensor.lower()}")
        
        sleep(delay) # Pausa entre lecturas según el sensor
    
    print(f"Monitoreo de {tipo_sensor.lower()} completado")

# Función para extraer el valor de temperatura del DHT11
def obtener_solo_temperatura():
    temperatura, _ = leer_temperatura_humedad()
    return temperatura

# Función para extraer el valor de humedad del DHT11
def obtener_solo_humedad():
    _, humedad = leer_temperatura_humedad()
    return humedad

# Función para mostrar gráfica de luminosidad
def mostrar_grafica_luminosidad():
    # Se pasa el nombre del tipo de lectura, la función de lectura, el rango (0-100%), la unidad y el delay entre lecturas
    mostrar_grafica("Luminosidad", leer_luminosidad, 0, 100, "%", 0.5)

# Función para mostrar gráfica de temperatura
def mostrar_grafica_temperatura():
    # Se pasa el nombre del tipo de lectura, la función de lectura, el rango (0-50°C), la unidad y el delay entre lecturas
    mostrar_grafica("Temperatura", obtener_solo_temperatura, 0, 50, "°C", 1.0)

#  Función para mostrar gráfica de humedad
def mostrar_grafica_humedad():
    # Se pasa el nombre del tipo de lectura, la función de lectura, el rango (0-100%), la unidad y el delay entre lecturas
    mostrar_grafica("Humedad", obtener_solo_humedad, 0, 100, "%", 1.0)

# Función para mostrar información del equipo y el logo del Tecnológico durante 20 segundos
def mostrar_integrantes():
    print("Mostrando información del equipo...")
    inicio = ticks_ms() # Marca el tiempo de inicio
    
    # Primero se muestra el logo durante 5 segundos
    oled.fill(0) # Limpia la pantalla
    # Recorre cada fila del logo
    for y, fila in enumerate(LOGO):
        x = 0  # Inicializa la posición horizontal (columna) en 0 para cada nueva fila
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
    oled.show() # Actualiza la pantalla para mostrar el logo dibujado
    print("Mostrando logo del Tecnológico...")
    
    # Espera 5 segundos mostrando el logo
    while ticks_diff(ticks_ms(), inicio) < 5000:
        sleep(0.1)
    
    # Luego se muestra la información del equipo durante 15 segundos
    print("Mostrando información del equipo...")
    tiempo_restante = 20000 - ticks_diff(ticks_ms(), inicio) # Tiempo restante para completar 20 segundos
    inicio_texto = ticks_ms() # Marca el tiempo de inicio para mostrar el texto
    
    # Muestra la información del equipo durante el tiempo restante
    while ticks_diff(ticks_ms(), inicio_texto) < tiempo_restante:
        oled.fill(0) # Limpia la pantalla
        oled.text('Sist.Programables', 0, 0)
        oled.text('ISC', 0, 10)
        oled.text('Equipo:', 0, 20)
        oled.text('Samuel J. Juarez B.', 0, 30)
        oled.text('Ivan A. Cadena L.', 0, 40)
        oled.text('10/09/2025', 0, 50)
        oled.show() # Actualiza la pantalla para mostrar la información envianda con la función text()
    
    print("Información del equipo completada.")
    
# Bucle principal del programa que maneja el menú y las opciones del usuario
while True:
    mostrar_menu() # Muestra el menú principal
    opcion = leer_opcion_consola() # Lee la opción seleccionada por el usuario
        
    if opcion == 0: # Opción para salir del programa
        print("Saliendo del sistema...")
        oled.fill(0)
        oled.text("Sistema", 40, 20) 
        oled.text("Terminado", 35, 35)
        oled.show() # Actualiza la pantalla para mostrar el mensaje de salida
        break # Sale del bucle y termina el programa
    elif opcion == 1:  # Opción para monitorear luminosidad
        print("Iniciando monitoreo de luminosidad por 20 segundos...")
        mostrar_grafica_luminosidad()
    elif opcion == 2:  # Opción para monitorear temperatura
        print("Iniciando monitoreo de temperatura por 20 segundos...")
        mostrar_grafica_temperatura()
    elif opcion == 3:  # # Opción para monitorear humedad
        print("Iniciando monitoreo de humedad por 20 segundos...")
        mostrar_grafica_humedad()
    elif opcion == 4:  # Opción para mostrar información del equipo
        print("Mostrando información del equipo por 20 segundos...")
        mostrar_integrantes()
    else: # Manejo de opción inválida
        print("Opción inválida. Seleccione una opción del 0 al 4.")
        
    sleep(0.5) # Pequeña pausa antes de mostrar el menú nuevamente