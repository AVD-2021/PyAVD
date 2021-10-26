from ambiance import Atmosphere
from .. import ureg

def mach_to_speed(altitude, mach):
    """  """
    return Atmosphere(altitude).speed_of_sound * (ureg.m/ureg.s) * mach