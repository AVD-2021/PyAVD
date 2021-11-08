from gpkit import Model, Variable, VectorVariable, Vectorize, parse_variables
from gpkit.constraints.tight import Tight
from gpkit import ureg


class UC(Model):
    """Undercarriage model

    Variables
    ---------
    W  [kg]  weight

    Upper Unbounded
    ---------------
    W

    Lower Unbounded
    ---------------

    """
    @parse_variables(__doc__, globals())
    def setup(self):
        constraints = []
        components = self.components = []

        # Undercarriage weight is sum of its components - note the tight constraint
        if len(components) > 0:
            constraints += [Tight([W >= sum(comp.W for comp in components)])]


        return [constraints, components]