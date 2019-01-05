import multiprocessing as mp
from queue import Empty as EmptyQueue
from datetime import datetime

from game.flappy import FlappyGame, GameStates, K_SPACE, K_RETURN
from ia.EvolutionaryNetwork import NetworkOrganism, GeneticAlg, network_fitness, selection_function
from copy import copy

JUMP_KEY = K_SPACE
START_KEY = K_RETURN
RESET_KEY = K_RETURN

ACTIONS_DICT = {START_KEY: 0, JUMP_KEY: 0, RESET_KEY: 0}

JUMP_ACTION = copy(ACTIONS_DICT)
JUMP_ACTION[JUMP_KEY] = 1
START_ACTION = copy(ACTIONS_DICT)
START_ACTION[START_KEY] = 1
RESET_ACTION = copy(ACTIONS_DICT)
RESET_ACTION[RESET_KEY] = 1


def run(game_instance, state_queue, actions_queue):
    print("Corriendo Flappy ...")
    game_instance.execute(state_queue, actions_queue)
    print("Juego terminado")
    exit(0)


def ia_player_handler(player, action_queue, state, data=None):
    """
    Hace jugar a un jugador artificial.
    Retorna True si aún está jugando. False si ya terminó
    """
    if state == GameStates.START:
        action_queue.put(START_ACTION)
        return True
    elif state == GameStates.RESET:
        player.fitness = data  # Actualiza el score
        # start = datetime.now()
        # while True:
        #     actions_queue.put(RESET_ACTION)  # Trata de resetear el juego durante 1 segundo
        #     if (datetime.now() - start).total_seconds() > 1:
        #         break
        actions_queue.put(RESET_ACTION)
        return False
    elif state == GameStates.PLAYING:
        network_output = player.network.feed_forward(data)  # Recibe la data de distancias
        perform_jump = True if network_output[0] > 0.5 else False  # Transformar salida de la red a si salta o no salta
        if perform_jump:
            action_queue.put(JUMP_ACTION)
        return True


if __name__ == '__main__':
    # Set neural networks to evolve

    GA = GeneticAlg(pop_size=20, organism_type=NetworkOrganism, fitness_function=network_fitness,
                    selection_function=selection_function, mutation_rate=.1)

    # Init and run game
    game = FlappyGame()
    state_queue = mp.Queue()
    actions_queue = mp.Queue()
    game_process = mp.Process(target=run, args=(game, state_queue, actions_queue))
    game_process.start()

    players = iter(GA.population)
    current_player = next(players)

    # Play the game
    while game_process.is_alive():
        try:
            game_state, player_data = state_queue.get()
            # Tomar un individuo de la población y hacer que juegue
            # Cuando llegue a reset:
            #    - Actualizar fitness del individuo
            #    - Cambiar a otro individuo
            # Cuando no queden mas individuos, reproducir nueva generación.
            # Repetir hasta n_generations

            # print(game_state, player_data)

            if not ia_player_handler(current_player, actions_queue, game_state, player_data):
                try:
                    print("El jugador ha sido cambiado")
                    current_player = next(players)
                except StopIteration as e:  # Se han usado todos los players de esta generación
                    print("Usando generación nueva ")
                    GA.breed_new_generation()
                    print("Fitness última generación")
                    print(GA.fitness)
                    players = iter(GA.population)
                    current_player = next(players)

        except EmptyQueue as e:
            print(e)
            print("No se ha recibido más estados desde el juego")
            game_process.terminate()
    game_process.join()

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
