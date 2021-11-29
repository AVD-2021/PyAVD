from logging import WARNING
from gpkit import Model, Variable, VectorVariable, Vectorize, parse_variables
from gpkit.constraints.tight import Tight
from gpkit import ureg as u
import numpy as np
# import sympy as sym           ---> cringeee why dis


"""
temp - remove dis
    x_np                            [m]             Neutral Point Position
    depsilon_dalpha                 [-]             Rate of Change of Downwash with AoA (@M0)       
    fuse_Cm                         [-]             Pitching Moment Coefficient of Fuselage
    Kn_on                           [-]             Static Margin (w/ thrust)
    adjusted_htail_cl               [-]             Pre-determined value to ease complexity in code
    dCM_dalpha                      [-]             Rate of change of Moment coefficient with AoA w.r.t to cg 
"""


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
        self.depsilon_dalpha        = 0
        self.dCM_dalpha             = 0
        self.z_t                    = 0


        # Calculating variables ----> Nah m8 call this in the outer Model, dont call 'get' methods from __init__... Unless you really want to
        # self.get_fuseCm(fuselage, wing, aircraft)
        # self.get_depsilon_dalpha(wing, aircraft)


    def get_fuseCm(self):
        """
        Input requires value import from the fuselage and wing model 
        """

        aircraft = self.aircraft

        # TODO: if extra time, look at datcom 1978 or elsewhere for equation to calculate K_f

        input_to_kf         = aircraft.wing.qc / aircraft.fuselage.length
        
        # Initialise maxCringe()
        if input_to_kf == 0.1:
            K_f = 0.06
        elif input_to_kf == 0.2:
            K_f = 0.246    
        elif input_to_kf == 0.3:
            K_f = 0.6
        elif input_to_kf == 0.4:
            K_f = 1.0    
        elif input_to_kf == 0.5:
            K_f = 1.6
        elif input_to_kf == 0.6:
            K_f = 2.8

        # aircraft.fuselage.width is max fuselage width!
        # TODO: add references
        self.CM_f = K_f * (aircraft.fuselage.length * aircraft.fuselage.width ** 2) / (aircraft.wing.c * aircraft.wing.S)

        return self.CM_f



    def get_SM(self):           # When you name a function like this, you're doing it wrong if you dont return anything...

        aircraft    = self.aircraft
        SM_Poff     = self.SM_Poff      = (self.x_np - aircraft.x_cg) / aircraft.wing.c

        if aircraft.engine.location == "under-mounted":
            self.SM_Pon = self.SM_Poff - 0.02

        elif aircraft.engine.location == "aft-mounted":
            self.SM_Pon = self.SM_Poff + 0.01   # worst case, was +0.01 or +0.02

        # return self.SM_Poff, self.SM_Pon ---> Do you want to have it like this?
    


    def get_depsilon_dalpha(self):

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
        empennage   = aircraft.empennage

        # Note: all CL_alpha are evaluated at the flight AoA ----> Do u mean cruise?
        self.htailplane_adj_cl = empennage.eta_h  * empennage.CL_alpha_h * (1 - self.depsilon_dalpha) * (empennage.s_h / wing.Sref)

        numerator   = wing.CL_alpha_w * (aircraft.ac_w / wing.c) - self.CM_f + self.htailplane_adj_cl * (aircraft.ac_h / wing.c)
        denominator = wing.CL_alpha_w + self.htailplane_adj_cl

        self.x_np =  wing.c.to(u.meter) * (numerator / denominator)

        # return self.x_np


    def get_dCM_dalpha(self):

        aircraft    = self.aircraft
        wing        = aircraft.wing        # Parce que readability

        self.dCM_dalpha = -wing.CL_alpha_w * (aircraft.ac_w - aircraft.x_cg) / wing.c + self.CM_f - self.htailplane_adj_cl * (aircraft.ac_h - aircraft.x_cg) / wing.c

        # return self.dCM_dalpha




    # Trim stuff should really get its own class - specific to different flight regimes - discussed with Cooper some time ago





    ## TRIM ANALYSIS


    def get_CL_w(self, a_infty):

        return wing.CL_alpha_w * (a_infty + wing.i_w - wing.alpha_0)

    def get_CL_h(self, a_infty, i_h):
        
        return (wing.CL_alpha_h * ((a_infty + wing.i_w - wing.alpha_0) * (1-self.depsilon_dalpha)+(i_h-wing.i_w)-(empennage.alpha_0_h-wing.alpha_0)) + empennage.CL_delta_e * empennage.delta_e)

    # get alpha and setting angle (elevator engle)
    def get_iH_alphaInfty(self):

        i_h, alpha_infty = sym.symbols('i, a')

        # L = W       
        eq1 = sym.Eq(self.get_CL_w(wing, a) + empennage.eta_h * empennage.S.to(u.meters**2) / wing.S.to(u.meter**2) * self.get_CL_h(wing, empennage, a, i), 2 * aircraft.weight / (raihaan.rho * raihaan.U**2 * wing.S))


        K_w = 1/(np.pi * wing.AR * wing.e)
        K_h = 1/(np.pi * empennage.AR_h * empennage.e_h)

        # D = T
        eq2 = sym.Eq(aircraft.Cd0 + K_w * self.get_CL_w(wing, a)**2 + empennage.eta_h * K_h * empennage.S.to(u.meters**2) / wing.S.to(u.meter**2) * self.get_CL_h(wing, empennage, a, i)**2, 2 * Engine.T / (raihaan.rho * raihaan.U**2 * wing.S))

        result = sym.solve([eq1,eq2],(i,a))


    def get_CM_0w(self):

        # sweep is in rad and at the 1/4 chord pos, twist is in deg
        # CM0_af is the imcompressible airfoil zero lift pitching moment
        self.CM_0w = (wing.CM0_af * (wing.AR * np.cos(wing.sweep.to(u.radians))**2)/(wing.AR + 2 * np.cos(wing.sweep.to(u.radians))) - 0.01 * wing.twist.to(u.degrees)) * self.correction_factor


    def get_Zt(self):

        lift_term =  - self.get_CL_w(wing, fetch_from_result_of_function_above) * (wing.ac_w.to(u.meter)- aircraft.cg.to(u.meter)) / wing.c.to(u.meter)

        tailplane_term = - empennage.eta_h * self.get_CL_h(wing, empennage, fetch_from_above, fetch_from_abv) * ((empennage.S.to(u.meter**2)) / wing.S.to(u.meter**2)) * (empennage.ac_h.to(u.meter) - aircraft.cg.to(u.meter)) / wing.c.to(u.meter)

        q = 0.5 * raihaan.U**2 * raihaan.rho

        self.z_t = -wing.S.to(u.meter) * wing.c.to(u.meter) * q * (lift_term + self.CM_0w + self.CM_f * fetch_from_above + tailplane_term) / Engine.T


