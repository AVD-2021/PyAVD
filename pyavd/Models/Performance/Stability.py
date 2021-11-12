from gpkit import Model, Variable, VectorVariable, Vectorize, parse_variables
from gpkit.constraints.tight import Tight
from gpkit import ureg as u


class Stability(Model):
    """Stability model

    Variables
    ---------

    """
    @parse_variables(__doc__, globals())
    def setup(self):
        constraints = self.constraints  = []

        return [constraints]