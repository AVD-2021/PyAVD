from ..Tools import stub


class BaselineConfig:
    '''
    Baseline Configuration class for PyAVD

    ---> Handles the top-level aircraft configuration, providing empirical lookup tables for required parameters.


    Attributes
    ----------
        raw : dict
            Raw configuration dictionary
    
    Methods
    -------
        K_LD_approx()
            Lookup table for K_LD

        LD_max_approx()
            LD_max approximator

        WfW0()
            WfW0 approximator

        W0_approx()
            W0 approximator

        SFC_approx()
            Lookup table for SFC
    '''

    def __init__(self, config_file=None):
        self.raw = config_file


    @stub
    def K_LD_lookup(self):
        return None


    @stub
    def LD_max_approx(self, A_wetted):
        return None
    

    @stub
    def Brequet_range(self):
        return None

    
    @stub
    def Brequet_endurance(self):
        return None


    @stub
    def WfW0(self):
        return None
    

    @stub
    def W0_approx(self):
        return None


    @stub
    def SFC_approx(self):
        return None