""""
Variables we need:

1. lift curve slope of the wing (M=0 and M at all segment's flight speed) --> correction factor 
2. density (rho) 
3. speed (U)
4. x_cg: 20ft (approx atm)
5. Thrust 
6. wing sweep: 9 degrees (might change soon)
7. wing taper: 0.22 
8. position of wing quarter chord along a/c x axis
9. vertical distance of the H.tailplane relative to the CG (h_h)
10. horizontal distance of the H.tailplane relative to the CG (l_h) 
11. CL_alpha_h (M=0 and M at all segment's flight speed) 
12 horizontal tailplane area (s_h): 70 ft^2
13. position of aerodynamic centre of the wing along a/c x axis (x_ac)
14. position of aerodynamic centre of the tailplane along a/c x axis (x_ac_h)
15. Oswald efficiency of the wing (e_w)
16. Oswald efficiency of the tailplane (e_h): 
17. Aspect ratio of the tailplane (AR_h)
18. wing setting angle (i_h)
19. wing zero lift AoA (alpha_0): -1.8 degrees
20. tailplane zero lift AoA (alpha_0)
21. Lift coefficient wrt to the change of the elevator angle (CL_delta_e)
22. imcompressible airfoil zero lift pitching moment (CM0_af)


NOTE:

PERFORMANCE ANALYSIS 

"""
