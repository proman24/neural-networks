from __future__ import print_function
import numpy as np

np.random.seed(42)


class Layer:
    """ Implements a layer module.
    A building block. Each layer is capable of performing two things:
        - Process input to get output: output = layer.forward(inputs)
        - Propagate gradients through itself: grad_input = layer.backward(inputs, gradients)
    Some layers also have learnable parameters which they update during the backward pass.
    """

    def __init__(self):
        raise NotImplementedError()

    def forward(self, inputs):
        """ Forward pass of the layer.
        Takes input data of shape [batch, input_units] 
        and returns output data [batch, output_units].
        """
        raise NotImplementedError()

    def backward(self, inputs, gradients, **kwargs):
        """ Backward pass of the layer.
        Performs a backpropagation step through the layer, with respect to the given input.
        To compute loss gradients w.r.t input, you need to apply chain rule (backprop):
            dL / dx  = (dL / dZ) * (dZ / dx)
        Luckily, we already receive dL / dZ as input, 
        so we only need to multiply it by dZ / dx.
        If our layer has parameters (e.g. dense layer, conv layer etc.), 
        you also need to update them here using dL / dZ.
        """
        raise NotImplementedError()


class Dense(Layer):
    """ A dense layer is a layer which performs a learned affine transformation:
        f(x) = <W*x> + b

    Args:
        input_units (int): incoming connections to the dense layer.
        output_units (int): number of hidden neurons in the dense layer.
    """

    def __init__(self, input_units, output_units):
        self.type = 'dense'

        # initialize weights with glorot/xavier uniform initialization
        self.weights = np.random.randn(input_units, output_units) * \
            np.sqrt(6. / (input_units + output_units))
        self.biases = np.zeros(output_units)

    def _init_g2(self):
        self.g2_weights = np.zeros_like(self.weights)
        self.g2_biases = np.zeros_like(self.biases)

    def forward(self, inputs):
        """ Forward pass of the Dense Layer.
        Perform an affine transformation:
            f(x) = <W*x> + b

        input shape: [batch, input_units] 
        output shape: [batch, output units]

        Args:
            inputs (numpy.ndarray): the outputs from previous layers.
        Returns:
            numpy.ndarray: the linear transformation applied to the inputs.
        """
        return np.dot(inputs, self.weights) + self.biases

    def backward(self, inputs, gradients, **kwargs):
        """ Backward pass of the Dense Layer.
        Computes gradient of loss w.r.t. dense layer input.

        Args:
            inputs (numpy.ndarray): the inputs to the dense layer to compute the gradients.
            gradients (numpy.ndarray): the gradients w.r.t. loss propagated back from following layers.
        Returns:
            numpy.ndarray: the gradient of loss w.r.t. dense layer inputs.
        """
        lr = kwargs.get('lr', 0.001)
        optim = kwargs.get('optim', 'rmsprop')

        # dL / dx = dL / dZ * dZ / dx = gradients * W
        grad_input = np.dot(gradients, self.weights.T)
        # m -> batch size
        m = inputs.shape[0]

        # compute gradient w.r.t. weights and biases
        # dL / dW = dL / dZ * dZ / dW = gradients * inputs
        grad_weights = np.dot(inputs.T, gradients) / m
        # dL / db = dL / dZ * dZ / db = gradients * 1
        grad_biases = gradients.sum(axis=0) / m

        assert grad_weights.shape == self.weights.shape and \
            grad_biases.shape == self.biases.shape

        update_weights = lr * grad_weights
        update_biases = lr * grad_biases

        if optim == 'rmsprop':
            gamma = kwargs.get('gamma', 0.9)
            epsilon = kwargs.get('epsilon', 1e-7)
            if not hasattr(self, 'g2_weights'):
                self._init_g2()
            self.g2_weights = (self.g2_weights * gamma) + \
                np.square(grad_weights) * (1 - gamma)
            self.g2_biases = (self.g2_biases * gamma) + \
                np.square(grad_biases) * (1 - gamma)

            self.weights -= update_weights / \
                (np.sqrt(self.g2_weights) + epsilon)
            self.biases -= update_biases / (np.sqrt(self.g2_biases) + epsilon)
        elif optim == 'gd':
            self.weights -= update_weights
            self.biases -= update_biases

        # propagate back the gradients of Loss wrt to layer inputs
        # dL / dx
        return grad_input


class ReLU(Layer):
    """ Simply applies elementwise rectified linear unit to all inputs. """

    def __init__(self):
        self.type = 'relu'

    def forward(self, inputs):
        """ Forward pass of the ReLU non-linearity.

        Args:
            inputs (numpy.ndarray): the linear transformation from dense layer.
        """
        return np.maximum(0, inputs)

    def backward(self, inputs, gradients, **kwargs):
        """ Backward pass of the ReLU non-linearity.
        Computes gradient of loss w.r.t. ReLU input.

        Args:
            inputs (numpy.ndarray): the inputs to the ReLU layer to compute the gradients.
            gradients (numpy.ndarray): the gradients w.r.t. loss propagated back from following layers.
        Returns:
            numpy.ndarray: the gradient of loss w.r.t. ReLU inputs.
        """
        grad_relu = inputs > 0
        return gradients * grad_relu
