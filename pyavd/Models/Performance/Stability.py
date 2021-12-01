from gpkit import ureg as u
import numpy as np
import sympy as sym



class Stability:
    """Stability model"""

    def __init__(self, solved_model):

        # Adding converged solution to the class for later use
        # Note we aren't passing the gpkit models here, just the converged solution...
        self.aircraft = solved_model

        
        # Initializing Variables
        self.CM_f                   = 0
        self.x_np                   = 0
        self.SM_Poff                = 0
        self.SM_Pon                 = 0
        self.htailplane_adj_cl      = 0
        self.dCM_dalpha             = 0
        self.z_t                    = 0
        self.g                      = 9.81          # Yes yes its hacky but idc it works


        # Calculating variables ----> Nah m8 call this in the outer Model, dont call 'get' methods from __init__... Unless you really want to
        # self.calc_fuseCm(fuselage, wing, aircraft)
        # self.calc_depsilon_dalpha(wing, aircraft)


    def calc_fuseCm(self):
        """
        Input requires value import from the fuselage and wing model 
        """

        aircraft = self.aircraft

        # TODO: if extra time, look at datcom 1978 or elsewhere for equation to calculate K_f

        input_to_kf         = aircraft.wing.qc / aircraft.fuselage.length
        
        # Initialise maxCringe()
        if input_to_kf == 0.1:      K_f = 0.06
        elif input_to_kf == 0.2:    K_f = 0.246    
        elif input_to_kf == 0.3:    K_f = 0.6
        elif input_to_kf == 0.4:    K_f = 1.0    
        elif input_to_kf == 0.5:    K_f = 1.6
        elif input_to_kf == 0.6:    K_f = 2.8

        # aircraft.fuselage.width is max fuselage width!
        # TODO: add references
        self.CM_f = K_f * (aircraft.fuselage.length * aircraft.fuselage.width ** 2) / (aircraft.wing.c * aircraft.wing.S)

        return self.CM_f



    def calc_SM(self):           # When you name a function like this, you're doing it wrong if you dont return anything...

        aircraft    = self.aircraft
        SM_Poff     = self.SM_Poff      = (self.x_np - aircraft.x_cg) / aircraft.wing.c

        if aircraft.engine.location == "under-mounted":
            self.SM_Pon = SM_Poff - 0.02

        elif aircraft.engine.location == "aft-mounted":
            self.SM_Pon = SM_Poff + 0.01   # worst case, was +0.01 or +0.02

        # return self.SM_Poff, self.SM_Pon ---> Do you want to have it like this?
    


    def calc_depsilon_dalpha(self):

        aircraft    = self.aircraft
        wing        = aircraft.wing        # Parce que readability
        
        K_a         = 1 / wing.AR - 1 / (1 + wing.AR ** 1.7)
        K_lambda    = (10 - 3 * wing.taper) / 7.0
        K_h         = (1 - np.abs(aircraft.h_h / wing.b) ) / np.cbrt(2 * aircraft.l_h / wing.b)             # ---> Tis a constant, doesn't need unit conversions...

        self.correction_factor = 1  #TODO: we need the lift curve slope of the wing (at M and M=0), for all flight speeds

        # This will likely break cos of the powers, may need to use ureg.magnitude - check!
        self.depsilon_dalpha = 4.44 * (K_a * K_lambda * K_h * np.sqrt(np.cos(wing.sweep.to(u.radian)) ** 1.19)) * self.correction_factor

        # return self.depsilon_dalpha




    def x_np(self):

        aircraft    = self.aircraft
        wing        = aircraft.wing        # Parce que readability
        wingAero    = wing.dynamic
        H_tail      = aircraft.H_tail
        H_tailAero  = H_tail.dynamic

        # Note: all CL_alpha are evaluated at the flight AoA ----> Do u mean cruise? No? All the flight segments including landing and takeoff
        self.htailplane_adj_cl = H_tail.eta_h  * H_tail.CL_alpha_h * (1 - H_TailAero.depsilon_dalpha) * (H_tail.s_h / wing.Sref)

        numerator   = wing.CL_alpha_w * (aircraft.ac_w / wing.c) - self.CM_f + self.htailplane_adj_cl * (aircraft.x_ac_h / wing.c)
        denominator = wingAero.CL_alpha_w + self.htailplane_adj_cl

        self.x_np =  wing.c.to(u.meter) * (numerator / denominator)

        # return self.x_np


    def calc_dCM_dalpha(self):

        aircraft    = self.aircraft
        wing        = aircraft.wing 
        wingAero    = wing.dynamic
        H_tail      = aircraft.H_tail
        H_tailAero  = H_tail.dynamic

        self.dCM_dalpha = -wingAero.CL_alpha * (aircraft.ac_w - aircraft.x_cg) / wing.c + self.CM_f - self.htailplane_adj_cl * (aircraft.x_ac_h - aircraft.x_cg) / wing.c

        # return self.dCM_dalpha



    # Trim stuff should really get its own class - specific to different flight regimes - discussed with Cooper some time ago



    ## TRIM ANALYSIS


    def calc_CL_w(self, a_infty):
        wing        = self.aircraft.wing

        return wing.CL_alpha * (a_infty + wing.i_w - wing.alpha_0)

    def calc_CL_h(self, a_infty, i_h):
        aircraft    = self.aircraft
        wing        = aircraft.wing 
        wingAero    = wing.dynamic
        H_tail      = aircraft.H_tail
        H_tailAero  = H_tail.dynamic
        
        return H_tail.CL_alpha_h * ((a_infty + wingAero.i_w - wingAero.alpha_0)*(1 - H_TailAero.depsilon_dalpha) + (i_h - wing.i_w)-(H_tailAero.alpha_0 - wingAero.alpha_0)) + H_tailAero.CL_delta_e * H_tailAero.delta_e

    # Get alpha and setting angle (elevator angle)
    def calc_iH_alphaInfty(self, state):
        aircraft    = self.aircraft
        wing        = aircraft.wing 
        wingAero    = wing.dynamic
        H_tail      = aircraft.H_tail
        H_tailAero  = H_tail.dynamic

        i_h, alpha_infty = sym.symbols('i, a')          

        # L = W
        # mass here is the mass at current flight segment (state.M)
        eq1 = sym.Eq(self.calc_CL_w(alpha_infty) + H_tailAero.eta_h * H_tailAero.S_h / wing.Sref * self.calc_CL_h(alpha_infty, i_h), 2 * state.M * self.g / (state.rho * state.U**2 * wing.Sref))


        K_w = 1 / (np.pi * wing.AR * wing.e)
        K_h = 1 / (np.pi * H_tail.AR * H_tail.e_h)

        # D = T
        # Fast syntax check pls 
        # Also cant extract Thrust from Engine model, will exist in the Mission model somewhere in the engine performance model for a given flight regime
        eq2 = sym.Eq(aircraft.Cd0 + K_w * self.calc_CL_w(alpha_infty)**2 + H_tail.eta_h * K_h * H_tail.S_h / wing.Sref * self.calc_CL_h(alpha_infty, i_h)**2, 2 * state.T / (state.rho * state.U**2 * wing.Sref))

        result = self.result = sym.solve([eq1, eq2], (i_h, alpha_infty))

        [self.i_h, self.alpha_infty] = result

        return result


    def calc_CM_0w(self):
        wing        = self.aircraft.wing

        # sweep is in rad and at the 1/4 chord pos, twist is in deg
        # CM0_af is the incompressible airfoil zero lift pitching moment
        self.CM_0w = (wing.CM0_af * (wing.AR * np.cos(wing.sweep.to(u.radians))**2)/(wing.AR + 2 * np.cos(wing.sweep.to(u.radians))) - 0.01 * wing.twist.to(u.degrees)) * self.correction_factor
    

    def calc_Zt(self, state):
        aircraft    = self.aircraft
        wing        = aircraft.wing
        H_tail   = aircraft.H_tail

        lift_term =  - self.calc_CL_w(self.alpha_infty) * (wing.ac_w- aircraft.x_cg) / wing.c
        tailplane_term = - H_tail.eta_h * self.calc_CL_h(self.alpha_infty) * ((H_tail.S) / wing.Sref) * (aircraft.x_ac_h - aircraft.cg) / wing.c
        q = 0.5 * state.U**2 * state.rho

        self.z_t = -wing.Sref * wing.c * q * (lift_term + self.CM_0w + self.CM_f * self.alpha_infty + tailplane_term) / state.T             # Change T after finishing segments class

        return self.z_t


""""
Variables we need:

1. lift curve slope of the wing (M=0 and M at all segment's flight speed) --> correction factor --> (defined without value)

2. Thrust (just some stupid simple equation, cruise -> T=D, descent & ascent -> find T needed for wanted descent/ascent rate)

3. CL_alpha_h (M=0 and M at all segment's flight speed) --> (defined without value)

4. Oswald efficiency of the tailplane (e_h) --> (defined without value)
 
6. wing setting angle (i_w) --> (defined without value)

7. tailplane zero lift AoA (alpha_0) --> (defined without value)

8. Lift coefficient wrt to the change of the elevator angle (CL_delta_e) --> (defined without value)

9. incompressible airfoil zero lift pitching moment (CM0_af) -- > Nuclino 5.5-3 (NOT defined, from aerofoil data)

"""
