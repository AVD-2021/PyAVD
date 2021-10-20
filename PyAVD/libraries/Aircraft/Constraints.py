class Constraints:
    '''
    Aircraft Constraints class for PyAVD

    ---> Handles Airworthiness regulations (FAR25 for now) and performance constraints defined in Aircraft.Spec()
    '''
    
    def __init__(self,AR,e,LD_max,FieldLength,MaxVstall,Cl_max,Cl_clean):
        self.AR = AR
        self.e = e
        self.LD_max = LD_max
        self.FL = FieldLength
        self.MaxVstall = MaxVstall
        self.Cl_max = Cl_max
        self.Cl_clean = Cl_clean
    
    # Using Roskam Method.
    def takeoff(self):
        TOP = self.FL/37.5 #gives TOP in lbs^2/(ft^2 hp)
        # convert TOP into kg^2/(m^2 N)





