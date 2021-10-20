class Constraints:
    '''
    Aircraft Constraints class for PyAVD

    ---> Handles Airworthiness regulations (FAR25 for now) and performance constraints defined in Aircraft.Spec()
    '''
    
    def __init__(self,AR,e,LD_max,FieldLength,max_Vstall,Cl_max,Cl_clean):
        self.AR = AR
        self.e = e
        self.LD_max = LD_max
        self.FL = FieldLength
        self.max_Vstall = max_Vstall
        self.Cl_max = Cl_max # this Cl_max is the same as Cl max for landing.
        self.Cl_clean = Cl_clean
        self.Cd0 = 3.14 * AR * e /((2*LD_max)**2)
    
    #FIELD PERFORMANCE CONSTRAINTS.

    # Using Roskam Method.
    def takeoff(self):
        TOP = self.FL/37.5 #gives TOP in lbs/(ft^2)
        TOP = (TOP/2.2046)*9.81*(3.28^2)# convert TOP into N/m^2 to satisfy dimensional homogenity
        ClmaxTakeoff = self.Cl_clean + 0.7*(self.Cl_max - self.Cl_clean)
        #create an equation for thrust weight ratio as function of wing loading.

    #Using Roskam Method.
    def landingRoskam(self,rho):
        V_stall = (((self.FL*3.28)/0.5136)^(1/2))/1.994 #in m/s.
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

    def cruise(self,V_inf,alt):
        None
    
    def climb(self,climb_rate):
        None
    
    def loiter(self,V_inf,alt):
        None
    







    
    

    

    






