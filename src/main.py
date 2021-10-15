
'''
  _____           __      _______  
 |  __ \         /\ \    / /  __ \ 
 | |__) |   _   /  \ \  / /| |  | |
 |  ___/ | | | / /\ \ \/ / | |  | |
 | |   | |_| |/ ____ \  /  | |__| |
 |_|    \__, /_/    \_\/   |_____/ 
         __/ |                     
        |___/                      

PyAVD - A Python package to pretty much -solve- aircraft conceptual design!


Y3 AVD Group 11, Department of Aeronautics, Imperial College London.

'''

from libraries.Aircraft.Aircraft import Aircraft

# Run this to check the MRO - used to determine the order of inheritance!
# print(Aircraft.__mro__)

# Create the Aircraft instance
coolPlane = Aircraft()
print(coolPlane.W0)
