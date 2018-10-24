from __future__ import print_function
import os

import numpy as np
from autograd import elementwise_grad as grad

from . import Dense, ReLU
from . import (
    softmax_crossentropy_with_logits,
    grad_softmax_crossentropy_with_logits
)

np.random.seed(42)

class Trainer():

    def __init__(self, dims=None):
        if dims is None:
            raise UserWarning('Model dims should not be none')
        self._create(dims)

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
        
        for layer in self._network:
            activations.append(layer.forward(A))
            A = activations[-1]
            
        assert len(activations) == len(self._network)
        return activations

    def predict(self, X):
        """
        Compute network predictions.
        """
        logits = self._forward(X)[-1]
        return logits.argmax(axis=-1)

    def fit(self, X, y, **kwargs):
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
        loss = softmax_crossentropy_with_logits(logits, y)
        grad_loss = grad_softmax_crossentropy_with_logits(logits, y)

        # Backpropagate the gradients to all layers
        for l in range(len(self._network))[::-1]:
            grad_loss = self._network[l].backward(layer_inputs[l], grad_loss, **kwargs)

        return np.mean(loss)