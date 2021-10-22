import numpy as np
from .. import ureg


class Config:
    """
    Configuration class for PyAVD

    ---> Handles the top-level aircraft configuration, providing empirical lookup tables for required parameters in addition to higher fidelity methods.

    Attributes
    ----------
    config : dict
        Dictionary describing the aircraft's baseline configuration.

    
    Methods (Public)
    -------
        LD_max_approx()
            LD_max approximator

        W0_approx()
            W0 approximator
    """


    def __init__(config, config_file=None):
        config.raw = config_file

        config.W0_approx()
        config.K_LD_lookup()
        config.A_wetted_lookup()
        config.SFC_approx()
        config.LD_max_approx()


    def W0_approx(config):

        # Bit of a meh intial guess - can refine
        return 15000 * ureg.kg


    def K_LD_lookup(config):

        # For now, just returns for civil jets
        config.K_LD = 15.5

    
    def A_wetted_lookup(config):
        config.A_wetted = 6


    def SFC_approx(config):
        # will find engine database and test all engines from there from lower to higher SFC, until they pass all the constraints
        # might be worth developing a merit index craeted by us (cost?) 
    
        # config.approxSFC = config.approxLDmax * 0.866
        config.SFC_cruise_approx = 22.7 * ureg.mg / (ureg.N * ureg.s)
        config.SFC_loiter_approx = 19.8 * ureg.mg / (ureg.N * ureg.s)


    def LD_max_approx(config):
        '''Uses wetted aspect ratio and K_LD to approximate LDmax'''

        config.approxLDmax = config.K_LD * np.sqrt(config.A_wetted)