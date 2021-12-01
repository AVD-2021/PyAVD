from gpkit import Model, Vectorize, VectorVariable, parse_variables, ureg as u
from gpkit.constraints.tight import Tight
import numpy as np


class EnginePerformance(Model):
    """Engine performance model

    Variables
    ---------


    """
    @parse_variables(__doc__, globals())
    def setup(self, engine, state):
        return None


class Engine(Model):
    """Engine model

    Variables
    ---------
    M               1500       [kg]             Mass
    sfc_cruise      0.8        [1/hr]           Specific Fuel Consumption at Cruise
    sfc_loiter      0.7        [1/hr]           Specific Fuel Consumption at Loiter
    BPR                        [-]              Engine Bypass Ratio
    Tstatic_To                 [N]              Static Thrust at Takeoff
    T_max                      [N]              Maximum Thrust
    x_cg                       [m]              x Center of Gravity location
    z_cg                       [m]              z Center of Gravity location

    """

    dynamic = EnginePerformance

    @parse_variables(__doc__, globals())
    def setup(self, reverse=False):
        constraints = self.constraints  = []
        components  = self.components   = []




        return [constraints, components]
    
    


# Aliases - unused at the moment
class Starboard_Engine(Engine):
    def setup(self): return super().setup()


class Port_Engine(Engine):
    def setup(self): return super().setup()
