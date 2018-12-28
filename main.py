from game.flappy import FlappyGame, GameStates

if __name__ == '__main__':
    game = FlappyGame()
    game.execute()


"""
TODO: 

- Ver como simular el input según el estado del juego
    estado == START
        -> iniciar el juego
    estado == PLAYING
        -> jugar
    estado == RESET
        -> reintentar

- Crear red genética que aprenda sola de acuerdo al score obtenido
- Los inputs de la red son 3:
    -> Distancia al suelo
    -> Distancia al extremo superior derecho del tubo inferior del frente
    -> Distancia al extremo inferior derecho del tubo superior del frente
- La salida de la red es un real entre 0 y 1
- Se debe interpretar la salida
    -> Si la salida es menor a 0.5 el ave no salta
    -> Si la salida es mayor a 0.5 el ave salta
    
- El proceso de aprendizaje genético crea organismos que contienen los pesos
  de las neuronas de la red.
- Un objeto neural network debe ser capaz de retornar sus pesos en algún formato
- Un objeto neural network debe ser capaz de recibir/cargar pesos desde alguna estructura de datos

- Para ejecutar el juego y la red al mismo tiempo se usarán procesos.
- El proceso del juego escribirá en un archivo de texto las distancias en cada frame
- El proceso de la red leerá esas distancias y decidirá saltar o no
    
"""