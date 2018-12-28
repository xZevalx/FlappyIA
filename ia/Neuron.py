import numpy as np


def random_weights(n):
    return (np.random.rand(n) - 0.5) * 10


def random_bias():
    return (np.random.random() - 0.5) * 10


class Neuron:

    def __init__(self, ninputs=1, bias=None, weights=None, learning_rate=.1):
        """
        Inicializa una neurona.

        :param ninputs: Número de entradas que puede recibir
        :param bias: Si no es entregado se setea aleatoriamente un número real entre -5 y 5
        :param weights: Lista de pesos del mismo tamaño ninputs. Si no es entregado se setea aleatoriamente un número
                        real entre -5 y 5
        :param learning_rate: Taza de aprendizaje
        """
        if weights is None:
            self.weights = random_weights(ninputs)
        else:
            assert len(weights) == ninputs
            self.weights = np.array(weights)
        self.bias = bias if bias else random_bias()
        self.ninputs = ninputs
        self.lr = learning_rate
        self.delta = 0
        self._last_inputs = None
        self.output = None

    def guess(self, x):
        """
        Procesa las entradas usando la función de activación

        :param x: Lista de tamaño self.ninputs
        :return: Predicción
        """
        assert len(x) == self.ninputs
        weighted_sum = np.dot(x, self.weights) + self.bias

        self._last_inputs = np.array(x)

        self.output = self.activation_function(weighted_sum)
        return self.output

    def activation_function(self, x):
        """
        Función de activación. Por defecto retorna la entrada

        :param x: Ponderación de la entrada y los pesos de la neurona sumado a bias
        :return: Número
        """
        return x

    def update_delta(self, error):
        """
        Actualiza derivada de la neurona. Implementa backpropagation

        """
        self.delta = error * self.output * (1.0 - self.output)

    def adjust_neuron_params(self):
        """
        Ajusta pesos y bias de acuerdo a la derivada calculada

        :return:
        """
        movement = self.lr * self.delta
        self.weights += (movement * self._last_inputs)
        self.bias += movement


class Perceptron(Neuron):

    def activation_function(self, x):
        return int(x > 0)


class Sigmoid(Neuron):

    def activation_function(self, x):
        return 1.0 / (1.0 + np.exp(-x))


class InputNeuron(Neuron):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ninputs = 1
        self.weights = [1]
        self.bias = 0

    def guess(self, x):
        return x

    def update_delta(self, error):
        pass

    def adjust_neuron_params(self):
        pass


if __name__ == '__main__':
    # NAND example
    weights = [-2, -2]
    pct = Perceptron(2, bias=3, weights=weights)
    print(pct.guess([0, 0]))
    print(pct.guess([0, 1]))
    print(pct.guess([1, 1]))
    print(pct.guess([1, 0]))
