from __future__ import print_function
import os
import dill

import numpy as np

import loss
from layers import Dense, ReLU

np.random.seed(42)

class Trainer():

    def __init__(self, dims=None, name='model', pretrained=False, lr=0.001):
        self._name = name
        if pretrained:
            self._load_model()
        elif dims is None:
            raise UserWarning('Model dims should not be none')
        else:
            self._create(dims)
        self._lr = lr
        self._alpha = 0.99
        self._epsilon = 1e-8

    def _create(self, dims):
        model = []
        input_shape = dims[0]
        num_classes = dims[-1]
        model.append(Dense(input_shape, dims[1]))
        model.append(ReLU())
        for i in range(2, len(dims) - 1):
            model.append(Dense(dims[i - 1], dims[i]))
            model.append(ReLU())
        model.append(Dense(dims[-2], num_classes))
        self._network = model

    def _forward(self, X):
        """ Compute activations of all network layers by 
        applying them sequentially. Return a list of activations 
        for each layer. Make sure last activation corresponds to network logits.
        """
        activations = []
        A = X
        it = 0
        for layer in self._network:
            if np.isnan(np.sum(A)):
                print('nan')
                print(it)
                print(layer)
                exit(0)
            activations.append(layer.forward(A))
            A = activations[-1]
            it += 1
        assert len(activations) == len(self._network)
        return activations

    def predict(self, X):
        """
        Compute network predictions.
        """
        logits = self._forward(X)[-1]
        return logits.argmax(axis=-1)

    def fit(self, X, y):
        """ Train your network on a given batch of X and y.
        You first need to run forward to get all layer activations.
        Then you can run layer.backward going from last to first layer.

        After you called backward for all layers, all Dense layers 
        have already made one gradient step.
        """

        # Get the layer activations
        layer_activations = self._forward(X)
        layer_inputs = [X] + layer_activations  #layer_input[i] is an input for network[i]
        logits = layer_activations[-1]

        # Compute the loss and the initial gradient
        objective = loss.softmax_crossentropy_with_logits(logits, y)
        grad_objective = loss.grad_softmax_crossentropy_with_logits(logits, y)

        # Backpropagate the gradients to all layers
        for l in range(len(self._network))[::-1]:
            grad_objective = self._network[l].backward(layer_inputs[l], grad_objective, 
                            lr=self._lr, alpha=self._alpha, epsilon=self._epsilon)

        return np.mean(objective)

    def save_model(self):
        if not os.path.isdir('models'):
            os.mkdir('models')
        with open('models/{}.dill'.format(self._name), 'wb') as dill_file:
            dill.dump(self._network, dill_file)
        print('Model saved to `models/{}.dill`'.format(self._name))

    def _load_model(self):
        with open('models/{}.dill'.format(self._name), 'rb') as dill_file:
            self._network = dill.load(dill_file)