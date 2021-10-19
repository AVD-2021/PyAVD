from ..Tools import stub
import numpy as np


class BaselineConfig:
    """
    Baseline Configuration class for PyAVD

    ---> Handles the top-level aircraft configuration, providing empirical lookup tables for required parameters.

    Attributes
    ----------
    config : dict
        Dictionary containing the baseline configuration.

    
    Methods (Public)
    -------
        LD_max_approx()
            LD_max approximator

        W0_approx()
            W0 approximator
    """


    def __init__(config, config_file=None):
        config.raw = config_file


    @stub
    def W0_approx(config):
        None


    @stub
    def K_LD_lookup(config):
        None

    
    @stub
    def A_wetted_lookup(config):
        None


    @stub
    def SFC_approx(config):
        None


    def LD_max_approx(config):
        '''Uses wetted aspect ratio and K_LD to approximate LDmax'''

        config.approxLDmax = config.K_LD_lookup() * np.sqrt(config.A_wetted())
