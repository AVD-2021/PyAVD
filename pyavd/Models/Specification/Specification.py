from gpkit import Model, Variable, VectorVariable, Vectorize, parse_variables
from gpkit.constraints.tight import Tight
from gpkit import ureg


class Specification(Model):
    """FAR25 specification - for commercial transport aircraft 

    Variables
    ---------------

    """
    def setup(self, aircraft):

        # All operational constraints go here - returned at end


        return []