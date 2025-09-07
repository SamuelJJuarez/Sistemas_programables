# Integrantes:
# Samuel Jafet Juárez Baliño
# Iván Alejandro Cadena López

# Objetivo: Detectar y graficar una señal de voltaje analógica en tiempo real utilizando un ESP32 y una pantalla OLED,
# incluyendo información relevante como el valor de voltaje actual y dibujando los ejes de la gráfica,
# mostrando la forma de onda en la pantalla y actualizándola continuamente para reflejar los cambios en la señal de entrada.

#  Se importan las clases Pin y SoftI2C del módulo machine. Pin se usa para controlar los pines GPIO del ESP32,
# mientras que SoftI2C implementa el protocolo de comunicación I2C por software
from machine import Pin, SoftI2C, ADC
import ssd1306 # Se importa el módulo ssd1306 para controlar la pantalla OLED
from time import sleep_ms # Se importa sleep_ms para crear pausas en milisegundos

# Configuración I2C y OLED
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

# Configuración del convertidor analógico-digital en el pin GPIO34 para leer el potenciómetro
adc = ADC(Pin(34))  
adc.atten(ADC.ATTN_11DB)  # Se configura la atenuación para medir voltajes de 0-3.3V
adc.width(ADC.WIDTH_12BIT)  # Se configura la resolución a 12 bits (valores de 0 a 4095)

# Variables para la configuración de la pantalla y almacenamiento de datos
ancho_oled = 128 # Se define el ancho del OLED
alto_oled = 64 # Se define el alto del OLED
buffer = [0]*ancho_oled   # Buffer circular que almacena los últimos 128 valores de la gráfica

# Función para mapear un valor de un rango a otro rango
def map_value(val, in_min, in_max, out_min, out_max):
    # Aplica regla de tres para convertir un valor de un rango de entrada a un rango de salida
    # Fórmula: valor_salida = (valor_entrada - min_entrada) * (max_salida - min_salida) / (max_entrada - min_entrada) + min_salida
    return int((val - in_min) * (out_max - out_min) / (in_max - in_min) + out_min)

# Función para convertir el valor del ADC a voltaje real
def adc_to_volt(adc_val):
    # Convierte el valor digital (0-4095) a voltaje (0-3.3V) usando regla de tres
    return (adc_val / 4095) * 3.3

# Ciclo principal que se ejecuta continuamente
while True:
    # Lee el valor analógico del potenciómetro (0-4095)
    lectura = adc.read()
    # Convierte el valor ADC en una coordenada y de la pantalla, dejando márgenes de 10 píxeles arriba y abajo
    # Los valores altos del ADC se mapean a la parte superior de la pantalla (y pequeña)
    y = map_value(lectura, 0, 4095, alto_oled-10, 10)
    # Agrega el nuevo valor al final del buffer y elimina el más antiguo (como en una cola FIFO)  
    buffer.append(y)
    buffer.pop(0) # Elimina el primer elemento para mantener el tamaño del buffer constante

    # Limpia la pantalla llenándola de negro
    oled.fill(0)

    # Dibuja los ejes del gráfico
    oled.hline(0, alto_oled-10, ancho_oled, 1)  # Eje X horizontal en la parte inferior (10 píxeles desde abajo)
    oled.vline(0, 0, alto_oled-10, 1)           # Eje Y vertical en el lado izquierdo

    # Dibuja la gráfica conectando puntos consecutivos con líneas
    for x in range(1, ancho_oled):
        # Conecta el punto anterior buffer[x-1] con el punto actual buffer[x] usando una línea
        oled.line(x-1, buffer[x-1], x, buffer[x], 1)

    # Convierte la lectura actual a voltaje y la muestra en pantalla
    volt = adc_to_volt(lectura)
    oled.text("{:.2f}V".format(volt), 60, 0) # Muestra el voltaje con 2 decimales en la posición (60, 0)

     # Actualiza la pantalla para mostrar todos los elementos dibujados
    oled.show()
     # Pausa de 50 milisegundos antes de la siguiente lectura
    sleep_ms(50)
