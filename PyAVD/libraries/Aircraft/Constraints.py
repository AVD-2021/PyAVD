from .Config import Config
import matplotlib.pyplot as plt
from .. import ureg, sealevel
from ..Tools import mach_to_speed
import numpy as np
from ambiance import Atmosphere


class Constraints(Config):
    '''
    Aircraft Constraints class for PyAVD

    ---> Handles Airworthiness regulations (FAR25 for now) and performance constraints defined in Aircraft.Spec()
    '''

    def __init__(constraint, FieldLength, max_Vstall, Cl_max, Cl_clean):

        constraint.FL = FieldLength
        constraint.max_Vstall = max_Vstall

        # This Cl_max is the same as Cl max for landing
        constraint.Cl_max = Cl_max
        constraint.Cl_clean = Cl_clean

        # X-axis of constraint graph
        constraint.WS = np.array(np.linspace(1, 3000, 4000)) * ureg.Pa


        # Run constraint functions
        constraint.takeoff()
        constraint.landingRaymer(250 * ureg.meters, 1)
        constraint.landingRoskam()

        constraint.plot_constraints()


    '''FIELD PERFORMANCE CONSTRAINTS'''


    def takeoff(constraint):
        """ 
        ROSKAM Method
        ---> S_takeoff = 37.5 * TOP (FAR25)
        """
        TOP = constraint.FL / (37.5 * (ureg.ft ** 3 / ureg.lb))
        ClmaxTakeoff = constraint.Cl_clean + 0.7 * (constraint.Cl_max - constraint.Cl_clean)

        # Calculate Thrust/Weight ratio as a function of wing loading
        constraint.TW_takeoff = constraint.WS / ((ClmaxTakeoff * 9.81 * TOP.to(ureg.kg / ureg.m**2)) / 1.21)
        print(f"TW_TO:{constraint.TW_takeoff.to_base_units()}")


    def landingRoskam(constraint):
        """ 
        ROSKAM Method 
        --->
        """
        constraint.V_stall =  ( (constraint.FL.to(ureg.ft)) / (0.5136 * ureg.ft / ureg.kts**2) ) ** 0.5
        constraint.wingLoadingMax_roskam = ( 0.5 * sealevel.density * ureg.kg/(ureg.m**3)  * (constraint.V_stall**2) * constraint.Cl_max ).to(ureg.N / ureg.m**2)


    def landingRaymer(constraint, Sa, KR):
        """
        RAYMER Method
            
        """

        # FAR25 requirement
        # TODO: put type of requirement (i.e. FAR25) and then some requirements like Sa are set automatically
        # TODO: put the type of aircraft (i.e. jet transport) and then some settings like AR, wetted ratio are set automatically
        ALD = constraint.FL * 3/5
        
        constraint.wingLoadingMax_raymer = (ALD - Sa)/(0.51 * (ureg.m**3 / ureg.N) * KR) * constraint.Cl_max


    def stallConstraint(constraint):
        """ 
        RAYMER Method
        """
        constraint.WS_maxStall = np.array(np.ones(100)) * 0.5 * sealevel.density * (ureg.kg / ureg.m**3) * (constraint.max_Vstall**2) * constraint.Cl_max


    """POINT PERFORMANCE CONSTRAINTS - using thrust matching equations"""


    def thrustMatching(constraint, climb_rate, V_inf, alpha, alt, n=1):
        # All the parameters already come with units
        atmosphere = Atmosphere(alt.to(ureg.m).magnitude)
        rho = atmosphere.density * (ureg.kg / ureg.m**3)
        rho0 = sealevel.density * (ureg.kg / ureg.m**3)
        sigma = rho / rho0
        
        # Calculate beta
        if alt.to(ureg.m).magnitude <= 11000:
            beta = sigma ** 0.7
        
        else:
            beta = 1.439 * sigma

        term1 = (1.0 / V_inf) * climb_rate
        # Neglect term 2 of S 2.2.9        
        term3 = (0.5 * rho * ((V_inf)**2) * constraint.Cd0) / (alpha * constraint.WS)
        term4 = (alpha * (n**2) * constraint.WS) / (0.5 * rho * (V_inf**2) * np.pi * constraint.aspect_ratio * constraint.e)

        return (alpha / beta) * (term1 + term3 + term4)
        
        
    # def level_flight(constraint, V_inf, alt, sigma, alpha):)
    #     return constraint.thrustMatching(0, V_inf, alpha, alt, 1
        
    
    def climb(constraint, climb_gradient, V_inf, alpha): 
        # Convert climb gradient (%) into climb rate (dh/dt)
        climb_rate = (climb_gradient * V_inf.to(ureg.kts)).magnitude * ureg.ft / ureg.min
        climb_rate = climb_rate.to(ureg.m / ureg.s)

        # Cd0 and e affected by takeoff and landing flap settings during positive and negative climb.
        constraint.Cd0_takeoff = constraint.Cd0 + 0.02
        constraint.e_takeoff = constraint.e * 0.95

        return constraint.thrustMatching(climb_rate, V_inf, alpha, 0 * ureg.m)


    def go_around_climb(constraint, climb_gradient, V_inf, alpha):
        # Convert climb gradient (%) into climb rate (dh/dt)
        climb_rate = climb_gradient * V_inf.to(ureg.kts) #in ft/min

        constraint.Cd0_goaround = constraint.Cd0 + 0.07
        constraint.e_goaround = constraint.e * 0.9
        
        return constraint.thrustMatching(climb_rate, V_inf, alpha, 0 * ureg.m)


    def plot_constraints(constraint):

        # TW_dict = {}

        # for i,j in enumerate(constraint.profile):

        #     if j[0] == "cruise" or j[0] == "loiter":
        #         alpha = constraint.cumulative_fuel_frac[i-1]
        #         TW.dict[j[0]] = constraint.thrustMatching(0, j[1]['Speed'], alpha, j[1]['Altitude'])
            
        #     elif j[0] == "climb":
        #         alpha = constraint.cumulative_fuel_frac[i-1]
        #         constraint.climb(j[1]['Gradient'], j[1]['Speed'], alpha)

        WS = constraint.WS

        # Cruise
        TW_cruise1 = constraint.thrustMatching(0 * ureg.m / ureg.s, mach_to_speed((40000 * ureg.ft).to(ureg.m).magnitude, 0.75), 0.98, 40000 * ureg.ft)
        TW_cruise_maxSpeed = constraint.thrustMatching(0 * ureg.m / ureg.s, mach_to_speed((40000 * ureg.ft).to(ureg.m).magnitude, 0.78), 0.94, 40000 * ureg.ft)
        TW_absCeiling = constraint.thrustMatching(0 * ureg.m / ureg.s, mach_to_speed((40000 * ureg.ft).to(ureg.m).magnitude, 0.75), 0.94, 45000 * ureg.ft)
        TW_cruise2 = constraint.thrustMatching(0 * ureg.m / ureg.s, 200 * ureg.kts, 0.5, 26000 * ureg.ft)
        
        # Climb
        TW_climb1 = constraint.climb(0.1, 1.1 * constraint.V_stall, 0.98) * 2.0
        TW_climb2 = constraint.climb(2.4, 1.1 * constraint.V_stall, 0.98) * 2.0
        TW_climb3 = constraint.climb(1.2, 1.25 * constraint.V_stall, 0.98) * 2.0
        TW_climb4 = constraint.climb(2.1, 1.5 * constraint.V_stall, 0.3) * 2.0
        TW_climb5 = constraint.climb(3.2, 1.3 * constraint.V_stall, 0.3)
        
        # Loiter
        TW_loiter = constraint.thrustMatching(0 * ureg.m / ureg.s, 150 * ureg.kts, 0.2, 5000 * ureg.ft)

        # Landing
        TW_line = np.linspace(0, 1, 100)
        WS_maxLanding_Raymer = np.array(np.ones(100)) * constraint.wingLoadingMax_raymer
        WS_maxLandingRoskam = np.array(np.ones(100)) * constraint.wingLoadingMax_roskam

        constraint.fig_constraint = plt.figure()

        # plot the functions
        plt.plot(WS, constraint.TW_takeoff, 'b', label='Takeoff')
        plt.plot(WS_maxLandingRoskam,TW_line, 'r', label='Roskam Landing')
        #plt.plot(WS_maxLanding_Raymer,TW_line, 'r--', label='Raymer Landing')
        plt.plot(WS,TW_cruise1,'k',label='Cruise 1')
        plt.plot(WS,TW_cruise2,'lime',label='Cruise 2')
        plt.plot(WS,TW_cruise_maxSpeed,'g',label='Cruise Max Speed')
        plt.plot(WS,TW_absCeiling,'tab:pink',label='Absolute ceiling')
        plt.plot(WS,TW_loiter,'tab:cyan',label='Loiter')
        plt.plot(WS,TW_climb1,'y',label='Climb 1st Segment OEI')
        plt.plot(WS,TW_climb2,'m',label='Climb 2nd Segment OEI')
        plt.plot(WS,TW_climb3,'c',label='Climb 3rd Segment OEI')
        plt.plot(WS,TW_climb4,'tab:olive',label='Climb from approach OEI')
        plt.plot(WS,TW_climb5,'tab:brown',label='Climb from landing AEO')
        plt.plot(2300,0.3,'r',marker = "X",label='Selected Design Point')
        plt.xlabel("W/S")
        plt.ylabel("T/W")
        plt.legend(bbox_to_anchor=(1, 1))

        plt.grid()
        # show the plot
        plt.ylim([0, 1])
        plt.xlim([0, 3000])

