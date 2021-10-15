
'''
Baseline Configuration class for PyAVD

- Handles the top-level aircraft configuration, providing empirical lookup tables for required parameters.

'''

class BaselineConfig:

    def __init__(self, config_file):
        self.raw = config_file


    def K_LD_approx(self):
        return self.raw['K_LD']


    def LD_max_approx(self):
        return self.raw['LD_max']


    def We_parameters(self):
        return self.raw['We_parameters']


    def WeW0(self, W0):

        # Equation S 1.2-1 - Operating empty weight fraction
        return self.We_parameters()[0] * W0 ** self.We_parameters()[1]
    

    def W0_approx(self):
        return self.raw['W0_approx']


    def SFC_approx(self):
        return self.raw['SFC_approx']

