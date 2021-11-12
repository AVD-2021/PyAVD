from gpkit import Model, Vectorize, VectorVariable, parse_variables, ureg as u
from gpkit.constraints.tight import Tight
import numpy as np


class UC(Model):
    """Undercarriage model

    Variables
    ---------
    W   [kg]  weight

    """
    @parse_variables(__doc__, globals())
    def setup(self):
        constraints = []
        components = self.components = []

        # Undercarriage weight is sum of its components - note the tight constraint
        if len(components) > 0:
            constraints += [Tight([W >= sum(comp.W for comp in components)])]


        return [constraints, components]