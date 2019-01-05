from ia.genetic_algorithm import IOrganism, GeneticAlg
from ia.NeuralNetwork import NeuralNetwork, Sigmoid

import random
from datetime import datetime
from copy import copy
from numpy import argsort

random.seed(datetime.now().second)


class NetworkOrganism(IOrganism):
    """
    Esta clase contiene la representación de una red neuronal que consiste en un arreglo las capas de la red.
    Esta representación es útil a la hora de hacer crossover de organismos para evolucionar la red, pues solo se
    mezclan las neuronas entre las mismas capas.
    El fitness de este organismo es el puntaje obtenido en el juego.
    """

    def __init__(self, *args, **kwargs):
        self.network = None
        super().__init__(*args, **kwargs)

    def spontaneous_generation(self, size):
        """
        La red ya genera automáticamente neuronas con sus pesos y bias de forma aleatoria, así que usamos eso y
        extraemos las capas que sirven como representación
        """
        self.network = NeuralNetwork(layers_conf=[3, 8, 8, 8, 1], learning_rate=.1, neuron_type=Sigmoid)
        self.representation = self.network.get_layers()

    def mutate(self, *args, **kwargs):
        """ Realiza mutaciones aleatorias en cada capa."""
        for layer in self.representation:
            # Solo algunas neuronas mutan
            for idx_neuron in range(len(layer.neurons)):
                if random.random() < 0.1:
                    layer.neurons[idx_neuron].randomize()
        self.network.set_layers(self.representation)

    def breed(self, organism):
        """ Realiza crossover de neuronas para cada capa """
        brood_repr = []
        for i in range(len(self.representation)):
            layer1 = self.representation[i]
            layer2 = organism.representation[i]
            brood_repr.append(NetworkOrganism.crossover_layers(layer1, layer2))
            #brood_repr.append(NetworkOrganism.average_layers(layer1, layer2))

        new_network = copy(self.network)
        new_network.set_layers(brood_repr)
        new_organism = NetworkOrganism(representation=brood_repr)
        new_organism.network = new_network

        return new_organism

    @staticmethod
    def crossover_layers(layer1, layer2):
        """
        Realiza entrecruzamiento en dos puntos entre capas.
        Importante recordar que aquí se trabaja con objetos NeuronLayer
        """
        assert len(layer1) == len(layer2)
        crossover_point1 = int(len(layer1) * random.random())
        crossover_point2 = int(len(layer1) * random.random())
        crossover_point1 = min(crossover_point1, crossover_point2)
        crossover_point2 = max(crossover_point1, crossover_point2)
        new_layer = copy(layer1)
        new_layer.neurons[crossover_point1:crossover_point2] = layer2.neurons[crossover_point1:crossover_point2]
        return new_layer

    @staticmethod
    def average_layers(layer1, layer2):
        assert len(layer1) == len(layer2)
        new_layer = copy(layer1)
        for i in range(len(new_layer)):
            new_layer.neurons[i].weights = (layer1.neurons[i].weights + layer2.neurons[i].weights) / 2
            new_layer.neurons[i].bias = (layer1.neurons[i].bias + layer2.neurons[i].bias) / 2
        return new_layer



def network_fitness(network_organism):
    """
    El fitness del organismo es el score obtenido en el juego el cual es actualizado una vez que ha terminado de jugar.
    Por lo tanto aquí solo lo retornamos
    """
    return network_organism.fitness


def selection_function(organisms, fitnesses, return_best=True):
    """ Ordena de menor a mayor fitness (score) """
    sorted_indexes = argsort(fitnesses)
    organisms = organisms[sorted_indexes]
    return organisms[int(len(organisms) / 2):], organisms[-1]
