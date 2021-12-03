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
    Cd0                         [-]             Zero-lift drag coefficient
    x_cg                        [m]             Longitudinal centre of gravity location
    z_cg                        [m]             Vertical centre of gravity location
    Vstall_TO                   [m/s]           Stall speed (Takeoff)
    Vstall_LD                   [m/s]           Stall speed (Landing)


    """
    @parse_variables(__doc__, globals())
    def setup(self, aircraft, state):
        self.aircraft   = aircraft
        self.state      = state
        perf_models     = self.perf_models  = []
        constraints     = self.constraints  = {}

        # Adding individual component performance models
        # perf_models     += aircraft.wing.dynamic(aircraft.wing, state)
        # perf_models     += aircraft.engine.dynamic(aircraft.engine, state)
        # perf_models     += aircraft.empennage.dynamic(aircraft.empennage, state)
        # perf_models     += aircraft.fuselage.dynamic(aircraft.fuselage, state)
        # perf_models     += aircraft.uc.dynamic(aircraft.uc, state)

        # Add dynamic models to each component, even if blank (None)
        [perf_models.append(model.dynamic(model, state)) for model in aircraft.components]

        # Whole aircraft performance constraints
        W               = aircraft.M_0 * 9.81 * (u.m/u.s**2)
        Sref            = aircraft.wing.Sref
        U               = state.U
        rho             = state.rho


        # xcg constraints - derived from the weighted average of the aircraft components and systems x_cg
        constraints.update({"Longitudinal CG" : Tight([
                    x_cg >= (sum(c.x_cg * c.M for c in aircraft.components) + sum(s.x_cg * s.M for s in aircraft.systems)) / aircraft.M_dry                       ])})

        # Same for z_cg
        constraints.update({"Vertical CG" : Tight([
                    z_cg >= (sum(c.z_cg * c.M for c in aircraft.components) + sum(s.z_cg * s.M for s in aircraft.systems)) / aircraft.M_dry                       ])})


        # TODO: make a drag model for the aircraft - ie topic 4 eqns go here
        # D = self.wing_aero.D
        # CL = self.wing_aero.CL
        
        return {"Performance": perf_models, "constraints": constraints}

'''
Note: x_cg is a derived variable from the aircraft components and systems - similar implementation as M_0
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
    g               9.81        [m/s^2]         Gravitational Acceleration
    LD_max                      [-]             Maximum Lift to Drag ratio
    K_LD            15.5        [-]             K_LD empirical coefficient | Civil Jets
    Sw_Sref         6.0         [-]             Wetted Area to Reference Area ratio
    x_cg                        [m]             Body-fixed x-axis component of center of gravity
    x_ac_w          6.65        [m]             Position of 1/4 chord of wing
    x_ac_h          13.5        [m]             Aerodynamic Center of Tailplane
    l_h             7.05        [m]             Relative longitudinal distance between the wing and tailplane
    h_h             4.73        [m]             Relative vertical distance between wing and tailplane
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

        components      += [payload, fuse, wing, engine, H_tail, V_tail, uc]
        

        constraints.update({"Dry Mass" : Tight([
                    M_dry >= sum(c.M for c in components) + sum(s.M for s in systems)])})
        

        constraints.update({"Total Mass" : Tight([
                    M_0 >= M_fuel + M_dry])})

        # Stuff from S1 initial sizing
        # constraints.update({"LDmax ratio (approx)" : [
        #             LD_max == K_LD * (AR/Sw_Sref)**0.5          ]})

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
        # constraints.update({"Minimum Cd0" : [
        #             self.Cd0 >= 1e-6]})

        # constraints.update({"Minimum Wing Loading" : [
        #             self.W0_S >= 0.1 * u.N / u.m**2]})

        # constraints.update({"Maximum Thrust to Weight" : [
        #             self.T0_W0 <= 1]})

        self.constraints.update({"Boundary Constraints": constraints})
