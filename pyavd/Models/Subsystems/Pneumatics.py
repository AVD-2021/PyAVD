from gpkit import Model, Vectorize, VectorVariable, parse_variables, ureg as u
from gpkit.constraints.tight import Tight
import numpy as np


class Pneumatics(Model):
    """Pneumatics system model

    Variables
    ---------
    W           [kg]        Weight
    x_cg            10.5       [m]              x Center of Gravity location
    z_cg                   [m]              z Center of Gravity location
    """
    @parse_variables(__doc__, globals())
    def setup(self):
        constraints = self.constraints  = []
        components  = self.components   = []

        # Pneumatics weight is sum of its components - note the tight constraint
        constraints += [Tight([W >= sum(comp.W for comp in components)])]

        constraints += [Tight([])]


        return [constraints, components]