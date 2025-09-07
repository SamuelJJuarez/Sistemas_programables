from machine import Pin, PWM
import time

 # =======================================================================
 # PIN ROJO - GPIO4
 # Crea el objeto PWM en el pin GPIO 4 con una frecuencia de 20 kHz y un ciclo de trabajo del 50% (512/1024)
pwm4 = PWM(Pin(4), freq=20000, duty=512)

 # =======================================================================
 # PIN VERDE - GPIO2
 # Crea el objeto PWM en el pin GPIO 2
pwm2 = PWM(Pin(2))

# Imprime la frecuencia establecida por defecto (normalmente 1 kHz)
print(pwm2.freq())

 # Establece una nueva frecuencia de 10 kHz
pwm2.freq(10000)

 # Imprime el ciclo de trabajo establecido por defecto (normalmente 0)
print(pwm2.duty())

# Establece un nuevo ciclo de trabajo al 200/1024 (~20%)
pwm2.duty(200)

# Detiene el programa por 2 segundos
time.sleep(2)

 # Apaga el PWM en el pin GPIO 2
pwm2.deinit()

# =======================================================================
 # PIN AZUL - GPIO15
 # Crea el objeto PWM en el pin GPIO 15 con una frecuencia de 28.1 kHz
pwm15 = PWM(Pin(15), freq=28100)

while True:
    # Aumenta el ciclo de trabajo desde 0 hasta 1023 (2**10=1024) en pasos de 1
    for i in range(2**10):
         pwm15.duty(i)
         # Cambia el ciclo de trabajo cada milisegundo
         time.sleep(0.001)  

    # Disminuye el ciclo de trabajo desde 1023 hasta 0 en pasos de 1
    for i in range(2**10 - 1, -1, -1):
        pwm15.duty(i)
        # Cambia el ciclo de trabajo cada milisegundo
        time.sleep(0.001)