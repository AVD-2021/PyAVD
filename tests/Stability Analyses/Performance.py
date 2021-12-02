from gpkit import ureg as u
import numpy as np
from numpy.core.fromnumeric import take
import sympy as sym
from ambiance import Atmosphere

# from pyavd.Models.Components.Aircraft import Aircraft


class Performance():
    """Performance model
        
    """
    def __init__(self,
        ac_stall_speed_takeoff,
        ac_stall_speed_landing,
        aircraft_Cd0_landing,
        aircraft_Cd0_takeoff,
        aircraft_Cl_ground,
        aircraft_CL_landing,
        aicraft_Cl_max_clean,
        Cl_climb,
        wing_AR,
        wing_oswald,
        aircraft_W0_S,
        aircraft_W_S_landing,
        aircraft_ground_AoA,
        aircraft_takeoff_AoA,
        h_obs_takeoff,
        h_obs_landing,
        engine_BPR,
        n_engines,
        aircraft_W0,
        aircarft_Wlanding,
        aircraft_LoverD_takeoff,
        ac_reverse_thrust,
        ac_wheel_braking,
        T_max,
        static_T_takeoff,
        dragOEI_evaluated_at_Vcl,
        aircraft_T0_W0,
        takeoff_density,
        wing_S):
        
        self.g = 9.81
        self.aircraft_Cl_ground = aircraft_Cl_ground # Cl at ground configuration (takeoff)
        self.wing_AR = wing_AR
        self.wing_oswald = wing_oswald
        self.wing_S = wing_S
        self.aircraft_W0_S = aircraft_W0_S # wing loading at W0 (start)
        self.aircraft_ground_AoA = aircraft_ground_AoA
        self.aircraft_takeoff_AoA = aircraft_takeoff_AoA
        self.aircraft_stall_speed_takeoff = ac_stall_speed_takeoff
        self.aircraft_stall_speed_landing =ac_stall_speed_landing
        self.h_obs_takeoff = h_obs_takeoff
        self.h_obs_landing = h_obs_landing
        self.engine_BPR = engine_BPR
        self.n_engines = n_engines
        self.aircraft_W0 = aircraft_W0
        self.aircraft_L_over_D_takeoff = aircraft_LoverD_takeoff
        self.ac_reverse_thrust = ac_reverse_thrust
        self.ac_wheel_braking = ac_wheel_braking
        self.T_max = T_max
        self.aircraft_Cl_landing = aircraft_CL_landing
        self.static_T_takeoff = static_T_takeoff
        self.aircraft_Cl_climb = Cl_climb
        self.aircraft_Cl_max_clean = aicraft_Cl_max_clean
        self.aircraft_Wlanding = aircarft_Wlanding
        self.aircraft_W_S_landing = aircraft_W_S_landing
        self.dragOEI_evaluated_at_Vcl = dragOEI_evaluated_at_Vcl
        self.aircraft_T0_W0 = aircraft_T0_W0
        self.takeoff_density = takeoff_density
        


    def get_Sg(self):

        mu = 0.03 # assuming dry concrete

        K_A  = (self.takeoff_density / (2 * self.aircraft_W0_S)) * (mu * self.aircraft_Cl_ground  - self.aircraft_Cd0 - self.aircraft_Cl_ground**2 / (np.pi * self.wing_AR * self.wing_oswald))
        K_T = self.aircraft_T0_W0 - mu

        S_g = (1.0 / (2.0 * self.g * K_A)) * np.log((K_T + K_A * self.V_lof**2)/(K_T))
        
        return S_g

    def get_Sr(self):

        dtheta_dt = 3 * (u.degree / u.second) 
        S_r = self.V_lof * ( (self.aircraft_takeoff_AoA.to(u.radians) - self.aircraft_ground_AoA.to(u.radians)) / dtheta_dt.to(u.radians / u.second))

        return S_r

    def get_Str_Scl(self):
        
        V_tr = (1.15 * self.aircraft_stall_speed_takeoff).to(u.meters / u.second)
        
        # Assumed load factor
        n = 1.2

        R = V_tr ** 2 / ((n - 1) * self.g.to(u.meters / u.second**2))

        
        gamma_CL = np.arcsin(self.aircraft_T0_W0 - 1/self.aircraft_L_over_D_takeoff)

        h_tr = R * (1 - np.cos(gamma_CL))

        if h_tr > self.h_obs_takeoff.to(u.meters):
            S_tr = np.sqrt(R**2 - (R-self.h_obs_takeoff.to(u.meters)) ** 2)
            S_cl = 0

        else:
            S_tr = R * np.sin(gamma_CL)
            S_cl = (self.h_obs_takeoff.to(u.meters)-h_tr) / np.tan(gamma_CL)

        return S_tr, S_cl

    

    def get_BFL(self, state):
        
        # Raymer 17.114
        T_av = 0.75 * self.static_T_takeoff * (5 + self.engine_BPR) / (4 + self.engine_BPR)

        gamma_cl = np.arcsin(((self.n_engines-1)/self.n_engine) * self.aircraft_T0_W0 - self.dragOEI_evaluated_at_Vcl / self.aircraft_W0)
        
        if self.n_engines == 2:
            gamma_min = 0.024
        elif self.n_engines == 3:
            gamma_min = 0.027
        elif self.n_engines == 4:
            gamma_min = 0.030

        G = gamma_cl - gamma_min
     
        # 0.02 if we have typical flaps
        U = 0.01 * self.aircraft_Cl_max_clean + 0.02
        
        sigma = state.rho / 1.225 # rho0
        
        # TODO: NOTE!!! used to be W_S but W0_S should be the same for BFL??
        BFL = (0.863/(1 + 2.3 * G)) * ((self.aircraft_W0_S) / (state.rho * self.g.to(u.feet / u.second**2) * self.aircraft_Cl_climb) + self.h_obs_takeoff.to(u.feet)) * (1/(T_av/self.aircraft_W0 - U) + 2.7) + 655/np.sqrt(sigma)

        return BFL.to(u.meters)


    
    def get_Sb(self, state):

        
        if (self.ac_reverse_thrust):
            T_breaking = - self.T_max * 0.4 # most conservative of -0.4 to -0.5
        else:
            T_breaking = self.T_max * 0.15 # most conservative of 0.10 to 0.15        

        if (self.ac_wheel_braking):
            mu = 0.3 # conservative of 0.3 to 0.5
        else:
            mu = 0.03


        K_A = (state.rho / (2.0  * self.aircraft_W_S_landing)) * (mu * self.aircraft_Cl_landing - self.aircraft_Cd0 - self.aircraft_Cl_landing**2 / (np.pi * self.wing_AR * self.wing_oswald))

        K_T = T_breaking / self.aircraft_Wlanding - mu

        S_b = (1/(2 * self.g * K_A)) * np.log(K_T / (K_T + K_A * self.V_td ** 2))
        
        return S_b


    def get_Sfr(self):
        
        t_fr = 3 # assuming the worse scenario (1-3 secs)

        S_fr = self.V_td * t_fr
        
        return S_fr


    def get_Sf_hf(self):
        
        gamma_a = (3 * u.degrees).to(u.radians)

        V_f = 1.23 * self.aircraft_stall_speed_landing

        # Loading factor
        n = 1.2

        R = V_f ** 2 / ((n-1)*self.g)

        h_f = R(1-np.cos(gamma_a))

        S_f = R * np.sin(gamma_a)

        return S_f, h_f


    def get_Sa(self):

        gamma_a = (3 * u.degrees).to(u.radians)

        #V_a = 1.3 * aircraft.stall_speed_Ld

        S_a = (self.h_obs_landing.to(u.meter) - self.h_f) / np.tan(gamma_a)

        return S_a


    def ground_performance(self, state):
        self.V_lof = (1.1 * self.ac_stall_speed_takeoff).to(u.meters / u.second)
        self.V_td = (1.15 * self.ac_stall_speed_landing).to(u.meters / u.second)


        self.S_g = self.get_Sg()
        self.S_r = self.get_Sr()
        self.S_tr, self.S_cl = self.get_Str_Scl()

        self.S_b = self.get_Sb(state)
        self.S_fr = self.get_Sfr()
        self.S_f, self.h_f = self.get_Sf_hf()
        self.S_a = self.get_Sa()
        self.BFL = self.get_BFL(state)

        self.S_To_act = (self.S_g + self.S_cl + self.S_tr) # already accounts for safety factor
        self.S_Ld_act = (self.Sa + self.S_f + self.S_fr + self.S_b) # already accounts for safety factor

        self.S_to_req = 1.15 * self.S_To_act
        self.S_Ld_req = 1.666 * self.S_Ld_act

        

        print(f"Takeoff distances: S_g = {self.S_g}, S_r = {self.S_r}, S_tr = {self.S_tr}\nS_To_act = {self.S_To_act}, S_To_req = {self.S_to_req}")
        print(f"Landing distances: S_b = {self.S_b}, S_fr = {self.S_fr}, S_f = {self.S_f}, S_a = {self.S_a}\nS_Ld_act = {self.S_Ld_act}, S_Ld_req = {self.S_Ld_req}")
        print(f"BFL = {self.BFL}")

        state[0]["U"] = self.V_lof
        state[-1]["U"] = self.V_td

        return state


