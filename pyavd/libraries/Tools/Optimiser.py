from scipy.optimize import minimize
import numpy as np


class Optimiser:
    def __init__(opti, weights, type='SLSQP'):
        opti.weights = weights


    def _objective(opti, params):
        """
        Simple dot product of parameters and weights
        """
        return np.dot(params, opti.weights)
