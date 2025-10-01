# Integrantes:
# Samuel Jafet Juárez Baliño
# Iván Alejandro Cadena López

# Fecha: 30/09/2025

# Objetivo: Desarrollar un sistema de control automático de iluminación que detecte la presencia o ausencia
# de luz ambiente mediante una fotocelda LDR y active/desactive un foco conectado
# a través de un módulo relevador. El sistema funciona de manera autónoma, encendiendo el foco cuando hay
# oscuridad y apagándolo cuando hay suficiente luz natural.

# Se importa la clase Pin del módulo machine para controlar los pines GPIO del ESP32
from machine import Pin
from time import sleep # Se importa sleep para crear pausas entre lecturas

# Configuración del pin GPIO18 como entrada digital para leer el estado de la fotocelda LDR
# El sensor LDR devuelve:
# 0 (LOW) cuando hay luz
# 1 (HIGH) cuando no hay luz 
ldr = Pin(18, Pin.IN)

# Configuración del pin GPIO27 como salida digital para controlar el módulo relevador
# El relevador controla el encendido/apagado del foco:
# 1 (HIGH) activa el relevador y enciende el foco
# 0 (LOW) desactiva el relevador y apaga el foco
rele = Pin(27, Pin.OUT)

# Bucle principal que se ejecuta continuamente para monitorear la luz ambiente
while True:
    # Lee el estado del LDR
    # not ldr.value() invierte la lógica: True cuando no hay luz (ldr.value() == 1)
    if not ldr.value():
        # Si no hay luz, enciende el foco
        rele.value(1) # Activa el relevador para encender el foco
    else:
        # Si hay luz, apaga el foco
        rele.value(0) # Desactiva el relevador para apagar el foco
    
    # Retardo de 1 segundo antes de la siguiente lectura
    sleep(1)
    
    