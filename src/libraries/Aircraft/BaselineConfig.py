
'''
Baseline Configuration class for PyAVD

- Handles the top-level aircraft configuration, providing empirical lookup tables for required parameters.

'''

from ..Tools.decorators import stub


class BaselineConfig:

    def __init__(self, config_file=None):
        self.raw = config_file


    @stub
    def K_LD_approx(self):
        return self.raw['K_LD']


    @stub
    def LD_max_approx(self):
        return self.raw['LD_max']
        
    
    @stub
    def WfW0(self):
        return self.raw['WfW0']
    

    @stub
    def W0_approx(self):
        return self.raw['W0_approx']


    @stub
    def SFC_approx(self):
        return self.raw['SFC_approx']

