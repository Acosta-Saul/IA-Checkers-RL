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
resaltado = (0, 255, 0)  # Color para resaltar la ficha seleccionada
movimiento_posible = (0, 0, 255)  # Color para mostrar movimientos posibles

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
        self.es_dama = False  # Indica si la ficha es una dama

    def mover(self, nueva_columna, nueva_fila):
        self.columna = nueva_columna
        self.fila = nueva_fila
        self.rect.x = nueva_columna * TCELDA + (TCELDA - 50) // 2
        self.rect.y = nueva_fila * TCELDA + (TCELDA - 50) // 2

        # Promover a dama si llega al extremo opuesto
        if not self.es_dama:
            if (self.color == negro and nueva_fila == 3) or (self.color == blanco and nueva_fila == 0):
                self.es_dama = True
                pygame.draw.circle(self.image, (255, 215, 0), (25, 25), 8)  # Marcar como dama


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


# Función para obtener la ficha en una casilla
def obtener_ficha(columna, fila):
    for ficha in all_sprite_list:
        if ficha.columna == columna and ficha.fila == fila:
            return ficha
    return None


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


# Función para obtener movimientos posibles
def obtener_movimientos_posibles(ficha):
    movimientos = []
    direcciones = []

    # Direcciones para fichas normales
    if not ficha.es_dama:
        if ficha.color == negro:
            direcciones = [(1, 1), (-1, 1)]  # Diagonal hacia adelante para negras
        else:
            direcciones = [(1, -1), (-1, -1)]  # Diagonal hacia adelante para blancas
    else:
        # Direcciones para damas (adelante y atrás)
        direcciones = [(1, 1), (-1, 1), (1, -1), (-1, -1)]

    for dx, dy in direcciones:
        nueva_columna = ficha.columna + dx
        nueva_fila = ficha.fila + dy

        # Verificar si la casilla está dentro del tablero
        if 0 <= nueva_columna < 4 and 0 <= nueva_fila < 4:
            if not casilla_ocupada(nueva_columna, nueva_fila):
                movimientos.append((nueva_columna, nueva_fila))
            else:
                # Verificar si se puede capturar una ficha
                ficha_comida = obtener_ficha(nueva_columna, nueva_fila)
                if ficha_comida and ficha_comida.color != ficha.color:
                    nueva_columna_captura = nueva_columna + dx
                    nueva_fila_captura = nueva_fila + dy
                    if 0 <= nueva_columna_captura < 4 and 0 <= nueva_fila_captura < 4:
                        if not casilla_ocupada(nueva_columna_captura, nueva_fila_captura):
                            movimientos.append((nueva_columna_captura, nueva_fila_captura))

    return movimientos


# Colocar fichas iniciales
tablero = Tablero()
colocar_fichas(negro, 0)
colocar_fichas(blanco, 3)

ficha_seleccionada = None
ganador = None
movimientos_posibles = []

# Bandera para evitar incremento repetido de victorias
victoria_detectada = False

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
                        movimientos_posibles = obtener_movimientos_posibles(ficha)
                        break
            else:
                # Mover ficha si la casilla está en los movimientos posibles
                if (columna, fila) in movimientos_posibles:
                    dx = columna - ficha_seleccionada.columna
                    dy = fila - ficha_seleccionada.fila

                    # Movimiento simple
                    if abs(dx) == 1 and abs(dy) == 1:
                        ficha_seleccionada.mover(columna, fila)
                        turno = 'blanco' if turno == 'negro' else 'negro'
                        numero_turno += 1
                        ficha_seleccionada = None
                        movimientos_posibles = []
                        sound.play()

                    # Captura
                    elif abs(dx) == 2 and abs(dy) == 2:
                        medio_columna = (ficha_seleccionada.columna + columna) // 2
                        medio_fila = (ficha_seleccionada.fila + fila) // 2
                        ficha_comida = obtener_ficha(medio_columna, medio_fila)
                        if ficha_comida:
                            ficha_seleccionada.mover(columna, fila)
                            all_sprite_list.remove(ficha_comida)
                            turno = 'blanco' if turno == 'negro' else 'negro'
                            numero_turno += 1
                            sound.play()
                        ficha_seleccionada = None
                        movimientos_posibles = []

                else:
                    # Deseleccionar la ficha si se hace clic en otra casilla
                    ficha_seleccionada = None
                    movimientos_posibles = []

        if event.type == pygame.KEYDOWN:
            # Si se presiona la barra espaciadora, reiniciar el juego
            if event.key == pygame.K_SPACE:
                reiniciar_juego()
                ganador = None
                victoria_detectada = False

    # Verificar ganador solo si no se ha detectado victoria previamente
    if not victoria_detectada:
        ganador, quien_gana = verificar_ganador()

        # Si hay un ganador, actualizar el contador de victorias
        if ganador:
            if quien_gana == 'ia':
                victorias_ia += 1
            elif quien_gana == 'humano':
                victorias_humano += 1

            victoria_detectada = True

    # Verificar si es empate después de 64 turnos
    if numero_turno > 64 and not ganador:
        empates += 1
        ganador = "¡Empate!"
        victoria_detectada = True

    # Dibujar tablero y fichas
    screen.fill((255, 255, 255))
    tablero.dibujar_grid(screen)
    all_sprite_list.draw(screen)

    # Resaltar la ficha seleccionada
    if ficha_seleccionada:
        pygame.draw.rect(screen, resaltado, (ficha_seleccionada.rect.x - 5, ficha_seleccionada.rect.y - 5, 60, 60), 3)

    # Mostrar movimientos posibles
    for movimiento in movimientos_posibles:
        columna, fila = movimiento
        pygame.draw.circle(screen, movimiento_posible, (columna * TCELDA + TCELDA // 2, fila * TCELDA + TCELDA // 2), 10)

    # Mostrar ganador o empate
    if ganador:
        mostrar_texto(ganador, screen, 385, size=36)
        mostrar_texto("Jugar otra vez (barra espaciadora)", screen, 420, size=24)

    # Mostrar turno actual
    mostrar_texto(f"Turno {numero_turno}: {'IA' if turno == 'negro' else 'Humano'}", screen, 460, size=24)

    # Mostrar contador de victorias y empates
    mostrar_texto(f"IA: {victorias_ia}   Humano: {victorias_humano}   Empates: {empates}", screen, 480, size=24)

    pygame.display.flip()