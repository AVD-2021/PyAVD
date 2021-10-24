
#from os import _EnvironCodeFunc

import matplotlib.pyplot as plt
import numpy as np
#from ..Tools.decorators import debug


# from Aircraft.Config import Config
# from libraries import Config as cf

class Constraints:
    '''
    Aircraft Constraints class for PyAVD

    ---> Handles Airworthiness regulations (FAR25 for now) and performance constraints defined in Aircraft.Spec()
    '''
    
    def __init__(self,AR,e,LD_max,FieldLength,max_Vstall,Cl_max,Cl_clean): #input all in SI units.
        self.AR = AR
        self.e = e
        self.LD_max = LD_max
        self.FL = FieldLength
        self.max_Vstall = max_Vstall
        self.Cl_max = Cl_max # this Cl_max is the same as Cl max for landing.
        self.Cl_clean = Cl_clean
        self.Cd0 = (np.pi * AR * e) / ((2.0*LD_max)**2)
        print(f"Cd0 = {self.Cd0}")
        self.WS = np.array(np.linspace(1,3000,3001)) # x axis of constraint graph.
    
    #FIELD PERFORMANCE CONSTRAINTS.

    # Using Roskam Method.
    def takeoff(self):
        TOP = self.FL*3.28/37.5 #gives TOP in lbs/(ft^2)
        TOP = (TOP/2.2046)*9.81*(3.28**2)# convert TOP into N/m^2 to satisfy dimensional homogenity.
        ClmaxTakeoff = self.Cl_clean + 0.7*(self.Cl_max - self.Cl_clean)
        TW = self.WS / ((ClmaxTakeoff*TOP)/1.21) #create an equation for thrust weight ratio as function of wing loading.
        return TW

    #Using Roskam Method.
    def landingRoskam(self,rho):
        V_stall = (((self.FL*3.28)/0.5136)**(1/2))/1.994 #in m/s.
        wingLoadingMax = 0.5*rho*(V_stall**2)*self.Cl_max
        return wingLoadingMax

    #Using Raymer Method.
    def landingRaymer(self,Sa,KR):
        ALD = self.FL*(3/5) # FAR25 requirement.
        wingLoadingMax = ((ALD-Sa)/(0.51*KR))*self.Cl_max
        return wingLoadingMax

    #Using Raymer Method.
    def stallConstraint(self,rho):
        wingLoadingMax = 0.5*rho*(self.max_Vstall**2)*self.Cl_max
        return wingLoadingMax

    #POINT PERFORMANCE CONSTRAINTS - using thrust matching equations.

    def thrust_Matching(self,climb_rate,V_inf,alpha,sigma,alt,Cd0_new,e_new,n): #input in SI units.

        # print(f"ws size: {self.WS.shape}")
        # print(f"climb_rate = {climb_rate}, v_inf = {V_inf}, alpha={alpha}, sigma={sigma}\n alt={alt}, Cd0 = {Cd0_new}, e = {e_new}, n = {n}")

        #Calculate beta.
        if alt <= 11000:
            beta = sigma**0.7
        else:
            beta = 1.439*sigma

        print(f"beta = {beta}")

        term1 = (1.0 / V_inf) * climb_rate
        # print(f"term1 = {term1}")
        # neglect term 2 of 2.2.9
        density = 1.225 * sigma
        #print(f"density={density}")
        term3 = (0.5 * density * ((V_inf)**2)*Cd0_new) / (alpha*self.WS)
        #print(f"term3={term3}")
        term4 = (alpha*(n**2)*self.WS)/(0.5*density*(V_inf**2)*np.pi*self.AR*e_new)
        #print(f"term4={term4}")

        TW = (alpha/beta)* (term1 + term3 + term4)

        print(f"tw size: {TW.shape}")
        
        return TW
        
    def cruise(self,V_inf,alt,sigma,alpha):
        return self.thrust_Matching(0,V_inf,alpha,sigma,alt,self.Cd0,self.e,1)
        
    
    def climb(self,climb_gradient,V_inf,TorL,alpha): #TorL means we choose if it is takeoff or landing.
        #convert climb gradient (%) into climb rate (dh/dt)
        V_inf = V_inf*1.944 #convert from m/s into kts
        climb_rate = climb_gradient*V_inf #in ft/min
        climb_rate  = (climb_rate/3.28)/60 #in m/s

        #Cd0 and e affected by takeoff and landing flap settings during positive and negative climb.
        if TorL == "T":
            Cd0 = self.Cd0 + 0.02
            e = self.e*0.95

        else:
            Cd0 = self.Cd0 + 0.07
            e = self.e*0.9
        
        return self.thrust_Matching(climb_rate,V_inf,alpha,1,0,self.Cd0,e,1)


    
    def loiter(self,V_inf,alt,alpha,sigma):
        return self.thrust_Matching(0,V_inf,alpha,sigma,alt,self.Cd0,self.e,1)
    




ac1 = Constraints(AR=8,e=0.9,LD_max=16,FieldLength=1200,
                max_Vstall=45,Cl_max=2.1,Cl_clean=1.5) #(AR,e,LD_max,FieldLength,max_Vstall,Cl_max,Cl_clean)

#Landing.
TW_line = np.linspace(0,1,100)
WS_maxLanding_Raymer = np.array(np.ones(100))*ac1.landingRaymer(250,1)
WS_maxLandingRoskam = np.array(np.ones(100))*ac1.landingRoskam(1.225)

#Takeoff.
WS = np.linspace(1,3000,3001) # can be used throughout.
TW_takeoff = ac1.takeoff()

#Stall.
TW_line = np.linspace(0,1,100)
WS_maxStall = np.array(np.ones(100))*ac1.stallConstraint(1.225)

#Cruise.
TW_cruise1 = ac1.cruise(221.8,12000,0.245,0.94) #(V_inf,alt,sigma,alpha)
TW_cruise_maxSpeed = ac1.cruise(0.78*325.5,12000,0.245,0.94)
TW_cruise2 = ac1.cruise(200/1.994,8000,0.42,0.5)
TW_absCeiling = ac1.cruise(295*0.8,13000,0.18,0.94)

#Climb
TW_climb1 = 2*ac1.climb(0.1,1.1*87/1.994,"T",0.98)
TW_climb2 = 2*ac1.climb(2.4,1.1*87/1.993,"T",0.97)
TW_climb3 = 2*ac1.climb(1.2,1.25*87/1.994,"T",0.96)

TW_climb4 = 2*ac1.climb(2.1,1.5*87/1.994,"L",0.5)
TW_climb5 = ac1.climb(3.2,1.3*87/1.994,"L",0.5)

#Loiter
TW_loiter = ac1.loiter(150/1.994,1500,0.6,0.86)

fig = plt.figure()

# plot the functions
plt.plot(WS,TW_takeoff, 'b', label='Takeoff')
#plt.plot(WS_maxLanding_Raymer,TW_line, 'c', label='Raymer Landing')
plt.plot(WS_maxLandingRoskam,TW_line, 'r', label='Roskam Landing')
#plt.plot(WS_maxStall,TW_line,'g',label='Stall Constraint')
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

plt.legend(bbox_to_anchor=(1, 1))

plt.grid()
# show the plot
plt.ylim([0, 1])
plt.show()




    

    






