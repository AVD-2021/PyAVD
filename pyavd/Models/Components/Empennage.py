from gpkit import Model, Variable, VectorVariable, Vectorize, parse_variables
from gpkit.constraints.tight import Tight
from gpkit import ureg


class Empennage(Model):
    """Empennage model

    Variables
    ---------
    M         [kg]          Mass

    """
    @parse_variables(__doc__, globals())
    def setup(self):
        constraints = []
        components = self.components = []

        # Add components of the empennage
        tailplane = self.tailplane = Tailplane()

        # Concatenate components
        components += [tailplane]

        # Empennage weight is sum of its components - note the tight constraint
        if len(components) > 0:
            constraints += [Tight([M >= sum(comp.M for comp in components)])]


        return [constraints, components]



### Tailplane class with eta_h, CLalpha_h, x_ac_h, S_h, l_h, h_h
class Tailplane(Model):
    """Tailplane model

    Variables
    ---------
    M                       [kg]            Mass
    CL_alpha_h                [-]             Lift Curve Slope for Tailplane at current AoA

    """
    @parse_variables(__doc__, globals())
    def setup(self, empennage_config, ):
        constraints = []
        components = self.components = []

        #TODO: airfoil class to re-use for tailplane, wing, cannard etc
        # airfoil = self.airfoil = NACA0015() or whatever

        if empennage_config     == "T-Tail":    eta_h = Variable("eta_h", 1.0, "Horizontal Tailplane Efficiency")
        elif empennage_config   == "Low-Tail":  eta_h = Variable("eta_h", 0.9, "Horizontal Tailplane Efficiency")

        # Tailplane weight is sum of its components
        # Note the use of the tight constraint set - doesn't enforce equality but throws helpful loose warning
        if len(components) > 0:
            constraints += [Tight([M >= sum(comp.M for comp in components)])]


        return [constraints, components]