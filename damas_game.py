import pygame, sys, random, json, os
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

# ------------------ Configuración Q-Learning ------------------
q_table_file = "qvalues.json"
if os.path.exists(q_table_file):
    with open(q_table_file, "r") as f:
        q_table = json.load(f)
else:
    q_table = {}

# Parámetros del Q-Learning
alpha = 0.1       # Tasa de aprendizaje más alta para aprender más rápido
gamma = 0.99      # Factor de descuento más alto para priorizar recompensas a largo plazo
epsilon = 0.3     # Mayor probabilidad de exploración inicial

# Parámetros para el decaimiento de ε (epsilon)
epsilon_min = 0.1    # Valor mínimo de epsilon más alto para seguir explorando
decay_rate = 0.995   # Decaimiento más lento para explorar durante más tiempo

# Historial de movimientos de la IA durante la partida: cada entrada es (estado, acción, nuevo_estado)
ai_history = []

# Bandera para actualizar el Q-table una sola vez al finalizar la partida
q_updated = False

# --------------------- Clases y funciones ---------------------

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
    global turno, all_sprite_list, numero_turno, q_updated
    # Limpiar todas las fichas
    all_sprite_list.empty()

    # Colocar las fichas en sus posiciones iniciales
    colocar_fichas(negro, 0)  
    colocar_fichas(blanco, 3)  
    
    turno = 'negro'  
    numero_turno = 1  
    q_updated = False

# Función para obtener movimientos posibles de una ficha
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
        direcciones = [(1, 1), (-1, 1), (1, -1), (-1, -1)]

    for dx, dy in direcciones:
        nueva_columna = ficha.columna + dx
        nueva_fila = ficha.fila + dy

        # Verifica si la casilla está dentro del tablero
        if 0 <= nueva_columna < 4 and 0 <= nueva_fila < 4:
            if not casilla_ocupada(nueva_columna, nueva_fila):
                movimientos.append((nueva_columna, nueva_fila))
            else:
                # Verifica si se puede capturar una ficha
                ficha_comida = obtener_ficha(nueva_columna, nueva_fila)
                if ficha_comida and ficha_comida.color != ficha.color:
                    nueva_columna_captura = nueva_columna + dx
                    nueva_fila_captura = nueva_fila + dy
                    if 0 <= nueva_columna_captura < 4 and 0 <= nueva_fila_captura < 4:
                        if not casilla_ocupada(nueva_columna_captura, nueva_fila_captura):
                            movimientos.append((nueva_columna_captura, nueva_fila_captura))

    return movimientos

# ----------------- Funciones para Q-Learning -----------------
# Descripciones para recordar lo que hace cada función:
def obtener_estado():
    """
    Representa el estado actual del tablero como un string.
    Se recorre la lista de fichas y se crea una lista con la información de cada una.
    """
    state = []
    for ficha in all_sprite_list:
        # Representa la ficha como: (Color, columna, fila, es_dama)
        color_str = "N" if ficha.color == negro else "B"
        state.append((color_str, ficha.columna, ficha.fila, ficha.es_dama))
    state.sort()
    return str(state)

def obtener_movimiento_ia():
    """
    Obtiene una lista de movimientos posibles para las fichas de la IA (color negro).
    Cada movimiento es una tupla (ficha, (columna_destino, fila_destino))
    """
    moves = []
    for ficha in all_sprite_list:
        if ficha.color == negro:  # IA
            movs = obtener_movimientos_posibles(ficha)
            for m in movs:
                moves.append((ficha, m))
    return moves

def elegir_movimiento_ia(state, moves):
    """
    Selecciona un movimiento utilizando una estrategia ε-greedy.
    La acción se representa como una tupla: (col_inicial, fila_inicial, col_destino, fila_destino)
    """
    best_move = None
    # Exploración: con probabilidad epsilon elige un movimiento aleatorio
    if random.random() < epsilon:
        best_move = random.choice(moves)
    else:
        max_q = -float('inf')
        for ficha, move in moves:
            # Se define la acción según la posición actual de la ficha y la posición destino
            action = (ficha.columna, ficha.fila, move[0], move[1])
            # Se obtienen los Q‑valores; si no existe, se asume 0
            q_val = q_table.get(state, {}).get(str(action), 0)
            if q_val > max_q:
                max_q = q_val
                best_move = (ficha, move)
        # Si no se encontró ninguna acción (por ejemplo, si el estado no está en la tabla), se elige aleatoriamente
        if best_move is None:
            best_move = random.choice(moves)
    return best_move

