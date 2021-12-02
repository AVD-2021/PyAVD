from gpkit import ureg as u
import numpy as np
import sympy as sym
import logging


class Stability:
    """Stability model"""

    def __init__(self, 
    aircraft_x_cg,
    wing_qc,
    x_aerocenter_tail,
    l_h,
    h_h,
    wing_AR,
    wing_taper,
    wing_c,
    wing_S,
    wing_b,
    wing_sweep,
    wing_cl_alpha,
    fuselage_length,
    fuselage_width,
    eta_h,
    S_h,
    CL_alpha_h,
    compressibility_correction,
    wing_alpha0,
    wing_iw,
    tail_alpha0,
    cl_delta_e,
    wing_cm0_af, # CM0_af is the incompressible airfoil zero lift pitching moment
    wing_twist,
    oswald_wing,
    oswald_tailplane,
    tail_AR,
    aircraft_Cd0,
    CM0_w,
    elevator_deflection_conver_parameter
    ):

        # Adding converged solution to the class for later use
        # Note we aren't passing the gpkit models here, just the converged solution...

        self.l_h = l_h
        self.h_h = h_h
        self.aircraft_x_cg = aircraft_x_cg
        self.x_aerocenter_wing = wing_qc
        self.x_aerocenter_tail = x_aerocenter_tail
        self.wing_b = wing_b
        self.wing_AR = wing_AR
        self.wing_qc = wing_qc
        self.wing_cl_alpha = wing_cl_alpha
        self.fuselage_length = fuselage_length
        self.fuselage_width = fuselage_width      
        self.wing_c = wing_c
        self.wing_taper = wing_taper
        self.wing_S = wing_S
        self.wing_sweep = wing_sweep
        self.eta_h = eta_h
        self.S_h = S_h
        self.CL_alpha_h = CL_alpha_h

        self.wing_alpha0 = wing_alpha0
        self.wing_iw = wing_iw
        self.tailplane_alpha0 = tail_alpha0
        self.cl_delta_e = cl_delta_e
        self.wing_cm0_af = wing_cm0_af
        self.wing_twist = wing_twist
        self.oswald_wing = oswald_wing
        self.oswald_tail = oswald_tailplane
        self.tail_AR = tail_AR
        self.aircraft_Cd0 = aircraft_Cd0
        self.CM0_w = CM0_w


        self.correction_factor = compressibility_correction

        # Initializing Variables
        self.CM_f                   = 0
        self.x_np                   = 0
        self.SM_Poff                = 0
        self.SM_Pon                 = 0
        self.htailplane_adj_cl      = 0
        self.dCM_dalpha             = 0
        self.z_t                    = 0
        self.g                      = 9.81          # Yes yes its hacky but idc it works

    

    def calc_fuseCm(self):
        """
        Input requires value import from the fuselage and wing model 
        """

        # TODO: if extra time, look at datcom 1978 or elsewhere for equation to calculate K_f

        input_to_kf             = self.wing_qc / self.fuselage_length        # round to 1 dp
        input_to_kf             = round(input_to_kf, 1)
        
        # Initialise maxCringe()
        if input_to_kf == 0.1:      K_f = 0.06
        elif input_to_kf == 0.2:    K_f = 0.246    
        elif input_to_kf == 0.3:    K_f = 0.6
        elif input_to_kf == 0.4:    K_f = 1.0    
        elif input_to_kf == 0.5:    K_f = 1.6
        elif input_to_kf == 0.6:    K_f = 2.8

        print("K_f: {}".format(K_f))

        # aircraft.fuselage.width is max fuselage width!
        # TODO: add references
        self.CM_f = K_f * (self.fuselage_length * self.fuselage_width ** 2) / (self.wing_c * self.wing_S)

        return self.CM_f



    def calc_SM(self):           # When you name a function like this, you're doing it wrong if you dont return anything...

        SM_Poff     = self.SM_Poff      = (self.x_np - self.aircraft_x_cg) / self.wing_c

# #       if aircraft.engine.location == "under-mounted":
#         self.SM_Pon = SM_Poff - 0.02

