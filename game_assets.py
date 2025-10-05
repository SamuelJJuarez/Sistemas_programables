# Integrantes:
# Samuel Jafet Juárez Baliño
# Iván Alejandro Cadena López

# Fecha: 29/09/2025

# Objetivo: Definir los recursos gráficos (sprites) y clases de objetos del juego "Los Bunkers",
# un juego estilo Space Invaders para ESP32 donde el jugador debe defender el planeta de invasores alienígenas
# utilizando un giroscopio MPU6050 para controlar la mira y un botón para disparar.

# Matriz de píxeles que representa el sprite del enemigo alienígena (8x8 píxeles)
# Cada 1 representa un píxel encendido (blanco) y cada 0 un píxel apagado (negro)
enemy = [
    [0,0,0,1,1,0,0,0],  
    [0,0,1,1,1,1,0,0],  
    [0,0,1,0,0,1,0,0],  
    [0,0,1,0,0,1,0,0],  
    [0,1,1,1,1,1,1,0], 
    [1,0,0,1,1,0,0,1],  
    [1,1,1,1,1,1,1,1],  
    [0,1,0,1,1,0,1,0],  
]

# Clase Enemy: Representa a un enemigo alienígena en el juego
class Enemy:
    def __init__(self, rail, x, y):
        # rail: número de carril donde se encuentra el enemigo (1-9)
        # x: posición horizontal inicial en píxeles
        # y: posición vertical inicial en píxeles

        self.rail = rail  # Identificador del carril donde está el enemigo
        self.x = x        # Coordenada x (horizontal) del enemigo
        self.y = y        # Coordenada y (vertical) del enemigo

# Matriz de píxeles que representa la mira normal del jugador (8x8 píxeles)
# Diseño de cruz circular para apuntar a los enemigos
aim = [
    [0,0,0,1,1,0,0,0],  
    [0,0,1,1,1,1,0,0],  
    [0,1,1,0,0,1,1,0],  
    [1,1,0,1,1,0,1,1],  
    [1,1,0,1,1,0,1,1],  
    [0,1,1,0,0,1,1,0],  
    [0,0,1,1,1,1,0,0],  
    [0,0,0,1,1,0,0,0],  
]

# Matriz de píxeles que representa la mira mejorada/rápida del jugador (8x8 píxeles)
# Se activa cuando el jugador mueve rápidamente el giroscopio 
qaim = [
    [1,1,0,0,0,0,1,1],  
    [1,0,1,1,1,1,0,1],  
    [0,1,1,0,0,1,1,0], 
    [0,1,0,1,1,0,1,0],  
    [0,1,0,1,1,0,1,0],  
    [0,1,1,0,0,1,1,0],  
    [1,0,1,1,1,1,0,1],  
    [1,1,0,0,0,0,1,1],  
]

# Clase Aim: Representa la mira controlada por el jugador
class Aim:
    def __init__(self, x, y):
        # x: posición horizontal inicial de la mira en píxeles
        # y: posición vertical inicial de la mira en píxeles
        
        self.x = x  # Coordenada x (horizontal) de la mira
        self.y = y  # Coordenada y (vertical) de la mira

# Matriz de píxeles que representa un búnker/defensa (8x8 píxeles)
# Los búnkers son estructuras defensivas que el jugador debe proteger de los alienígenas
bunker = [
    [0,0,1,1,1,1,0,0],  
    [0,1,1,1,1,1,1,0],  
    [1,1,1,1,1,1,1,1],  
    [1,0,0,1,1,0,0,1],  
    [1,0,0,1,1,0,0,1],  
    [1,1,1,1,1,1,1,1],  
    [1,1,1,0,0,1,1,1],  
    [1,1,1,0,0,1,1,1],  
]

# Clase Bunker: Representa una estructura defensiva en el juego
class Bunker:
    def __init__(self, rail, x, y):
        # rail: número de carril donde se encuentra el búnker (1-9)
        # x: posición horizontal del búnker en píxeles
        # y: posición vertical del búnker en píxeles (usualmente cerca del fondo)
        
        self.rail = rail  # Identificador del carril donde está el búnker
        self.x = x        # Coordenada x (horizontal) del búnker
        self.y = y        # Coordenada y (vertical) del búnker