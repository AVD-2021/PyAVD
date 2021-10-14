
'''
Baseline Configuration class for PyAVD

Handles the aircraft configuration, providing lookup functions for required parameters.

'''


class BaselineConfig:

    def __init__(self, config_file):
        self.config_file = config_file


    def K_LD_approx(self):
        return self.config_file['K_LD']


    def LD_max_approx(self):
        return self.config_file['LD_max']


    def We_parameters(self):
        return self.config_file['We_parameters']


    def WeW0(self, W0):
        '''
        Equation S 1.2-1 - Operating empty weight fraction
        '''

        return self.We_parameters[0] * W0 ** self.We_parameters[1]
    

    def W0_approx(self):
        return self.config_file['W0_approx']


    def SFC_approx(self):
        return self.config_file['SFC_approx']

