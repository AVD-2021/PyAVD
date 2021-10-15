
'''
Aircraft base class definition for PyAVD

- Incorporates subclasses Spec(), BaselineConfig() and Constraints()

'''

class Aircraft:

    def __init__(ac, spec, config, constraints):
        ac.Spec = spec
        ac.Config = config
        ac.Constraints = constraints

        # On first iteration, approximate aircraft W0 from Baseline Configuration
        ac.W0 = ac.Config.approx_W0()


    def iterate_W0(ac, n):
        '''
        Uses latest operating empty weight and fuel weight fractions to compute gross takeoff weight
        '''

        # Reassignment for clarity
        profile = ac.Spec.profile
        LD_max = ac.Config.LD_max_approx()
        SFC = ac.Config.SFC_approx()

        # Iterate n times
        for i in range(n):

            # Equation S 1.1-3 - Note that weight fractions computed in the configuration class
            ac.W0 = ac.Spec.fixed_weight / (1 - ac.Config.WfW0(profile, LD_max, SFC) - ac.Config.WeW0(ac.W0))

