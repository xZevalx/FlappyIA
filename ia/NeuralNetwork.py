from ia.NeuronLayer import NeuronLayer, InputLayer
from ia.Neuron import Neuron, Perceptron, Sigmoid

import numpy as np


def mean_squared_error(y1, y2):
    return np.sum((np.array(y1) - np.array(y2)) ** 2) / len(y1)


class NeuralNetwork:

    def __init__(self, layers_conf, learning_rate=.1, neuron_type=Neuron):
        self.layers = []

        self.layers.append(InputLayer(neurons=layers_conf[0]))

        for i in range(1, len(layers_conf)):
            nneurons = layers_conf[i]
            inputs_next_layer = layers_conf[i - 1]
            self.layers.append(NeuronLayer(ninputs=inputs_next_layer, neurons=nneurons, learning_rate=learning_rate,
                                           neuron_type=neuron_type))

        self.input_layer = self.layers[0]
        self.output_layer = self.layers[-1]
        self.lr = learning_rate

    def feed_forward(self, inputs):
        out = inputs
        for layer in self.layers:
            out = layer.feed_forward(out)
        return out

    def train(self, train_values, expected_output):
        # Feed network
        network_output = self.feed_forward(train_values)

        # Deltas update
        self.output_layer.update_output_deltas(expected_output=expected_output)

        for i in range(len(self.layers) - 2, 0, -1):  # We omit InputLayer
            weights_matrix = self.layers[i + 1].get_weights_matrix()
            deltas_matrix = self.layers[i + 1].get_deltas_matrix(required=len(self.layers[i].neurons))
            self.layers[i].update_hidden_deltas(weights=weights_matrix, deltas=deltas_matrix)

        # Weights and bias update

        for layer in self.layers[1:]:  # We omit InputLayer
            layer.update_neuron_params()

        return mean_squared_error(network_output, expected_output)

    def epoch_training(self, dataset, epoch=100):
        """

        :param dataset: list of tuples(input, expected values)
        :param epoch: Times to train the network
        :return: list with epoch errors
        """
        errors = []
        for e in range(epoch):
            print('Epoch {} de {}. Learning rate {}'.format(e+1, epoch, self.lr))
            epoch_error = 0
            for training_input, expected_value in dataset:
                epoch_error += self.train(training_input, expected_value)
            errors.append(epoch_error/len(dataset))
        return errors

    def get_layers(self):
        """ Returns all layers except InputLayer """
        return self.layers[1:]

    def set_layers(self, layers):
        """ Set self.layers from layers, excluding InputLayer """
        self.layers[1:] = layers
        self.output_layer = self.layers[-1]
