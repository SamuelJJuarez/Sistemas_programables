# Importar la biblioteca necesaria
import machine
import time

# Definir la frecuencia de la nota y la duración del sonido
notas = {'V': 0, 'G3': 196, 'B3': 247, 'C4':262 ,'C#4': 277, 'D4': 294, 'E4': 330, 'F4': 349, 
         'F#4': 370, 'G4': 392, 'A4': 440, 'B4': 494}
duraciones = {'Redonda': 4, 'Blanca': 2, 'Negra': 1, 'NegraExt': 1.5, 'Corchea': 0.5, 'Semicorchea': 0.25, 'Fusa': 0.125}

# Definir la función para reproducir la nota
def tocar_nota(nota, duracion, tempo):
    frecuencia = notas[nota]
    tiempo_sonido = duraciones[duracion] * (60 / tempo)  # Duración en segundos

    if frecuencia == 0:  # Silencio
        # Para silencio, simplemente esperar sin generar sonido
        time.sleep(tiempo_sonido)
    else:
        # Generar el sonido en el pin 26 usando PWM
        p = machine.Pin(26, machine.Pin.OUT)
        pwm = machine.PWM(p, freq=int(frecuencia), duty=512)

        # Sonar durante el 80% del tiempo de la nota
        time.sleep(tiempo_sonido * 0.8)
        
        # Detener el PWM
        pwm.deinit()
        
        # Pausa breve entre notas (20% del tiempo)
        time.sleep(tiempo_sonido * 0.2)

# Tocar el fragmento de Secrets de OneRepublic
notas_fragmento = ['D4', 'F#4', 'A4', 'F#4', 'D4', 'F#4', 'A4', 'F#4',#
                   'D4', 'F#4', 'A4', 'F#4', 'D4', 'F#4', 'A4', 'F#4',
                   'C#4', 'F#4', 'A4', 'F#4', 'A4', 'F#4', 'C#4', 'F#4',
                   'C#4', 'F#4', 'A4', 'F#4', 'A4', 'F#4', 'C#4', 'F#4',
                   'B3', 'D4', 'B4', 'D4', 'B4', 'D4', 'B3', 'D4',
                   'B3', 'D4', 'B4', 'D4', 'B4', 'D4', 'B3', 'D4',
                   'G3', 'D4', 'B4', 'D4', 'B4', 'D4', 'B4', 'D4',
                   'V', 'V', 'A4', 'A4', 'A4', 'A4', 'A4',
                   'A4', 'F#4', 'V', 'V',
                   'V', 'V', 'A4', 'A4', 'A4', 'A4',
                   'A4', 'F#4', 'E4', 'V',
                   'V', 'V', 'A4', 'A4', 'A4', 'A4', 'A4',
                   'A4', 'F#4', 'V', 'V',
                   'V', 'V', 'A4', 'A4', 'A4', 'A4', 'A4',
                   'A4', 'D4', 'D4', 'B3']

# Duración de cada nota en el fragmento
duracion_fragmento = ['Corchea', 'Corchea', 'Corchea', 'Corchea', 'Corchea', 'Corchea', 'Corchea', 'Corchea',
                   'Corchea', 'Corchea', 'Corchea', 'Corchea', 'Corchea', 'Corchea', 'Corchea', 'Corchea',
                   'Corchea', 'Corchea', 'Corchea', 'Corchea', 'Corchea', 'Corchea', 'Corchea', 'Corchea',
                   'Corchea', 'Corchea', 'Corchea', 'Corchea', 'Corchea', 'Corchea', 'Corchea', 'Corchea',
                   'Corchea', 'Corchea', 'Corchea', 'Corchea', 'Corchea', 'Corchea', 'Corchea', 'Corchea',
                   'Corchea', 'Corchea', 'Corchea', 'Corchea', 'Corchea', 'Corchea', 'Corchea', 'Corchea',
                   'Corchea', 'Corchea', 'Corchea', 'Corchea', 'Corchea', 'Corchea', 'Corchea', 'Corchea',
                   'Negra', 'Corchea', 'Corchea', 'Corchea', 'Corchea', 'Corchea', 'Corchea',
                   'Negra', 'Negra', 'Negra', 'Negra',
                   'Negra', 'Negra', 'Corchea', 'Corchea', 'Corchea', 'Corchea',
                   'Negra', 'Negra', 'Negra', 'Negra',
                   'Negra', 'Corchea', 'Corchea', 'Corchea', 'Corchea', 'Corchea', 'Corchea',
                   'Negra', 'Negra', 'Negra', 'Negra',
                   'Negra', 'Corchea', 'Corchea', 'Corchea', 'Corchea', 'Corchea', 'Corchea',
                   'Negra', 'Negra', 'Corchea', 'NegraExt']

# Ciclo para tocar cada nota del fragmento
for i in range(len(notas_fragmento)):
    nota = notas_fragmento[i]
    duracion = duracion_fragmento[i]
    tocar_nota(nota, duracion, 150)