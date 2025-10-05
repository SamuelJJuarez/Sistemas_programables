# Integrantes:
# Samuel Jafet Juárez Baliño
# Iván Alejandro Cadena López

# Archivo: main.py
# Propósito: Programa principal que se ejecuta automáticamente después de boot.py

# Objetivo: Desarrollar un sistema de control para un carrito motorizado mediante control remoto infrarrojo (IR).
# El carrito utiliza un puente H L298N para controlar dos motores DC independientemente, permitiendo movimientos
# básicos como avanzar, retroceder, girar a la izquierda, girar a la derecha y detenerse. El sistema funciona
# de manera autónoma sin necesidad de conexión a computadora, ejecutándose automáticamente al encender el ESP32.

# Se importa la clase Pin del módulo machine para controlar los pines GPIO del ESP32
from machine import Pin
import time # Se importa el módulo time para manejo de pausas y tiempos
from ir_rx import NEC_16 # Se importa la clase NEC_16 para manejar la recepción de señales infrarrojas

# Diccionario que mapea los códigos hexadecimales de los botones del control remoto a sus nombres descriptivos
# Estos códigos corresponden al control remoto específico utilizado en el proyecto
buttons = {
    0x45: "1",      # Botón numérico 1
    0x46: "2",      # Botón numérico 2
    0x47: "3",      # Botón numérico 3
    0x44: "4",      # Botón numérico 4
    0x40: "5",      # Botón numérico 5
    0x43: "6",      # Botón numérico 6
    0x7: "7",       # Botón numérico 7
    0x15: "8",      # Botón numérico 8
    0x9: "9",       # Botón numérico 9
    0x19: "0",      # Botón numérico 0
    0x16: "*",      # Botón asterisco
    0x18: "UP",     # Flecha hacia arriba (AVANZAR)
    0x52: "DOWN",   # Flecha hacia abajo (RETROCEDER)
    0xd: "#",       # Botón numeral (DETENER)
    0x1c: "OK",     # Botón OK
    0x8: "LEFT",    # Flecha izquierda (GIRAR IZQUIERDA)
    0x5a: "RGHT"    # Flecha derecha (GIRAR DERECHA)
}

# ========== CONFIGURACIÓN DEL PUENTE H L298N ==========
# El puente H controla los motores DC mediante 4 pines de entrada (IN1, IN2, IN3, IN4)

# Motor izquierdo (rueda izquierda) - Conectado a OUT1 y OUT2 del puente H
motor_izq_adelante = Pin(25, Pin.OUT)  # IN1 del L298N - Control de dirección adelante del motor izquierdo
motor_izq_atras = Pin(26, Pin.OUT)     # IN2 del L298N - Control de dirección atrás del motor izquierdo

# Motor derecho (rueda derecha) - Conectado a OUT3 y OUT4 del puente H
motor_der_adelante = Pin(27, Pin.OUT)  # IN3 del L298N - Control de dirección adelante del motor derecho
motor_der_atras = Pin(14, Pin.OUT)     # IN4 del L298N - Control de dirección atrás del motor derecho

# Receptor infrarrojo - Conectado al pin GPIO21
# Este pin recibe las señales del control remoto IR
ir_receptor = Pin(21, Pin.IN)

# ========== FUNCIONES DE CONTROL DE MOTORES ==========

# Función para hacer avanzar el carrito hacia adelante
def avanzar():
    """
    Mueve el carrito hacia adelante
    Ambos motores giran en dirección forward (adelante)
    
    Funcionamiento:
    - Motor izquierdo: IN1=HIGH, IN2=LOW → Giro adelante
    - Motor derecho: IN3=HIGH, IN4=LOW → Giro adelante
    """
    # Activa dirección adelante para ambos motores
    motor_izq_adelante.on()   # IN1 = HIGH
    motor_izq_atras.off()     # IN2 = LOW
    motor_der_adelante.on()   # IN3 = HIGH
    motor_der_atras.off()     # IN4 = LOW
    print("Movimiento: AVANZAR")

# Función para hacer retroceder el carrito hacia atrás
def retroceder():
    """
    Mueve el carrito hacia atrás
    Ambos motores giran en dirección reverse (reversa)
    
    Funcionamiento:
    - Motor izquierdo: IN1=LOW, IN2=HIGH → Giro atrás
    - Motor derecho: IN3=LOW, IN4=HIGH → Giro atrás
    """
    # Activa dirección atrás para ambos motores
    motor_izq_adelante.off()  # IN1 = LOW
    motor_izq_atras.on()      # IN2 = HIGH
    motor_der_adelante.off()  # IN3 = LOW
    motor_der_atras.on()      # IN4 = HIGH
    print("Movimiento: RETROCEDER")