'''
Here lies Gab's code.
'''

# ac1 = Constraints(AR=8,e=0.9,LD_max=16,FieldLength=1200,
#                 max_Vstall=45,Cl_max=2.1,Cl_clean=1.5) #(AR,e,LD_max,FieldLength,max_Vstall,Cl_max,Cl_clean)



# #Takeoff.
# WS = np.linspace(1,3000,3001) # can be used throughout.
# TW_takeoff = ac1.takeoff()

# #Stall.
# TW_line = np.linspace(0,1,100)
# WS_maxStall = np.array(np.ones(100))*ac1.stallConstraint(1.225)

# #Cruise.
# TW_cruise1 = ac1.cruise(221.8,12000,0.245,0.94) #(V_inf,alt,sigma,alpha)
# TW_cruise_maxSpeed = ac1.cruise(0.78*325.5,12000,0.245,0.94)
# TW_cruise2 = ac1.cruise(200/1.994,8000,0.42,0.5)
# TW_absCeiling = ac1.cruise(295*0.8,13000,0.18,0.94)

# #Climb
# TW_climb1 = 2*ac1.climb(0.1,1.1*87/1.994,"T",0.98) #climb_gradient,V_inf,TorL,alpha
# TW_climb2 = 2*ac1.climb(2.4,1.1*87/1.993,"T",0.97)
# TW_climb3 = 2*ac1.climb(1.2,1.25*87/1.994,"T",0.96)