######
## Mission Performance
####

    def Breguet_range(self, range, speed, SFC, LD):
        '''Evaluates weight fraction for a given flight regime'''

        # Equation S 1.3-2 - Breguet range
        return np.exp(- range * SFC / (speed * LD))
    
    def Breguet_endurance(self, endurance, SFC, LD):
        return np.exp(- endurance * SFC / LD )


    def mission_profile(self, state):
        # Equation S 1.3-1 - Fuel weight fraction

        aggregate_fuel_frac = 1
        
        # empty weight is 3180kg 
        # #if (current aircraft.We is close to old approx from poster):

        state[0]["Mass"] = self.aircraft_W0
        # 0-1 segment (takeoff)
        aggregate_fuel_frac *= 0.970

        # 1-2 segment (climb)
        aggregate_fuel_frac *= 0.985

        state[1]["Mass"] = self.aircraft_W0 * aggregate_fuel_frac
        # 2-3 segment (cruise)
        aggregate_fuel_frac *= self.Breguet_range(250000 * u.m , state[1]["U"] * u.meters, 1.45 * 10**5, 10.0)

        # 3-4 segment (descent)
        aggregate_fuel_frac *= 0.99

        # 4-5 (climb) 
        aggregate_fuel_frac *= 0.980 # decreased by 0.005 (random)

        state[2]["Mass"] = self.aircraft_W0 * aggregate_fuel_frac
        
        LoverD_gabs = ((state[2]["Mass"] * self.g)/(0.5*state[2]["rho"]*state[2]["U"]**2 * self.wing_S))/ state[2]["CD0"]

        # 5-6 (2nd cruise)
        aggregate_fuel_frac *= self.Breguet_range(370000 * u.m, state[2]["U"]* u.meters, 1.45 *10**5, LoverD_gabs)

        # 7-8 (loiter)
        LoverD_loiter = ((state[2]["Mass"] * self.g)/(0.5*state[2]["rho"]*state[2]["U"]**2 * self.wing_S))/ state[2]["CD0"]
        aggregate_fuel_frac *= self.Breguet_endurance(45 * u.min, 1.45*10**5, LoverD_loiter)

        # 8-9 (descent) 
        aggregate_fuel_frac *= 0.985 # decreased by 0.005

        state[-1]["Mass"] = self.aircraft_W0 * aggregate_fuel_frac
        # 9-10 (landing)
        aggregate_fuel_frac *= 0.995

        # repeat belof for various payload and weight fuels and make plot like in nuclino

        # TODO: DO IT THIS WAY TO GET A GRAPH OF RANGE WRT TO PAYLOAD WEIGHT SAD!!!
        # W10_W0 = (self.aircraft_W0 - aircraft.Wf) / self.aircraft_W0
        # # cruise 
        # W2_W3 = W10_W0 / aggregate_fuel_frac
        #
        #
        #
        #
        #
        #
        #
        # VERY IMPORTANT


        # cruise_range = np.log(W2_W3) * aircraft.LD_at_cruise * aircraft.cruise_speed / ruaridth.SFC_cruise

        # else:
            # re-estimate cruise and loiter weight fractions 
            


        # for i in range(len(mission_profile)):
        #     if mission_profile[i][0].lower() == "takeoff":
        #         aggregate_fuel_frac *= 0.97
        #         fuel_fracs.append(["Takeoff", 0.970])
                
        #     elif mission_profile[i][0].lower() == "climb":
        #         aggregate_fuel_frac *= 0.985
        #         fuel_fracs.append(["Climb", 0.985])
                
        #     elif mission_profile[i][0].lower() == "landing":
        #         aggregate_fuel_frac *= 0.995
        #         fuel_fracs.append(["Landing", 0.995])

        #     elif mission_profile[i][0].lower() == "cruise":
        #         cruise_frac = self.Breguet_range(mission_profile[i][1], SFC[0], LD[0])
        #         aggregate_fuel_frac *= cruise_frac
        #         fuel_fracs.append(["Cruise", np.round(cruise_frac.magnitude[0], 3)])

        #     elif mission_profile[i][0].lower() == "descent":
        #         aggregate_fuel_frac *= 0.99
        #         fuel_fracs.append(["Descent", 0.99])

        #     elif mission_profile[i][0].lower() == "loiter":
        #         loiter_frac = self.__Breguet_endurance(mission_profile[i][1], SFC[1], LD[1])
        #         aggregate_fuel_frac *= loiter_frac
        #         fuel_fracs.append(["Loiter", np.round(loiter_frac.magnitude, 3)])


        self.Wf_W0 = 1.01 * (1-aggregate_fuel_frac)

        print(f"High fidelity Wf_W0 = {self.Wf_W0}")

        return state