# Función para girar el carrito a la izquierda
def girar_izquierda():
    """
    Gira el carrito hacia la izquierda
    Motor derecho avanza, motor izquierdo retrocede (giro sobre su eje)
    
    Funcionamiento:
    - Motor izquierdo: IN1=LOW, IN2=HIGH → Giro atrás
    - Motor derecho: IN3=HIGH, IN4=LOW → Giro adelante
    Esto crea un giro en el lugar hacia la izquierda
    """
    # Motor izquierdo retrocede, motor derecho avanza
    motor_izq_adelante.off()  # IN1 = LOW
    motor_izq_atras.on()      # IN2 = HIGH
    motor_der_adelante.on()   # IN3 = HIGH
    motor_der_atras.off()     # IN4 = LOW
    print("Movimiento: GIRAR IZQUIERDA")

# Función para girar el carrito a la derecha
def girar_derecha():
    """
    Gira el carrito hacia la derecha
    Motor izquierdo avanza, motor derecho retrocede (giro sobre su eje)
    
    Funcionamiento:
    - Motor izquierdo: IN1=HIGH, IN2=LOW → Giro adelante
    - Motor derecho: IN3=LOW, IN4=HIGH → Giro atrás
    Esto crea un giro en el lugar hacia la derecha
    """
    # Motor izquierdo avanza, motor derecho retrocede
    motor_izq_adelante.on()   # IN1 = HIGH
    motor_izq_atras.off()     # IN2 = LOW
    motor_der_adelante.off()  # IN3 = LOW
    motor_der_atras.on()      # IN4 = HIGH
    print("Movimiento: GIRAR DERECHA")

# Función para detener completamente el carrito
def detener():
    """
    Detiene el carrito completamente
    Ambos motores se apagan (todas las señales en LOW)
    
    Funcionamiento:
    - Motor izquierdo: IN1=LOW, IN2=LOW → Sin movimiento
    - Motor derecho: IN3=LOW, IN4=LOW → Sin movimiento
    """
    # Apaga todas las señales de control de ambos motores
    motor_izq_adelante.off()  # IN1 = LOW
    motor_izq_atras.off()     # IN2 = LOW
    motor_der_adelante.off()  # IN3 = LOW
    motor_der_atras.off()     # IN4 = LOW
    print("Movimiento: DETENIDO")

# ========== FUNCIÓN CALLBACK PARA CONTROL REMOTO IR ==========

# Función callback que se ejecuta automáticamente cuando se recibe una señal del control remoto
def ir_callback(data, addr, ctrl):
    """
    Maneja las señales recibidas del control remoto infrarrojo
    Mapea cada botón presionado a una función de movimiento del carrito
    
    Parámetros:
    - data: código hexadecimal del botón presionado
    - addr: dirección del control remoto (no utilizada en este caso)
    - ctrl: bits de control del protocolo NEC (no utilizados en este caso)
    """
    # Verifica si el código recibido es inválido (-0x1 indica error de lectura)
    if data == -0x1:
        return  # Ignora señales inválidas
    
    # Verifica si el código recibido está en el diccionario de botones
    if data not in buttons:
        print(f"Botón desconocido: {hex(data)}")
        return  # Ignora botones no configurados
    
    # Obtiene el nombre del botón presionado
    boton = buttons[data]
    print(f"Botón presionado: {boton} (código: {hex(data)})")
    
    # Ejecuta la acción correspondiente según el botón presionado
    if boton == "UP":
        # Flecha arriba: Avanzar
        avanzar()
    elif boton == "DOWN":
        # Flecha abajo: Retroceder
        retroceder()
    elif boton == "LEFT":
        # Flecha izquierda: Girar a la izquierda
        girar_izquierda()
    elif boton == "RGHT":
        # Flecha derecha: Girar a la derecha
        girar_derecha()
    elif boton == "#":
        # Botón numeral: Detener
        detener()
    else:
        # Cualquier otro botón: Detener por seguridad
        detener()
        print(f"Botón '{boton}' no asignado - Deteniendo por seguridad")

# ========== INICIALIZACIÓN DEL SISTEMA ==========

# Configura el receptor infrarrojo con la función callback
# NEC_16 es el protocolo de comunicación utilizado por el control remoto
receptor = NEC_16(ir_receptor, callback=ir_callback)

# Detiene el carrito al iniciar (estado seguro)
detener()

# Mensaje de confirmación en consola
print("="*50)
print("Sistema de carrito motorizado iniciado")
print("Esperando comandos del control remoto IR...")
print("="*50)
print("Controles:")
print("  UP (↑)    : Avanzar")
print("  DOWN (↓)  : Retroceder")
print("  LEFT (←)  : Girar izquierda")
print("  RIGHT (→) : Girar derecha")
print("  # (numeral): Detener")
print("="*50)

# ========== BUCLE PRINCIPAL ==========

# Bucle infinito que mantiene el programa en ejecución
# El control del carrito se realiza mediante las interrupciones del receptor IR
# Este bucle solo mantiene el programa activo
while True:
    # Pausa breve para reducir el uso del procesador
    # El control real se maneja mediante interrupciones (callback)
    time.sleep(0.1)