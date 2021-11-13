from gpkit import Model, Variable, VectorVariable, Vectorize, parse_variables
from gpkit.constraints.tight import Tight
from gpkit import ureg


class Cabin(Model):
    def setup(self):
        constraints = []
        components = self.components = []

        self.W = W = Variable("W", "kg", "Fuselage Weight")

        # Fuselage weight is sum of its components - note the tight constraint means equality
        if len(components) > 0:
            constraints += [Tight([W >= sum(comp.W for comp in components)])]

        return [constraints, components]



class Fuselage(Model):
    """Fuselage model

    Variables
    ---------
    W  [kg]   weight
    t  [in]   wall thickness
    b  [in]   width
    h  [in]   height
    """
    
    def setup(self):
        constraints = []

        cabin = self.cabin = Cabin()

        components = self.components = []

        W = self.W = Variable("W", "kg", "Fuselage Weight")

        # Fuselage weight is sum of its components - note the tight constraint means equality
        if len(components) > 0:
            constraints += [Tight([W >= sum(comp.W for comp in components)])]

        return [components, constraints]


# TODO: implement proper constraints for this docstring
    """Fuselage model

    Variables
    ---------
    W  [kg]   weight
    t  [in]   wall thickness
    b  [in]   width
    h  [in]   height

    Upper Unbounded
    ---------------
    h, t, b, W

    Lower Unbounded
    ---------------
    h, t, b

    """