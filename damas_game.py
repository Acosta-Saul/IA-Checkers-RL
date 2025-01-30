import pygame, sys

pygame.init()
pygame.mixer.init()

# ============CONFIGUTACIÓN INICIAL===================

# Tamaño de pantalla
screen = pygame.display.set_mode([384, 520])

# Definir colores en RGB
marron_c = (102, 51, 0)
marron_o = (153, 76, 0)
negro = (0, 0, 0)
blanco = (255, 255, 255)

# Colecciona todos los sprites
all_sprite_list = pygame.sprite.Group()
TCELDA = 96

turno = 'negro'  # Turno inicial

# Contadores de victorias, empates y turnos
victorias_ia = 0
victorias_humano = 0
empates = 0
numero_turno = 1  # Comienza en 1


class Player(pygame.sprite.Sprite):
    def __init__(self, color, columna, fila):
        super().__init__()
        self.color = color
        self.image = pygame.Surface((50, 50), pygame.SRCALPHA)
        pygame.draw.circle(self.image, color, (25, 25), 25)
        self.rect = self.image.get_rect()
        self.rect.x = columna * TCELDA + (TCELDA - 50) // 2
        self.rect.y = fila * TCELDA + (TCELDA - 50) // 2
        self.columna = columna
        self.fila = fila

    def mover(self, nueva_columna, nueva_fila):
        self.columna = nueva_columna
        self.fila = nueva_fila
        self.rect.x = nueva_columna * TCELDA + (TCELDA - 50) // 2
        self.rect.y = nueva_fila * TCELDA + (TCELDA - 50) // 2


class Tablero:
    def dibujar_grid(self, screen):
        for x in range(4):
            for y in range(4):
                color = marron_o if (x + y) % 2 == 0 else marron_c
                pygame.draw.rect(screen, color, (x * TCELDA, y * TCELDA, TCELDA, TCELDA))


# Función para colocar fichas
def colocar_fichas(color, fila_inicio):
    for j in range(4):
        if (fila_inicio + j) % 2 == 0:
            ficha = Player(color, j, fila_inicio)
            all_sprite_list.add(ficha)


# Función para verificar si una casilla está ocupada
def casilla_ocupada(columna, fila):
    for ficha in all_sprite_list:
        if ficha.columna == columna and ficha.fila == fila:
            return True
    return False


# Función para verificar ganador o empate
def verificar_ganador():
    negras = sum(1 for ficha in all_sprite_list if ficha.color == negro)
    blancas = sum(1 for ficha in all_sprite_list if ficha.color == blanco)
    if negras == 0:
        return "¡Ganan las Blancas!", 'humano'
    elif blancas == 0:
        return "¡Ganan las Negras!", 'ia'
    return None, None


