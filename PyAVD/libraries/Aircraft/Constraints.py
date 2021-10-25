from .Config import Config
import matplotlib.pyplot as plt
from .. import ureg, sealevel
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
        constraint.WS = np.array(np.linspace(1,3000,4000)) * ureg.Pa
    

    '''FIELD PERFORMANCE CONSTRAINTS'''


    def takeoff(constraint):
        """ 
        ROSKAM Method
        ---> S_takeoff = 37.5 * TOP (FAR25)
        """
        TOP = (constraint.FL / 37.5).to(ureg.N / ureg.m ** 2)
        ClmaxTakeoff = constraint.Cl_clean + 0.7 * (constraint.Cl_max - constraint.Cl_clean)

        # Calculate Thrust/Weight ratio as a function of wing loading
        constraint.TW = constraint.WS / ((ClmaxTakeoff * TOP) / 1.21)


    def landingRoskam(constraint):
        """ 
        ROSKAM Method 
        --->
        """
        V_stall = (((constraint.FL*3.28)/0.5136)**(1/2))/1.994 #in m/s.
        wingLoadingMax = 0.5 * sealevel.density * (V_stall**2) * constraint.Cl_max
        constraint.wingLoadingMax_roskam = wingLoadingMax


    def landingRaymer(constraint, Sa, KR):
        """ RAYMER Method
            
        """

        # FAR25 requirement
        ALD = constraint.FL * 3/5 
        
        constraint.wingLoadingMax_raymer = ((ALD-Sa)/(0.51*KR)) * constraint.Cl_max


    def stallConstraint(constraint):
        """ 
        RAYMER Method
        """
        constraint.WS_maxStall = np.array(np.ones(100)) * 0.5 * sealevel.density * (constraint.max_Vstall**2) * constraint.Cl_max


    """POINT PERFORMANCE CONSTRAINTS - using thrust matching equations"""


    def thrust_Matching(constraint, climb_rate, V_inf, alpha, alt, n):

        atmosphere = Atmosphere(alt)
        rho = atmosphere.density
        rho0 = sealevel.density
        sigma = rho / rho0
        
        # Calculate beta
        if alt <= 11000:
            beta = sigma ** 0.7
        
        else:
            beta = 1.439 * sigma

        term1 = (1.0 / V_inf) * climb_rate
        # Neglect term 2 of S 2.2.9        
        term3 = (0.5 * rho * ((V_inf)**2) * constraint.Cd0) / (alpha * constraint.WS)
        term4 = (alpha * (n**2) * constraint.WS) / (0.5 * rho * (V_inf**2) * np.pi * constraint.aspect_ratio * constraint.e)
        
        constraint.TW = (alpha / beta) * (term1 + term3 + term4)
        
        
    # def level_flight(constraint, V_inf, alt, sigma, alpha):
    #     return constraint.thrust_Matching(0, V_inf, alpha, alt, 1)
        
    
    def climb(constraint, climb_gradient, V_inf, TorL, alpha): 
        #convert climb gradient (%) into climb rate (dh/dt)
        climb_rate = climb_gradient * V_inf #in ft/min

        # Cd0 and e affected by takeoff and landing flap settings during positive and negative climb.
        constraint.Cd0_takeoff = constraint.Cd0 + 0.02
        constraint.e_takeoff = constraint.e * 0.95

        constraint.Cd0_land = constraint.Cd0 + 0.07
        e = constraint.e_land * 0.9
        
        constraint.thrust_Matching(climb_rate, V_inf, alpha, 1, 0, constraint.Cd0, e, 1)



# ac1 = Constraints(AR=8,e=0.9,LD_max=16,FieldLength=1200,
#                 max_Vstall=45,Cl_max=2.1,Cl_clean=1.5) #(AR,e,LD_max,FieldLength,max_Vstall,Cl_max,Cl_clean)

# #Landing.
# TW_line = np.linspace(0,1,100)
# WS_maxLanding_Raymer = np.array(np.ones(100))*ac1.landingRaymer(250,1)
# WS_maxLandingRoskam = np.array(np.ones(100))*ac1.landingRoskam(1.225)

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




    

    






