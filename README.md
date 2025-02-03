# IA-Checkers RL
Resumen: Programa ejecutable desarrollado en Python que tiene un agente inteligente que juega damas contra humanos utilizando el algoritmo de Q-learning.

## Instalaciones necesarias
 1) Visual Studio Code
 2) Python v3.12.6
 3) Pygame

* Instrucciones para instalar
1) Instalar Visual Studio Code: https://code.visualstudio.com/Download
2) Instalar Python: https://www.python.org/downloads/
3) Ejecutar en consola el comando: pip install pygame

## Pasos para la ejecución del código

1) Realizar las instalaciones previamente mostradas.
2) Ejecutar el comando <b>pip installa pygame</b> para la utilizar la libreria gráfica.
3) Clonar este repositorio.
4) Abrir Visual Studio Code e ir a la ruta del repositorio clonado.
5) En la barra superior derecha / botón de play / desplegar la lista y hacer click en 'Run Python File'
6) Jugar.


### Información complementaria
Este programa utiliza el <b>algoritmo de Q-learning</b> bajo el <b>criterio de recompensas en capturas de fichas adversarias y castigos con fichas pérdidas</b>, para hacer que un agente inteligente pueda jugar Damas. El agente <b>aprende con el archivo qvalues.json</b>, el cual <b>contiene los resultados de todas las partidas que ha jugado</b> con el adversario (humano), cuando termina una partida <b>el resultado se guarda de manera automática en el archivo</b> previamente mencionado (se registran las victorias,derrotas y empates del agente), con dicho archivo <b>el agente aprende y mejora la toma decisiones</b> al realizar una acción en el juego. 

#### Manual de usuarios
El tablero contiene 4 fichas, 2 para cada jugador, blancas y negras, el jugador puede moverse en diagonal hacia adelante haciendo <b>CLICK IZQUIERDO</b> en la ficha que desea mover y posteriormente haciendo click en las casillas diagonales disponibles (si estan vacias), para capturar fichas rivales el usuario debe hacer <b>CLICK IZQUIERDO</b> en la ficha a jugar y si tiene una ficha en diagonal cuya casilla posterior en diagonal esta libre entonces hacer click en dicha casilla para capturar.Al llegar al extremo opuesto del tablero las fichas serán promovidas a damas y por ende podran moverse adelante y hacia atras en diagonal. Si ambos jugadores llegan al turno 64 entonces se declara en tablas la partida (empate). En el caso de que uno de los jugadores logre vencer al rival se sumara +1 al contador de victorias y podrá jugar una nueva partida presionando la <b>'BARRA ESPACIADORA'</b>.

