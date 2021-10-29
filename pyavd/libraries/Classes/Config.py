from .. import ureg
from .Spec import Spec
from .Standards import Standards

import numpy as np


class Config(Spec, Standards):
    """
    Configuration class for PyAVD

    ---> Handles the top-level aircraft configuration, providing empirical lookup tables for required parameters in addition to higher fidelity methods.
    """

    def __init__(config, AR, e):

        config.aspect_ratio = AR
        config.e = e

        config.W0_approx()
        config.K_LD_lookup()
        config.wetted_Area_lookup()
        config.A_wetted_lookup()
        config.SFC_approx()
        config.LD_max_approx()
        config.CD0_calculation()
        

    def W0_approx(config):

        # Bit of a meh initial guess - can refine
        config.W0 = 5000 * ureg.kg


    def K_LD_lookup(config):

        # For now, just returns for civil jets
        config.K_LD = 15.5


    def CD0_calculation(config):
        config.Cd0 = (np.pi * config.aspect_ratio * config.e) / ((2.0 * config.LDmax)**2)


    def wetted_Area_lookup(config):
        config.wetted_area_ratio = 6.0

    
    def A_wetted_lookup(config):
        # config.aspect_ratio = 7.5     # Blag this (curr Raymer 4.3.1)
        # TODO: this 6 value should be determined via a function by using the type of aircraft; it should not be hardcoded;
        config.A_wetted = config.aspect_ratio / config.wetted_area_ratio


    def SFC_approx(config):
        # will find engine database and test all engines from there from lower to higher SFC, until they pass all the constraints
        # might be worth developing a merit index created by us (cost?) 
    

        # config.SFC_cruise_approx = 22.7 * ureg.mg / ureg.N * ureg.s)
        # config.SFC_loiter_approx = 19.8 * ureg.mg / (ureg.N * ureg.s)

        config.SFC_cruise_approx = 0.8 * 1 / ureg.hour
        config.SFC_loiter_approx = 0.7 * 1 / ureg.hour


    def LD_max_approx(config):
        '''Uses wetted aspect ratio and K_LD to approximate LDmax'''

        config.LDmax = config.K_LD * np.sqrt(config.A_wetted)
        config.LD_cruise = config.LDmax * 0.866
        config.LD_loiter = config.LDmax
