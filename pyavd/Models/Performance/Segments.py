from gpkit import Model, Variable, VectorVariable, Vectorize, constraints, parse_variables
from gpkit.constraints.tight import Tight
from gpkit import ureg

# Implement following models
# Takeoff
# Climb
# Cruise
# Descent
# Loiter
# Landing


class Takeoff(Model):
    def setup(self):
        constraints = []
        
        return[constraints]
        

class Segment(Model):
    def setup(self, Aircraft):
        constraints = []
        return [constraints]

