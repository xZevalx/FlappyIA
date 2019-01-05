from ia.Neuron import Neuron, InputNeuron

import numpy as np


class NeuronLayer:

    def __init__(self, ninputs, neurons, learning_rate=.1, neuron_type=Neuron):
        """

        :param ninputs:
        :param neurons:
        :param neuron_type:
        """
        self.neurons = [neuron_type(ninputs=ninputs, learning_rate=learning_rate) for _ in range(neurons)]
        self.outputs = [0 for _ in range(neurons)]

    def feed_forward(self, inputs):
        for index, neuron in enumerate(self.neurons):
            self.outputs[index] = neuron.guess(inputs)
        return self.outputs

    def update_output_deltas(self, expected_output):
        for i in range(len(expected_output)):
            error = expected_output[i] - self.neurons[i].output
            self.neurons[i].update_delta(error=error)

    def update_hidden_deltas(self, weights, deltas):
        for i in range(len(self.neurons)):
            error = np.sum(weights[i] * deltas[i])
            self.neurons[i].update_delta(error=error)

    def get_weights_matrix(self):
        weights_matrix = []
        for neuron in self.neurons:
            weights_matrix.append(neuron.weights)

        return np.array(weights_matrix).T

    def get_deltas_matrix(self, required):
        deltas_matrix = []
        for neuron in self.neurons:
            deltas_matrix.append([neuron.delta])
        deltas_matrix *= required

        return np.array(deltas_matrix)

    def update_neuron_params(self):
        for neuron in self.neurons:
            neuron.adjust_neuron_params()

    def __len__(self):
        return self.get_number_of_neurons

    @property
    def get_number_of_neurons(self):
        return len(self.neurons)

    @property
    def get_neuron_class(self):
        return type(self.neurons[0])


class InputLayer(NeuronLayer):

    def __init__(self, neurons):
        super().__init__(ninputs=1, neurons=neurons, neuron_type=InputNeuron)

    def feed_forward(self, inputs):
        # TODO: Lanzar error de cuando la cantidad de inputs es incorrecta
        assert len(inputs) == len(self.neurons)
        for i in range(len(self.neurons)):
            self.outputs[i] = self.neurons[i].guess(inputs[i])

        return self.outputs
