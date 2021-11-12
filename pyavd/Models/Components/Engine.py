from gpkit import Model, Vectorize, VectorVariable, parse_variables, ureg as u
from gpkit.constraints.tight import Tight
import numpy as np


class Engine(Model):
    """Engine model

    Variables
    ---------
    W  [kg]  Weight
    
    """
    @parse_variables(__doc__, globals())
    def setup(self):
        constraints = self.constraints  = []
        components  = self.components   = []

        # Engine weight is sum of its components - note the tight constraint
        constraints += [Tight([W >= sum(comp.W for comp in components)])]


        return [constraints, components]