# Función para mostrar texto en pantalla
def mostrar_texto(texto, pantalla, y_pos, size=24):
    fuente = pygame.font.SysFont("Arial", size)
    superficie_texto = fuente.render(texto, True, (255, 0, 0))
    pantalla.blit(superficie_texto, (screen.get_width() // 2 - superficie_texto.get_width() // 2, y_pos))


# Función para reiniciar el juego
def reiniciar_juego():
    global turno, all_sprite_list, numero_turno
    # Limpiar todas las fichas
    all_sprite_list.empty()

    # Colocar las fichas en sus posiciones iniciales
    colocar_fichas(negro, 0)  
    colocar_fichas(blanco, 3)  
    
    turno = 'negro'  
    numero_turno = 1  
    
  


# Colocar fichas iniciales
tablero = Tablero()
colocar_fichas(negro, 0)
colocar_fichas(blanco, 3)

ficha_seleccionada = None
ganador = None

# Bandera para evitar incremento repetido de victorias
victoria_detectada = False

# Función para calcular todas las jugadas posibles
def jugadas_posibles(ficha):
    jugadas = []
    for dx, dy in [(-1, -1), (1, -1), (-1, 1), (1, 1)]:
        nueva_columna = ficha.columna + dx
        nueva_fila = ficha.fila + dy
        if 0 <= nueva_columna < 4 and 0 <= nueva_fila < 4 and not casilla_ocupada(nueva_columna, nueva_fila):
            jugadas.append((nueva_columna, nueva_fila))
    return jugadas


# Función de Minimax
def minimax():
    mejores_jugadas = []
    mejor_puntaje = -float('inf')  # Comenzar con el peor puntaje posible

    # Evaluar todas las fichas de la IA 
    for ficha in all_sprite_list:
        if ficha.color == negro:  
            # Primero, verificamos si hay alguna jugada de captura
            for dx, dy in [(-2, -2), (2, -2), (-2, 2), (2, 2)]:
                nueva_columna = ficha.columna + dx
                nueva_fila = ficha.fila + dy
                medio_columna = (ficha.columna + nueva_columna) // 2
                medio_fila = (ficha.fila + nueva_fila) // 2
                if 0 <= nueva_columna < 4 and 0 <= nueva_fila < 4 and not casilla_ocupada(nueva_columna, nueva_fila):
                    for ficha_comida in all_sprite_list:
                        if ficha_comida.columna == medio_columna and ficha_comida.fila == medio_fila and ficha_comida.color != ficha.color:
                            # Captura realizada
                            all_sprite_list.remove(ficha_comida)
                            puntaje = 10  # Recompensar la captura
                            mejores_jugadas.append((ficha, nueva_columna, nueva_fila, puntaje))
                            if puntaje > mejor_puntaje:
                                mejor_puntaje = puntaje
                            break

            # Si no se encontró ninguna captura, evaluar jugadas simples
            if not mejores_jugadas:
                for jugada in jugadas_posibles(ficha):
                    # Simple movimiento sin captura
                    mejores_jugadas.append((ficha, jugada[0], jugada[1], 0))  # Movimiento simple

    # Si hay jugadas, elegir la mejor
    if mejores_jugadas:
        # Seleccionar la jugada con el mejor puntaje
        mejor_jugada = max(mejores_jugadas, key=lambda x: x[3])  # Escoge la jugada con el puntaje más alto
        return mejor_jugada[1], mejor_jugada[2]  # Devuelve coordenada del tablero

    return None

sound = pygame.mixer.Sound("movimiento.mp3")
pygame.mixer.music.load("ost.mp3")
pygame.mixer.music.play(10)

# Bucle principal
start = True
inicio_espera = pygame.time.get_ticks()  
while start:
    # Esperar 3 segundos antes de iniciar el juego
    if pygame.time.get_ticks() - inicio_espera < 1000:
        screen.fill((255, 255, 255))
        tablero.dibujar_grid(screen)
        all_sprite_list.draw(screen)
        pygame.display.flip()
        continue  
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = pygame.mouse.get_pos()
            columna = pos[0] // TCELDA
            fila = pos[1] // TCELDA

            # Seleccionar ficha
            if not ficha_seleccionada:
                for ficha in all_sprite_list:
                    if ficha.rect.collidepoint(pos) and ficha.color == (negro if turno == 'negro' else blanco):
                        ficha_seleccionada = ficha
                        break
            else:
                dx = columna - ficha_seleccionada.columna
                dy = fila - ficha_seleccionada.fila

                if not casilla_ocupada(columna, fila):
                    if abs(dx) == 1 and abs(dy) == 1:  # Movimiento simple
                        ficha_seleccionada.mover(columna, fila)
                        turno = 'blanco' if turno == 'negro' else 'negro'
                        numero_turno += 1  # Incrementar el número de turno
                        ficha_seleccionada = None
                        sound.play()

                    elif abs(dx) == 2 and abs(dy) == 2:  # Captura
                        medio_columna = (ficha_seleccionada.columna + columna) // 2
                        medio_fila = (ficha_seleccionada.fila + fila) // 2
                        ficha_comida = None
                        for ficha in all_sprite_list:
                            if ficha.columna == medio_columna and ficha.fila == medio_fila and ficha.color != ficha_seleccionada.color:
                                ficha_comida = ficha
                                sound.play()
                                break
                        if ficha_comida:
                            ficha_seleccionada.mover(columna, fila)
                            all_sprite_list.remove(ficha_comida)
                            turno = 'blanco' if turno == 'negro' else 'negro'
                            numero_turno += 1  # Incrementar el número de turno
                        ficha_seleccionada = None

        if event.type == pygame.KEYDOWN:
            # Si se presiona la barra espaciadora, reiniciar el juego
            if event.key == pygame.K_SPACE:
                reiniciar_juego()
                ganador = None  # Reiniciar el ganador para el siguiente juego
                victoria_detectada = False  # Resetear la bandera para permitir que se detecte la victoria nuevamente

    # Verificar ganador solo si no se ha detectado victoria previamente
    if not victoria_detectada:
        ganador, quien_gana = verificar_ganador()

        # Si hay un ganador, actualizar el contador de victorias
        if ganador:
            if quien_gana == 'ia':
                victorias_ia += 1
            elif quien_gana == 'humano':
                victorias_humano += 1

            victoria_detectada = True  # Marcar que ya se detectó un ganador

    # Verificar si es empate después de 64 turnos
    if numero_turno > 64 and not ganador:
        empates += 1
        ganador = "¡Empate!"
        victoria_detectada = True

    # Movimiento de la IA 
    if turno == 'negro' and not victoria_detectada:
        jugada = minimax()
        if jugada:
            ficha = next(ficha for ficha in all_sprite_list if ficha.color == negro)
            ficha.mover(jugada[0], jugada[1])
            turno = 'blanco'
            numero_turno += 1
            sound.play()

    # Dibujar tablero y fichas
    screen.fill((255, 255, 255))
    tablero.dibujar_grid(screen)
    all_sprite_list.draw(screen)

    # Mostrar ganador o empate
    if ganador:
        mostrar_texto(ganador, screen, 385, size=36)
        mostrar_texto("Jugar otra vez (barra espaciadora)", screen, 420, size=24)

    # Mostrar turno actual
    mostrar_texto(f"Turno {numero_turno}: {'IA' if turno == 'negro' else 'Humano'}", screen, 460, size=24)

    # Mostrar contador de victorias y empates
    mostrar_texto(f"IA: {victorias_ia}   Humano: {victorias_humano}   Empates: {empates}", screen, 480, size=24)

    pygame.display.flip()