def movimiento_ia():
    """
    Realiza el movimiento de la IA:
      - Obtiene el estado actual.
      - Reúne los movimientos legales.
      - Selecciona uno usando ε-greedy.
      - Ejecuta el movimiento (incluyendo captura si corresponde).
      - Registra la transición (estado, acción, nuevo estado).
    """
    global turno, numero_turno, ai_history
    current_state = obtener_estado()
    moves = obtener_movimiento_ia()
    if not moves:
        return  # No hay movimientos disponibles, la IA pierde
    ficha, move = elegir_movimiento_ia(current_state, moves)
    target_col, target_row = move
    dx = target_col - ficha.columna
    dy = target_row - ficha.fila

    # Verificar si es un movimiento de captura
    captured_piece = None
    if abs(dx) == 2 and abs(dy) == 2:
        medio_col = (ficha.columna + target_col) // 2
        medio_row = (ficha.fila + target_row) // 2
        captured_piece = obtener_ficha(medio_col, medio_row)

    # Ejecutar el movimiento
    pos_inicial = (ficha.columna, ficha.fila)  # Guardamos la posición antes de mover
    if captured_piece:
        all_sprite_list.remove(captured_piece)
    ficha.mover(target_col, target_row)
    turno = 'blanco'
    numero_turno += 1
    sound.play()
    new_state = obtener_estado()
    # Se registra la acción: (col_inicial, fila_inicial, col_destino, fila_destino)
    action = (pos_inicial[0], pos_inicial[1], target_col, target_row)
    ai_history.append((current_state, str(action), new_state))

def actualizar_q_valores(reward):
    """
    Actualiza la Q-table utilizando la ecuación de Q-Learning para cada transición registrada
    durante la partida. El parámetro 'reward' es la recompensa obtenida al finalizar la partida.
    """
    global q_table, ai_history, epsilon
    for state, action, next_state in ai_history:
        q_current = q_table.get(state, {}).get(action, 0)
        # Como la partida terminó, se asume que el máximo Q del siguiente estado es 0.
        max_next = 0  
        q_new = q_current + alpha * (reward + gamma * max_next - q_current)
        if state not in q_table:
            q_table[state] = {}
        q_table[state][action] = q_new
    # Limpiar el historial para la siguiente partida
    ai_history = []
    # Guardar la Q-table en un archivo JSON con formato
    with open(q_table_file, "w") as f:
        # Convertir el diccionario a una cadena JSON formateada
        formatted_json = json.dumps(q_table, indent=4)
        f.write(formatted_json + "\n")  # Añadir un salto de línea al final
    # Actualizar epsilon aplicando decaimiento, sin que baje de epsilon_min
    epsilon = max(epsilon_min, epsilon * decay_rate)

# ------------------ Inicialización del juego ------------------

# Colocar fichas iniciales
tablero = Tablero()
colocar_fichas(negro, 0)
colocar_fichas(blanco, 3)

ficha_seleccionada = None
ganador = None
movimientos_posibles = []

sound = pygame.mixer.Sound("movimiento.mp3")
pygame.mixer.music.load("ost.mp3")
pygame.mixer.music.play(10)

# Bucle principal
start = True
inicio_espera = pygame.time.get_ticks()  
while start:
    # Esperar 1 segundo antes de iniciar el juego
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

            # Solo se permite la interacción para el humano (fichas blancas)
            if turno == 'blanco':
                if not ficha_seleccionada:
                    for ficha in all_sprite_list:
                        if ficha.rect.collidepoint(pos) and ficha.color == blanco:
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
                            turno = 'negro'
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
                                turno = 'negro'
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

    # Si es el turno de la IA (negro) y no hay ganador, la IA toma su movimiento
    if turno == 'negro' and not ganador:
        movimiento_ia()

    # Verificar ganador solo si no se ha detectado victoria previamente
    if not q_updated:
        ganador, quien_gana = verificar_ganador()

        # Si hay un ganador, actualizar el contador de victorias y actualizar la Q-table
        if ganador:
            if quien_gana == 'ia':
                victorias_ia += 1
                actualizar_q_valores(1)
            elif quien_gana == 'humano':
                victorias_humano += 1
                actualizar_q_valores(-1)
            else:
                actualizar_q_valores(0)
            q_updated = True

    # Verificar si es empate después de 64 turnos
    if numero_turno > 64 and not ganador:
        empates += 1
        ganador = "¡Empate!"
        if not q_updated:
            actualizar_q_valores(0)
            q_updated = True

    # Dibujar tablero y fichas
    screen.fill((255, 255, 255))
    tablero.dibujar_grid(screen)
    all_sprite_list.draw(screen)

    # Resaltar la ficha seleccionada (solo para el humano)
    if ficha_seleccionada:
        pygame.draw.rect(screen, resaltado, (ficha_seleccionada.rect.x - 5, ficha_seleccionada.rect.y - 5, 60, 60), 3)

    # Mostrar movimientos posibles (solo para el humano)
    for movimiento in movimientos_posibles:
        columna_mov, fila_mov = movimiento
        pygame.draw.circle(screen, movimiento_posible, (columna_mov * TCELDA + TCELDA // 2, fila_mov * TCELDA + TCELDA // 2), 10)

    # Mostrar ganador o empate
    if ganador:
        mostrar_texto(ganador, screen, 385, size=36)
        mostrar_texto("Jugar otra vez (barra espaciadora)", screen, 420, size=24)

    # Mostrar turno actual
    mostrar_texto(f"Turno {numero_turno}: {'IA' if turno == 'negro' else 'Humano'}", screen, 460, size=24)

    # Mostrar contador de victorias y empates
    mostrar_texto(f"IA: {victorias_ia}   Humano: {victorias_humano}   Empates: {empates}", screen, 480, size=24)

    pygame.display.flip()