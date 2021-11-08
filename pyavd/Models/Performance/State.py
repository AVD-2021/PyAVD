from gpkit import Model, Vectorize, VectorVariable, parse_variables
from gpkit.constraints.tight import Tight
from gpkit.nomials.variables import Variable
import numpy as np
from ambiance import Atmosphere


class State(Model):
    """Context for evaluating flight physics

    Variables
    ---------
    V            [knots]    True airspeed
    alt          [m]        Altitude

    """
    @parse_variables(__doc__, globals())
    def setup(self):

        # Maybe better to have a vector for atmospheric states?
        
        mu = Variable("mu", Atmosphere(alt).dynamic_viscosity, "N*s/m^2", "")

        pass