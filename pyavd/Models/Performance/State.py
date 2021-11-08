from gpkit import Model, Vectorize, VectorVariable, parse_variables
from gpkit.constraints.tight import Tight
import numpy as np


class State(Model):
    """Context for evaluating flight physics

    Variables
    ---------
    V     40       [knots]    true airspeed
    mu    1.628e-5 [N*s/m^2]  dynamic viscosity
    rho   0.74     [kg/m^3]   air density

    """
    @parse_variables(__doc__, globals())
    def setup(self):
        pass