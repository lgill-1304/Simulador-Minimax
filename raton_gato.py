import numpy as np
import random
import pygame
import time

# Dimensiones del tablero
TABLERO_TAMANIO = 5
TAMANIO_CELDA = 80
ANCHO_VENTANA = TABLERO_TAMANIO * TAMANIO_CELDA
ALTO_VENTANA = TABLERO_TAMANIO * TAMANIO_CELDA

# Colores
COLOR_FONDO_CLARO = (255, 255, 255)
COLOR_FONDO_OSCURO = (0, 0, 0)
COLOR_LINEA = (0, 0, 0)

# Inicializamos el tablero
tablero = np.zeros((TABLERO_TAMANIO, TABLERO_TAMANIO))

# Función para posicionar el gato y el ratón a una distancia de al menos 4 casillas
def posicion():
    while True:
        gato_x = random.randint(0, TABLERO_TAMANIO - 1)
        gato_y = random.randint(0, TABLERO_TAMANIO - 1)
        raton_x = random.randint(0, TABLERO_TAMANIO - 1)
        raton_y = random.randint(0, TABLERO_TAMANIO - 1)
        
        # Calcula la distancia entre el gato y el ratón
        distancia = abs(gato_x - raton_x) + abs(gato_y - raton_y)
        
        # Si la distancia es mayor o igual a 4, devuelve las posiciones
        if distancia >= 4:
            return (gato_x, gato_y), (raton_x, raton_y)

# Posiciones iniciales del gato y ratón
gato_pos, raton_pos = posicion()

# Definir las posiciones iniciales en el tablero
tablero[gato_pos] = 1  # 1 representa al Gato
tablero[raton_pos] = 2  # 2 representa al Ratón

# Para evitar movimientos repetidos
movimientos_previos = set()

# Funciones de movimiento y evaluación
def mover_jugador(tablero, posicion_actual, nueva_posicion):
    if (0 <= nueva_posicion[0] < TABLERO_TAMANIO) and (0 <= nueva_posicion[1] < TABLERO_TAMANIO):
        jugador = tablero[posicion_actual]
        tablero[posicion_actual] = 0
        tablero[nueva_posicion] = jugador
        return nueva_posicion
    else:
        return posicion_actual

def evaluar(tablero):
    gato_pos = np.argwhere(tablero == 1)
    raton_pos = np.argwhere(tablero == 2)
    
    if gato_pos.size == 0 or raton_pos.size == 0:
        return 0
    
    # Distancia Manhattan gato
    gato_pos = gato_pos[0]
    raton_pos = raton_pos[0]
    distancia = np.sum(np.abs(gato_pos - raton_pos))
    return -distancia  # Queremos minimizar la distancia para el Gato

def evaluar_raton(tablero):
    gato_pos = np.argwhere(tablero == 1)
    raton_pos = np.argwhere(tablero == 2)
    
    if gato_pos.size == 0 or raton_pos.size == 0:
        return 0
    
    # Distancia Manhattan ratón
    gato_pos = gato_pos[0]
    raton_pos = raton_pos[0]
    distancia = np.sum(np.abs(gato_pos - raton_pos))
    return distancia  # Queremos maximizar la distancia para el Ratón

# Algoritmo Minimax
def minimax(tablero, profundidad, maximizando, movimientos_previos):
    if profundidad == 0 or juego_terminado(tablero):
        return evaluar(tablero) if maximizando else evaluar_raton(tablero)
    
    # Movimientos del gato
    if maximizando:
        mejor_valor = -np.inf
        movimientos = generar_movimientos(tablero, 1, movimientos_previos)
        for movimiento in movimientos:
            valor = minimax(movimiento, profundidad - 1, False, movimientos_previos)
            mejor_valor = max(mejor_valor, valor)
        return mejor_valor
    
    # Movimientos del ratón
    else:
        mejor_valor = np.inf
        movimientos = generar_movimientos(tablero, 2, movimientos_previos)
        for movimiento in movimientos:
            valor = minimax(movimiento, profundidad - 1, True, movimientos_previos)
            mejor_valor = min(mejor_valor, valor)
        return mejor_valor

# Generación de movimientos y finalización de juego
def generar_movimientos(tablero, jugador, movimientos_previos):
    movimientos = []
    posicion_actual = np.argwhere(tablero == jugador)
    
    if posicion_actual.size == 0:
        return movimientos
    
    posicion_actual = posicion_actual[0]
    if jugador == 1:
        posibles_movimientos = [(0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)]  # Incluye movimientos diagonales
    else:
        posibles_movimientos = [(0, 1), (0, -1), (1, 0), (-1, 0)]  # Movimientos en las cuatro direcciones
    
    for movimiento in posibles_movimientos:
        nueva_posicion = (posicion_actual[0] + movimiento[0], posicion_actual[1] + movimiento[1])
        if (0 <= nueva_posicion[0] < TABLERO_TAMANIO) and (0 <= nueva_posicion[1] < TABLERO_TAMANIO):
            nuevo_tablero = tablero.copy()
            nuevo_tablero[posicion_actual[0], posicion_actual[1]] = 0
            nuevo_tablero[nueva_posicion[0], nueva_posicion[1]] = jugador
            
            if tuple(map(tuple, nuevo_tablero)) not in movimientos_previos:
                movimientos.append(nuevo_tablero)
    return movimientos

