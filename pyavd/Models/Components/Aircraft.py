from .Fuselage      import *
from .Payload       import *
from .Wing          import *
from .Engine        import *
from .UC            import *
from .Empennage     import *

from gpkit import Model, Vectorize, VectorVariable, parse_variables, ureg as u
from gpkit.constraints.tight import Tight
import numpy as np


class AircraftPerformance(Model):
    """Aircraft performance model

    Variables
    ---------

    """
    @parse_variables(__doc__, globals())
    def setup(self, aircraft, state):
        self.aircraft   = aircraft
        self.state      = state
        perf_models     = self.perf_models  = []

        perf_models     += aircraft.wing.dynamic(aircraft.wing, state)
        perf_models     += aircraft.engine.dynamic(aircraft.engine, state)

        # TODO: add the empennage, fuselage, engine and UC aero performance models
        # perf_models     += aircraft.empennage.dynamic(aircraft.empennage, state)
        # perf_models     += aircraft.fuselage.dynamic(aircraft.fuselage, state)
        # perf_models     += aircraft.uc.dynamic(aircraft.uc, state)
        

        W               = aircraft.W
        S               = aircraft.wing.S
        V               = state.V
        rho             = state.rho


        # D = self.wing_aero.D
        # CL = self.wing_aero.CL
        
        return {"Performance": perf_models}

'''
    M_dry                       [kg]          Aircraft Dry Mass
'''

class Aircraft(Model):
    """The Aircraft model

    Variables
    ---------
    M_0                         [kg]            Total Mass
    M_fuel                      [kg]            Starting Fuel Mass
    M_dry                       [kg]            Aircraft Dry Mass
    T0_W0                       [-]             Design Thrust to Weight ratio
    W0_S                        [N/m^2]         Design Wing Loading
    Cd0                         [-]             Zero-lift drag coefficient
    g               9.81        [m/s^2]         Gravitational Acceleration
    LD_max                      [-]             Maximum Lift to Drag ratio
    K_LD            15.5        [-]             K_LD empirical coefficient | Civil Jets
    Sw_Sref         6.0         [-]             Wetted Area to Reference Area ratio
    x_cg            ??6.32??    [m]             Body-fixed x-axis component of center of gravity
    x_ac_w          6.65        [m]             Position of 1/4 chord of wing
    x_ac_h          ??13.5???   [m]             Aerodynamic Center of Tailplane
    l_h             7.05        [m]             Relative longitudinal distance between the wing and tailplane
    h_h             ??4.73??    [m]             Relative vertical distance between wing and tailplane
    l_f             13.5        [m]             Length of the Fuselage
    w_f             1.70        [m]             Length of the Wing
    n_engines       2           [-]             Number of Engines


    Upper Unbounded
    ---------------
    W0_S, T0_W0, Cd0

    Lower Unbounded
    ---------------
    T0_W0, W0_S

    
    SKIP VERIFICATION

    """

    # Dynamic performance model - clones AircraftPerformance()
    dynamic = AircraftPerformance

    @parse_variables(__doc__, globals())
    def setup(self, CL_max=2.1, CL_clean=1.5, AR=7.5, e=0.9, emp_config="T-tail"):
        components      = self.components   = []
        systems         = self.systems      = []
        constraints     = self.constraints  = {}

        # Hyperparameters from the user - TODO: remove these
        self.CL_max     = CL_max
        self.CL_clean   = CL_clean
        self.AR         = AR
        self.e          = e
        self.emp_config = emp_config

        # Note that {str_} = Starboard, {prt_} = Port
        # Also order of initialization is important - some components depend on quantities from others!
        payload         = self.payload      = Payload()     
        fuse            = self.fuse         = Fuselage()
        wing            = self.wing         = Wing()
        engine          = self.engine       = Engine()
        H_tail          = self.H_tail       = H_Tail()
        V_tail          = self.V_tail       = V_Tail()
        uc              = self.uc           = UC()
        # str_engine      = self.str_engine   = Starboard_Engine()
        # prt_engine      = self.prt_engine   = Port_Engine()

        components      += [payload, engine]        
        # components      += [payload, fuse, str_wing, prt_wing, str_engine, prt_engine, empennage, uc]
        
        constraints.update({"Dry Mass" : Tight([
                    M_dry >= sum(c.M for c in self.components) + sum(s.M for s in systems)])})

        # M_dry = self.M_dry = sum(c.M for c in self.components) + sum(s.M for s in systems) ----> Hacky attempt
        
        constraints.update({"Total Mass" : Tight([
                    M_0 >= M_fuel + M_dry])})

        # M_0 = self.M_0 = M_fuel + M_dry ----> Hacky attempt

        constraints.update({"LDmax ratio (approx)" : [
                    LD_max == K_LD * (AR/Sw_Sref)**0.5          ]})

        # Add bounding constraints - temporary
        self.boundingConstraints()

        return [constraints, components]


    def boundingConstraints(self):
        constraints = {}

        ### TODO: remove temporary lower bound constraints

        constraints.update({"Minimum Fuel Mass" : [
                    self.M_fuel >= 10 * u.kg, self.M_fuel <= 100000 * u.kg]})

        # constraints.update({"Total Mass Boundaries" : [
        #             100000 * u.kg >= self.M_0]})
        
        # Minimum Cd0
        constraints.update({"Minimum Cd0" : [
                    self.Cd0 >= 1e-6]})

        # constraints.update({"Minimum Wing Loading" : [
        #             self.W0_S >= 0.1 * u.N / u.m**2]})

        # constraints.update({"Maximum Thrust to Weight" : [
        #             self.T0_W0 <= 1]})

        self.constraints.update({"Boundary Constraints": constraints})
