from .. import u

from .Fuselage import Fuselage
from .Wing import Wing
from .Engine import Engine
from .UC import UC
from .Empennage import Empennage

from gpkit import Model, Vectorize, VectorVariable, parse_variables
from gpkit.constraints.tight import Tight
import numpy as np


class AircraftPerformance(Model):
    """Aircraft performance model

    Variables
    ---------
    Wfuel  [kg]  fuel weight
    Wburn  [kg]  segment fuel burn

    Upper Unbounded
    ---------------
    Wburn, aircraft.wing.c, aircraft.wing.A

    Lower Unbounded
    ---------------
    Wfuel, aircraft.W, state.mu

    """
    @parse_variables(__doc__, globals())
    def setup(self, aircraft, state):
        self.aircraft = aircraft
        self.state = state

        self.wing_aero = aircraft.wing.dynamic(aircraft.wing, state)
        self.perf_models = [self.wing_aero]

        W = aircraft.W
        S = aircraft.wing.S

        V = state.V
        rho = state.rho

        D = self.wing_aero.D
        CL = self.wing_aero.CL

        return Wburn >= 0.1*D, W + Wfuel <= 0.5*rho*CL*S*V**2, {
            "performance":
                self.perf_models}



class Aircraft(Model):
    """The Aircraft model

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
        self.fuse = Fuselage()
        self.wing = Wing()
        self.components = [self.fuse, self.wing]

        return [W >= sum(c.W for c in self.components),
                self.components]
    
    # Dynamic performance model - creates instance of AircraftPerformance()
    dynamic = AircraftPerformance

