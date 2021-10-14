
'''
Baseline Configuration class for PyAVD

Handles the aircraft configuration, providing lookup functions for required parameters.

'''

class Config:

    def __init__(self, config_file):
        self.config_file = config_file

    def K_LD_approx(self):
        return self.config_file['K_LD']

    def LD_max_approx(self):
        return self.config_file['LD_max']

    def We_parameters(self):
        return self.config_file['We_parameters']
    
    def W0_approx(self):
        return self.config_file['W0_approx']

    def SFC_approx(self):
        return self.config_file['SFC_approx']