def juego_terminado(tablero):
    gato_pos = np.argwhere(tablero == 1)
    raton_pos = np.argwhere(tablero == 2)
    if gato_pos.size == 0 or raton_pos.size == 0:
        return True
    gato_pos = gato_pos[0]
    raton_pos = raton_pos[0]
    if np.array_equal(gato_pos, raton_pos):
        return True
    return False

# Dibujar jugadores y jugar
def dibujar_jugadores(pantalla, imagen_gato, imagen_raton, gato_pos, raton_pos):
    pantalla.fill(COLOR_FONDO_CLARO)
    for x in range(TABLERO_TAMANIO):
        for y in range(TABLERO_TAMANIO):
            color_celda = COLOR_FONDO_OSCURO if (x + y) % 2 == 0 else COLOR_FONDO_CLARO
            rect = pygame.Rect(y * TAMANIO_CELDA, x * TAMANIO_CELDA, TAMANIO_CELDA, TAMANIO_CELDA)
            pygame.draw.rect(pantalla, color_celda, rect)
            pygame.draw.rect(pantalla, COLOR_LINEA, rect, 1)
            if tablero[x, y] == 1:
                pantalla.blit(imagen_gato, rect.topleft)
            elif tablero[x, y] == 2:
                pantalla.blit(imagen_raton, rect.topleft)
    pygame.display.flip()

def jugar():
    global gato_pos, raton_pos
    turno_gato = True
    profundidad = 3
    rondas = 0  # Contador de rondas

    # Inicializar pygame
    pygame.init()
    pantalla = pygame.display.set_mode((ANCHO_VENTANA, ALTO_VENTANA))
    pygame.display.set_caption("Juego del Gato y el Ratón")
    reloj = pygame.time.Clock()

    # Cargar imágenes GIF y redimensionarlas
    imagen_gato = pygame.image.load('static/gatito.png')
    imagen_raton = pygame.image.load('static/ratoncito.png')
    imagen_gato = pygame.transform.scale(imagen_gato, (TAMANIO_CELDA, TAMANIO_CELDA))
    imagen_raton = pygame.transform.scale(imagen_raton, (TAMANIO_CELDA, TAMANIO_CELDA))

    corriendo = True
    while corriendo and not juego_terminado(tablero) and rondas < 10:  # Continuar el juego hasta que se alcance el límite de rondas
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                corriendo = False

        if turno_gato:
            # Turno del gato
            mejor_valor = -np.inf
            mejor_movimiento = None
            movimientos = generar_movimientos(tablero, 1, movimientos_previos)
            for movimiento in movimientos:
                valor = minimax(movimiento, profundidad, False, movimientos_previos)
                if valor > mejor_valor:
                    mejor_valor = valor
                    mejor_movimiento = movimiento
            if mejor_movimiento is not None:
                movimientos_previos.add(tuple(map(tuple, mejor_movimiento)))
                tablero[:] = mejor_movimiento
                gato_pos = np.argwhere(tablero == 1)[0]

            dibujar_jugadores(pantalla, imagen_gato, imagen_raton, gato_pos, raton_pos)
            time.sleep(1)
            turno_gato = False
        else:
            # Turno del ratón
            mejor_valor = -np.inf
            mejor_movimiento = None
            movimientos = generar_movimientos(tablero, 2, movimientos_previos)
            for movimiento in movimientos:
                valor = minimax(movimiento, profundidad, True, movimientos_previos)
                if valor > mejor_valor:
                    mejor_valor = valor
                    mejor_movimiento = movimiento
            if mejor_movimiento is not None:
                movimientos_previos.add(tuple(map(tuple, mejor_movimiento)))
                tablero[:] = mejor_movimiento
                raton_pos = np.argwhere(tablero == 2)[0]

            dibujar_jugadores(pantalla, imagen_gato, imagen_raton, gato_pos, raton_pos)
            time.sleep(1)
            turno_gato = True

        rondas += 1  # Incrementar el contador de rondas

    # Mostrar el resultado final
    pantalla.fill(COLOR_FONDO_CLARO)
    if gato_pos.size == 0 or raton_pos.size == 0:
        mensaje = "Error en la posición de los jugadores."
    elif rondas == 10:  # Si se alcanzó el límite de rondas
        mensaje = "¡El Ratón ha escapado!"
    elif juego_terminado(tablero):
        if np.array_equal(gato_pos, raton_pos):
            mensaje = "!El Gato ha atrapado al Ratón!"

    fuente = pygame.font.SysFont(None, 27)
    texto = fuente.render(mensaje, True, COLOR_LINEA)
    pantalla.blit(texto, (ANCHO_VENTANA // 4, ALTO_VENTANA // 2))
    pygame.display.flip()

    while True:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                return

if __name__ == "__main__":
    jugar()
