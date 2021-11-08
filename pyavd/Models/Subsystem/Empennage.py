from gpkit import Model, Variable, VectorVariable, Vectorize, parse_variables
from gpkit.constraints.tight import Tight
from gpkit import ureg


class Empennage(Model):

    def setup(self):
        constraints = []
        components = self.components = []