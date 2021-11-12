from gpkit import Model, Variable, VectorVariable, Vectorize, parse_variables
from gpkit.constraints.tight import Tight
from gpkit import ureg as u


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