from gpkit import Model, Variable, VectorVariable, Vectorize, parse_variables
from gpkit.constraints.tight import Tight
from gpkit import ureg

# Implement following models
# Takeoff
# Climb
# Cruise
# Descent
# Loiter
# Landing


class Segment(Model):
    def setup(self):
        constraints = []
        return [constraints]
