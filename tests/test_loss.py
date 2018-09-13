import sys
sys.path.append('../')

import unittest
import numpy as np

from loss import Losses
from util import eval_numerical_gradient

class TestLoss(unittest.TestCase):

    def test_crossentropy_loss_NUMERICAL_GRADIENT_CHECK(self):
        logits = np.linspace(-1, 1, 500).reshape([50, 10])
        answers = np.arange(50) % 10
        Losses.softmax_crossentropy_with_logits(logits, answers)
        grads = Losses.grad_softmax_crossentropy_with_logits(logits, answers)
        numeric_grads = eval_numerical_gradient(lambda l: Losses.softmax_crossentropy_with_logits(l, answers).mean(), logits)
        
        self.assertTrue(np.allclose(numeric_grads, grads, rtol=1e-3, atol=0), 
            msg="The reference implementation has just failed. Someone has just changed the rules of math.")