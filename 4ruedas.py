from machine import Pin, PWM

# Configuración de pines para los motores
motor_pins = [
	[Pin(26), Pin(25)],  # Motor 1
	[Pin(33), Pin(32)],  # Motor 2
	[Pin(4), Pin(0)],    # Motor 3
	[Pin(21), Pin(22)],  # Motor 4
]

# Configuración de pines para la velocidad de los motores
motor_speed_pins = [
	PWM(Pin(14), freq=5000),  # Motor 1
	PWM(Pin(13), freq=5000),  # Motor 2
	PWM(Pin(12), freq=5000),  # Motor 3
	PWM(Pin(15), freq=5000),  # Motor 4
]

# Función para avanzar
def forward(speed):
	for pins in motor_pins:
		pins[0].value(1)
		pins[1].value(0)
	for speed_pin in motor_speed_pins:
		speed_pin.duty(speed)

# Función para retroceder
def backward(speed):
	for pins in motor_pins:
		pins[0].value(0)
		pins[1].value(1)
	for speed_pin in motor_speed_pins:
		speed_pin.duty(speed)

# Función para girar a la izquierda
def left(speed):
	for i, pins in enumerate(motor_pins):
		if i % 2 == 0:
			pins[0].value(0)
			pins[1].value(1)
		else:
			pins[0].value(1)
			pins[1].value(0)
	for speed_pin in motor_speed_pins:
		speed_pin.duty(speed)

# Función para girar a la derecha
def right(speed):
	for i, pins in enumerate(motor_pins):
		if i % 2 == 0:
			pins[0].value(1)
			pins[1].value(0)
		else:
			pins[0].value(0)
			pins[1].value(1)
	for speed_pin in motor_speed_pins:
		speed_pin.duty(speed)