# TW_climb4 = 2*ac1.climb(2.1,1.5*87/1.994,"L",0.5)
# TW_climb5 = ac1.climb(3.2,1.3*87/1.994,"L",0.5)

# #Loiter
# TW_loiter = ac1.loiter(150/1.994,1500,0.6,0.86) #V_inf,alt,alpha,sigma

# fig = plt.figure()

# # plot the functions
# plt.plot(WS,TW_takeoff, 'b', label='Takeoff')
# #plt.plot(WS_maxLanding_Raymer,TW_line, 'c', label='Raymer Landing')
# plt.plot(WS_maxLandingRoskam,TW_line, 'r', label='Roskam Landing')
# #plt.plot(WS_maxStall,TW_line,'g',label='Stall Constraint')
# plt.plot(WS,TW_cruise1,'k',label='Cruise 1')
# plt.plot(WS,TW_cruise2,'lime',label='Cruise 2')
# plt.plot(WS,TW_cruise_maxSpeed,'g',label='Cruise Max Speed')
# plt.plot(WS,TW_absCeiling,'tab:pink',label='Absolute ceiling')
# plt.plot(WS,TW_loiter,'tab:cyan',label='Loiter')
# plt.plot(WS,TW_climb1,'y',label='Climb 1st Segment OEI')
# plt.plot(WS,TW_climb2,'m',label='Climb 2nd Segment OEI')
# plt.plot(WS,TW_climb3,'c',label='Climb 3rd Segment OEI')
# plt.plot(WS,TW_climb4,'tab:olive',label='Climb from approach OEI')
# plt.plot(WS,TW_climb5,'tab:brown',label='Climb from landing AEO')
# plt.plot(2300,0.3,'r',marker = "X",label='Selected Design Point')

# plt.legend(bbox_to_anchor=(1, 1))

# plt.grid()
# # show the plot
# plt.ylim([0, 1])
# plt.show()




    

    






