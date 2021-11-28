from logging import WARNING
from gpkit import Model, Variable, VectorVariable, Vectorize, parse_variables
from gpkit.constraints.tight import Tight
from gpkit import ureg as u
import numpy as np
# import sympy as sym           ---> cringeee


"""
temp
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
        self.aircraft = solved_model

        
        # Initializing Variables
        self.CM_f                   = None
        self.x_np                   = None
        self.SM_Poff                = None
        self.SM_Pon                 = None
        self.htailplane_adj_cl      = None
        self.depsilon_dalpha        = None
        self.dCM_dalpha             = None
        self.z_t


        # Calculating variables ----> Nah m8 happens in the Model
        self.get_fuseCm(fuselage, wing, aircraft)
        self.get_depsilon_dalpha(wing, aircraft)

        return 




    def get_fuseCm(self):
        """
        the input requires value import from the fuselage and wing model 

        """

        # TODO: if extra time, look at datcom 1978 or elsewhere for equation to calculate K_f

        wing_quarter_chord = aircraft.wing_qc.to(u.meter)
        input_to_kf = wing_quarter_chord / fuselage.length.to(u.meter)
        
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

        # fuselage.width is max fuselage width!
        self.CM_f = K_f * (fuselage.length.to(u.meter) * fuselage.width.to(u.meter) ** 2) / (wing.c.to(u.meter) * wing.S.to(u.meter**2))






    def get_SM(self, aircraft, wing, engine):
        
        self.SM_Poff = (self.x_np - aircraft.x_cg.to(u.meter)) / wing.c.to(u.meter)

        if engine.location == "under-mounted":
            self.SM_Pon = self.SM_Poff - 0.02

        elif engine.location == "aft-mounted":
            self.SM_Pon = self.SM_Poff + 0.01   # worst case, was +0.01 or +0.02



    def get_depsilon_dalpha(self, wing, aircraft):
        
        K_a = 1 / wing.AR - 1 / (1+ wing.AR ** 1.7)

        K_lambda = (10 - 3 * wing.taper) / 7.0

        K_h = (1 - np.abs(aircraft.h_h.to(u.meter) / wing.b.to(u.meter)) ) / np.cbrt(2 * aircraft.l_h.to(u.meter) / wing.b.to(u.meter))

        self.depsilon_dalpha = 4.44 * (K_a * K_lambda * K_h * np.sqrt(np.cos(wing.sweep.to(u.radian)) ** 1.19))

        self.correction_factor   #TODO: we need the lift curve slope of the wing (at M and M=0), for all flight speeds
        
        self.depsilon_dalpha *= self.correction_factor




    def x_np(self, wing, empennage, aircraft):

        # Note: all CL_alpha are evaluated at the flight AoA
        self.htailplane_adj_cl = empennage.eta_h  * empennage.CL_alpha_h * (1 - self.depsilon_dalpha) * (empennage.s_h.to(u.meter**2) / wing.S.to(u.meter**2))

        numerator = wing.CL_alpha_w * (aircraft.ac_w.to(u.meter) / wing.c.to(u.meter)) - self.CM_f + self.htailplane_adj_cl * (aircraft.ac_h.to(u.meter) / wing.c.to(u.meter))
        
        denominator = wing.CL_alpha_w + self.htailplane_adj_cl

        self.x_np =  wing.c.to(u.meter) * (numerator/denominator) 


    def get_dCM_dalpha(self, wing, empennage, aircraft):

        self.dCM_dalpha = -wing.CL_alpha_w * (aircraft.ac_w.to(u.meter) - aircraft.x_cg.to(u.meter)) / wing.c.to(u.meter) + self.CM_f - self.htailplane_adj_cl * (aircraft.ac_h.to(u.meter) - aircraft.x_cg.to(u.meter)) / wing.c.to(u.meter)
        

    ## TRIM ANALYSIS


    def get_CL_w(self, wing, a_infty):

        return wing.CL_alpha_w * (a_infty + wing.i_w - wing.alpha_0)

    def get_CL_h(self, wing, empennage, a_infty, i_h):
        
        return (wing.CL_alpha_h * ((a_infty + wing.i_w - wing.alpha_0) * (1-self.depsilon_dalpha)+(i_h-wing.i_w)-(empennage.alpha_0_h-wing.alpha_0)) + empennage.CL_delta_e * empennage.delta_e)

    # get alpha and setting angle (elevator engle)
    def get_iH_alphaInfty(self, aircraft, wing, empennage):

        i_h, alpha_infty = sym.symbols('i, a')

        # L = W       
        eq1 = sym.Eq(self.get_CL_w(wing, a) + empennage.eta_h * empennage.S.to(u.meters**2) / wing.S.to(u.meter**2) * self.get_CL_h(wing, empennage, a, i), 2 * aircraft.weight / (raihaan.rho * raihaan.U**2 * wing.S))


        K_w = 1/(np.pi * wing.AR * wing.e)
        K_h = 1/(np.pi * empennage.AR_h * empennage.e_h)

        # D = T
        eq2 = sym.Eq(aircraft.Cd0 + K_w * self.get_CL_w(wing, a)**2 + empennage.eta_h * K_h * empennage.S.to(u.meters**2) / wing.S.to(u.meter**2) * self.get_CL_h(wing, empennage, a, i)**2, 2 * Engine.T / (raihaan.rho * raihaan.U**2 * wing.S))

        result = sym.solve([eq1,eq2],(i,a))


    def get_CM_0w(self, wing):

        # sweep is in rad and at the 1/4 chord pos, twist is in deg
        # CM0_af is the imcompressible airfoil zero lift pitching moment
        self.CM_0w = (wing.CM0_af * (wing.AR * np.cos(wing.sweep.to(u.radians))**2)/(wing.AR + 2 * np.cos(wing.sweep.to(u.radians))) - 0.01 * wing.twist.to(u.degrees)) * self.correction_factor


    def get_Zt(self, wing, empennage, engine):

        lift_term =  - self.get_CL_w(wing, fetch_from_result_of_function_above) * (wing.ac_w.to(u.meter)- aircraft.cg.to(u.meter)) / wing.c.to(u.meter)

        tailplane_term = - empennage.eta_h * self.get_CL_h(wing, empennage, fetch_from_above, fetch_from_abv) * ((empennage.S.to(u.meter**2)) / wing.S.to(u.meter**2)) * (empennage.ac_h.to(u.meter) - aircraft.cg.to(u.meter)) / wing.c.to(u.meter)

        q = 0.5 * raihaan.U**2 * raihaan.rho

        self.z_t = -wing.S.to(u.meter) * wing.c.to(u.meter) * q * (lift_term + self.CM_0w + self.CM_f * fetch_from_above + tailplane_term) / Engine.T

 
""""
Variables we need:

1. lift curve slope of the wing (M=0 and M at all segment's flight speed) --> correction factor 
2. density (rho)
3. speed (U)
4. x_cg
5. Thrust 
6. wing sweep 
7. wing taper
8. position of wing quarter chord along a/c x axis
9. vertical distance of the H.tailplane relative to the CG (h_h)
10. horizontal distance of the H.tailplane relative to the CG (l_h) 
11. CL_alpha_h (M=0 and M at all segment's flight speed) 
12 horizontal tailplane area (s_h)
13. position of aerodynamic centre of the wing along a/c x axis (x_ac)
14. position of aerodynamic centre of the tailplane along a/c x axis (x_ac_h)
15. Oswald efficiency of the wing (e_w)
16. Oswald efficiency of the tailplane (e_h)
17. Aspect ratio of the tailplane (AR_h)
18. wing setting angle (i_h)
19. wing zero lift AoA (alpha_0)
20. tailplane zero lift AoA (alpha_0)
21. Lift coefficient wrt to the change of the elevator angle (CL_delta_e)
22. imcompressible airfoil zero lift pitching moment (CM0_af)


NOTE:

PERFORMANCE ANALYSIS 

"""
