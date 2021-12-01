import matplotlib.pyplot as plt
import numpy as np


#plane parameters
e = 0.9



Cl = np.arange(0.0,1.0,0.1,dtype=float)

AR = 5
Cd_5 = (Cl*Cl) / (e*AR*np.pi) + 0.0174
Cl_vs_Cd_5 = Cl/ Cd_5

AR = 6
Cd_6 = (Cl*Cl) / (e*AR*np.pi) + 0.0174
Cl_vs_Cd_6 = Cl/ Cd_6   

AR = 7.5
Cd_7 = (Cl*Cl) / (e*AR*np.pi) + 0.0174
Cl_vs_Cd_7 = Cl/ Cd_7

AR = 8
Cd_8 = (Cl*Cl) / (e*AR*np.pi) + 0.0174
Cl_vs_Cd_8 = Cl/ Cd_8

AR = 9
Cd_9 = (Cl*Cl) / (e*AR*np.pi) + 0.0174
Cl_vs_Cd_9 = Cl/ Cd_9

AR = 10
Cd_10 = (Cl*Cl) / (e*AR*np.pi) + 0.0174
Cl_vs_Cd_10 = Cl/ Cd_10


fig, axs = plt.subplots(1, 1)
axs.plot(Cl, Cl_vs_Cd_5, 'o-', label="AR = 5")
axs.plot(Cl, Cl_vs_Cd_6, 'v-', label="AR = 6")
axs.plot(Cl, Cl_vs_Cd_7, '^-', label="AR = 7.5")
axs.plot(Cl, Cl_vs_Cd_8, '<-', label="AR = 8")
axs.plot(Cl, Cl_vs_Cd_9, '>-', label="AR = 9")
axs.plot(Cl, Cl_vs_Cd_10, label="AR = 10")
axs.set_ylabel(r'$C_L / C_D$', fontsize=20)
axs.set_xlabel(r'$C_L$', fontsize=20)
axs.axvline(x=0.3, color='black', linestyle='--')
axs.axvspan(0.45, 0.7, facecolor='#2ca02c', alpha=0.5)

plt.legend(loc = 2)
plt.show()