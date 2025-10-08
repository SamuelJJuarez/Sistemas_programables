# Integrantes:
# Samuel Jafet Juárez Baliño
# Iván Alejandro Cadena López

# Objetivo: Desarrollar un sistema de control para un servomotor utilizando señales PWM generadas por el ESP32. 
# El programa permite posicionar el servomotor en cualquier ángulo entre 0° y 180°, en base a un número ingresado por el usuario,
# mediante una función parametrizada que calcula automáticamente el ciclo de trabajo (duty cycle) necesario
# para cada ángulo específico. Esto permite entender el funcionamiento del control de servomotores mediante PWM.

# Se importan la clase Pin del módulo machine. Pin se usa para controlar los pines GPIO del ESP32 y PWM 
# se usa para generar señales PWM necesarias para controlar el servomotor.
from machine import Pin, PWM
import time # Se importa el módulo time para crear pausas y esperar a que el servo complete su movimiento

# Configuración del pin GPIO4 como salida digital para controlar el servomotor
servo_pin = Pin(4, Pin.OUT)

# Configuración del PWM (Modulación por Ancho de Pulso) en el pin del servomotor
# PWM genera una señal de pulsos que controla la posición del servo
servo_pwm = PWM(servo_pin)

# Establece la frecuencia del PWM en 50 Hz (50 pulsos por segundo) usadas por servomotores
servo_pwm.freq(50)

# Función para mover el servomotor a un ángulo específico
def set_servo_angle(angle):
    # Posiciona el servomotor en el ángulo especificado (0° a 180°) en base al ángulo recibido
    
    # Asegura que el ángulo no sea exactamente 180 para evitar errores en el cálculo del duty cycle
    if angle == 180:
        angle = 179

    # Calcula el duty cycle en escala 0-1023 según el ángulo
    # Esta fórmula mapea 0-180° al rango 26-128 (equivalente a 1ms-2ms)
    duty_cycle = int((angle / 180) * (128 - 26) + 26)
    
    # Aplica el duty cycle calculado al PWM para mover el servo
    servo_pwm.duty(duty_cycle)
    
    # Pausa de 500ms para permitir que el servomotor complete el movimiento
    time.sleep_ms(500)

# Ciclo principal para mover el servomotor a diferentes ángulos
while True:
    # Solicita al usuario que ingrese un ángulo entre 0° y 180°
    angulo = int(input("Ingrese el ángulo al que desea mover el servomotor (0° a 180°): "))

    # Verifica que el ángulo esté dentro del rango válido
    if angulo < 0 or angulo > 180:
        # Si el ángulo es inválido, muestra un mensaje de error y continúa el ciclo
        print("Ángulo inválido. Por favor ingrese un valor entre 0 y 180.")
        continue

    # Mueve el servo a el ángulo especificado por el usuario
    set_servo_angle(angulo)
    print("Servo movido a", angulo, "grados") 

    time.sleep(1)  # Espera 1 segundo antes de la siguiente acción