#        elif aircraft.engine.location == "aft-mounted":
        self.SM_Pon = SM_Poff + 0.01   # worst case, was +0.01 or +0.02

        self.SM_Poff *= 100
        self.SM_Pon *= 100

        # return self.SM_Poff, self.SM_Pon ---> Do you want to have it like this?



    def calc_depsilon_dalpha(self):

        K_a         = 1 / self.wing_AR - 1 / (1 + self.wing_AR ** 1.7)
        K_lambda    = (10 - 3 * self.wing_taper) / 7.0
        K_h         = (1 - np.abs(self.h_h / self.wing_b) ) / np.cbrt(2 * self.l_h / self.wing_b)             # ---> Tis a constant, doesn't need unit conversions...

        # self.correction_factor = 1  #TODO: we need the lift curve slope of the wing (at M and M=0), for all flight speeds

        self.depsilon_dalpha = 4.44 * (K_a * K_lambda * K_h * np.sqrt(np.cos(self.wing_sweep.to(u.radian)) ** 1.19)) * self.correction_factor

        # return self.depsilon_dalpha




    def calc_x_np(self):
        numerator   = self.wing_cl_alpha * (self.x_aerocenter_wing / self.wing_c) - self.CM_f + self.htailplane_adj_cl * (self.x_aerocenter_tail / self.wing_c)
        denominator = self.wing_cl_alpha + self.htailplane_adj_cl

        self.x_np =  self.wing_c.to(u.meter) * (numerator / denominator)

        # return self.x_np


    def calc_dCM_dalpha(self):
        # Note: all CL_alpha are evaluated at the flight AoA ----> Do u mean cruise? No? All the flight segments including landing and takeoff
        self.htailplane_adj_cl = self.eta_h  * self.CL_alpha_h * (1 - self.depsilon_dalpha) * (self.S_h / self.wing_S)

        print(f"CM_f = {self.CM_f}, Lift_term = {-self.wing_cl_alpha * (self.wing_qc - self.aircraft_x_cg) / self.wing_c}, Tailplane term = {- self.htailplane_adj_cl * (self.x_aerocenter_tail - self.aircraft_x_cg) / self.wing_c}")
        self.dCM_dalpha = -self.wing_cl_alpha * (self.wing_qc - self.aircraft_x_cg) / self.wing_c + self.CM_f - self.htailplane_adj_cl * (self.x_aerocenter_tail - self.aircraft_x_cg) / self.wing_c

        # return self.dCM_dalpha

    def stability_analysis(self):

        # STABILITY
        self.calc_fuseCm()
        self.calc_depsilon_dalpha()
        self.calc_dCM_dalpha()
        self.calc_x_np()
        self.calc_SM()

        print(f"Power-off SM: {self.SM_Poff}")
        print(f"Power-on SM: {self.SM_Pon}")
        print(f"x_np: {self.x_np}")
        print(f"depsilon_dalpha: {self.depsilon_dalpha}")
        print(f"dCM_dalpha: {self.dCM_dalpha}")


    # Trim stuff should really get its own class - specific to different flight regimes - discussed with Cooper some time ago



    ## TRIM ANALYSIS





    def calc_CL_w(self, a_infty):

        return self.wing_cl_alphaw * (a_infty + self.wing_iw - self.wing_alpha0)

    def calc_CL_h(self, a_infty, i_h):

        return self.CL_alpha_h * ((a_infty + self.wing_iw - self.wing_alpha0)*(1 - self.depsilon_dalpha) + (i_h - self.wing_iw)-(self.tailplane_alpha0 - self.wing_alpha0)) + self.cl_delta_e * self.elevator_deflection

    # # Get alpha and setting angle (elevator angle)
    def calc_iH_alphaInfty(self, state):

        [rho, U, Mass, T] = state 

        i_h, alpha_infty = sym.symbols('i, a')          

        # L = W
        # mass here is the mass at current flight segment (state.M)
        eq1 = sym.Eq(self.calc_CL_w(alpha_infty) + self.eta_h * (self.S_h / self.wing_S) * self.calc_CL_h(alpha_infty, i_h), 2 * Mass * self.g / (rho * U**2 * self.wing_S))

        K_w = 1 / (np.pi * self.wing_AR * self.oswald_wing)
        K_h = 1 / (np.pi * self.tail_AR * self.oswald_tail)

        # D = T
        # Fast syntax check pls 
        # Also cant extract Thrust from Engine model, will exist in the Mission model somewhere in the engine performance model for a given flight regime
        eq2 = sym.Eq(self.aircraft_Cd0 + K_w * self.calc_CL_w(alpha_infty)**2 + self.eta_h * K_h * (self.S_h / self.wing_S) * self.calc_CL_h(alpha_infty, i_h)**2, 2 * T / (rho * U**2 * self.wing_S))

        result = self.result = sym.solve([eq1, eq2], (i_h, alpha_infty))

        [self.i_h, self.alpha_infty] = result

        #return result


    def calc_CM_0w(self):

        # sweep is in rad and at the 1/4 chord pos, twist is in deg
        # CM0_af is the incompressible airfoil zero lift pitching moment
        self.CM_0w = (self.wing_cm0_af * (self.wing_AR * np.cos(self.wing_sweep.to(u.radians))**2)/(self.wing_AR + 2 * np.cos(self.wing_sweep.to(u.radians))) - 0.01 * self.wing_twist.to(u.degrees)) * self.correction_factor
    

    def calc_Zt(self, state):

        lift_term =  self.calc_CL_w(self.alpha_infty) * (self.x_aerocenter_wing - self.aicraft_x_cg) / self.wing_c
        tailplane_term = self.eta_h * self.calc_CL_h(self.alpha_infty) * (self.S_h / self.wing_S) * (self.x_aerocenter_tail - self.aircraft_x_cg) / self.wing_c
        q = 0.5 * state.U**2 * state.rho

        self.z_t = -self.wing_S * self.wing_c * q * (lift_term - self.CM_0w  - self.CM_f * self.alpha_infty + tailplane_term) / state.T             # Change T after finishing segments class

        return self.z_t


    def calc_CM(self, state):

        q = 0.5 * state["U"]**2 * state["rho"]

        lift_term =  self.calc_CL_w(self.alpha_infty) * (self.x_aerocenter_wing - self.aicraft_x_cg) / self.wing_c
        tailplane_term = self.eta_h * self.calc_CL_h(self.alpha_infty) * (self.S_h / self.wing_S) * (self.x_aerocenter_tail - self.aircraft_x_cg) / self.wing_c
        
        self.CM = - lift_term - tailplane_term + self.CM_f * self.alpha_infty + self.CM0_w + (self.z_t * state["T"])/(q * self.wing_S * self.wing_c)


    def trim_analysis(self, state):
        # will go over range of this in the code
        self.elevator_deflection = 0

        # TRIM
        self.calc_CM_0w()
        
        # Testing for elevator deflection from 0 to 5 (think this is rad though??)
        # !!! re-think this part, not sure we are doing the right calculations !!
        # for ele_deflection in range(5):
        while np.abs(self.CM) > 0.01:
            self.elevator_deflection = self.ele_deflection

            self.calc_iH_alphaInfty()
            self.calc_Zt()
            #print(f"\n\nElevator deflection: {self.elevator_deflection}\ni_h: {self.i_h}\nalpha_infty: {self.alpha_infty}\nz_t: {self.z_t}\n\n")

            self.calc_CM()

            # Make this a root finding thingy
            # Strategy -> Update elevator_deflection, if CM < 0 make elevator deflection bigger by k*CM --> mess with k till u get convergence



        print(f"\n\nElevator deflection: {self.elevator_deflection}\ni_h: {self.i_h}\nalpha_infty: {self.alpha_infty}\nz_t: {self.z_t}\n\n")



    def calc_thrust(self, state):
    # getting thrust on all segments
        test = state

        for seg in test:
            seg["T"] = 0.5 * seg["rho"] * seg["U"]**2 * self.wing_S * (seg["Cd0"] + 1/(np.pi * self.wing_AR*self.oswald_wing) * self.calc_CL_w(self.alpha_infty)**2 + self.eta_h * (self.S_h / self.wing_S) * 1 / (np.pi * self.tail_AR * self.oswald_tail) * self.calc_CL_h(self.alpha_infty, self.i_h) ** 2)

        return test

""""
Variables we need:

1. lift curve slope of the wing (M=0 and M at all segment's flight speed) --> correction factor --> (defined without value)

2. Thrust (just some stupid simple equation, cruise -> T=D, descent & ascent -> find T needed for wanted descent/ascent rate)

3. CL_alpha_h (M=0 and M at all segment's flight speed) --> (defined without value)
t
4. Oswald efficiency of the tailplane (e_h) --> (defined without value)
 
6. wing setting angle (i_w) --> (defined without value)

7. tailplane zero lift AoA (alpha_0) --> (defined without value)

8. Lift coefficient wrt to the change of the elevator angle (CL_delta_e) --> (defined without value)

9. incompressible airfoil zero lift pitching moment (CM0_af) -- > Nuclino 5.5-3 (NOT defined, from aerofoil data)

"""