####
# Point Performance
###
  
    def rate_of_climb(self):

        # INSERT
        T = None 
        D = None

        # evaluate this at the weight of both climbs we do (get weight there using weight frac)
        W = None
    
        gamma = np.arcsin((T-D)/W)
        
        # for velocity at which we will climb (both climbs)
        V = None

        V_v = V * np.sin(gamma)

        # from this function want to get service ceiling (V_v = 500 ft/min), absolute ceiling (V_v = 0), and check that we meed gradient FAR25 req.


    def mission_envelope(self, state):


        for altitude in range(0, 16000, 1000):

            atmos = Atmosphere(altitude)
            rho = atmos.density
            speed_of_sound = atmos.speed_of_sound

            V_s = np.sqrt(2 * (aircraft.WS_cruise / rho * self.aircraft_Cl_max_clean))

            V_max = self.T_max / (0.5 * rho * self.wing_S * aircraft.CD_cruise)

            M_max = V_max / speed_of_sound

            drag = 0.5 * rho * state[1]["U"]**2 * state[1]["CD0"] * self.wing_S

            thrust = 

            specific_power  = V_max * () / (state[1]["Mass"] * self.g)

            # make specific excess power contour plot


    def point_performance(self, state):
        pass      
  

"""
list of variable we need:

1. aircraft stall speed at take off config.                        --> aircraft.stall_speed_To      --> (NOT defined, without value)


3. Lift coefficient at takeoff config. (@ ground angle of attack)  --> aircraft.CL_ground           --> (NOT defined without value)

4. AoA at take off                                                 --> aircraft.aoa_To              --> (NOT defined, without value)
5. AoA at ground                                                   --> aircraft.aoa_g               --> (NOT defined, without value)
6. lift to drag ratio at takeoff                                   --> aircraft.LD_T0               --> (NOT defined, without value)
   
9. static thrust of the engine at takeoff                          --> aircraft.T_stat_To           --> (Defined, without value)
10. Engine bypass ratio                                            --> Engine.bpr                   --> (Defined, without value)
11. Drag at OEI case evaluated at V_cl                             --> aircraft.D_oei_vcl           --> (NOT defined, without value)
12. CL max of clean configuration                                  --> aircraft.CL_max_clean        --> (NOT defined, without value)
13. CL at climb                                                    --> aicraft.CL_climb             --> (NOT defined, without value)
15. aircraft stall speed at landing configuration                  --> aircraft.stall_speed_Ld      --> (NOT defined, without value)

16. do we have wheel braking?                                                                       --> (Defined, without value)
17. do we have reverse thrust?                                                                      --> (Defined, without value)

18. maximum thrust                                                 --> aircraft.T_max               --> (Defined, without value)
20. landing weight                                                 --> aircraft.W_landing           --> (NOT defined, without value)
21. landing Wing loading                                           --> aircraft.WS_landing          --> (NOT defined, without value) -- segment
22. CL at the landing config                                       --> aircraft.CL_landing          --> (NOT defined, without value) 

23. fuel weight (W_f)                                              --> (NOT defined, without value) 
24. CD cruise                                                      --> (NOT defined, without value) 

1. SFC for loiter cruise and 2nd cruise                         --> (NOT defined, without value) -- segment 
2. L/D for loiter, cruise, and 2nd cruise                       --> (NOT defined, without value) -- segment
3. flight speed for 2nd cruise                                  --> (NOT defined, without value) -- segment


4. why did errikos no like our weight fracs?? correct them according to his poster feedback!!
5. empty weight? is it similar to poster prediction??? !!!!(LAST VERIFICATION)


1. equation for T as a function of flight speed, height              --> T = fn(v,h) !!
2. equation for D as a function of flight speed, height and weight   --> D = fn(v,h,W) !!
"""