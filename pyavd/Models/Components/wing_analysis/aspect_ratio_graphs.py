import matplotlib.pyplot as plt
import numpy as np


e = 0.9
CL = 0.3
AR = np.arange(5, 10, 0.1)
induced_drag = CL / (e * np.pi *AR)
weight = AR**(0.5)

fig, axs = plt.subplots(1, 2)
axs[0].plot(AR, weight)
axs[0].set_xlabel(r'$AR$', fontsize=20)
axs[0].set_ylabel(r'$AW$', fontsize=20)
axs[0].axvspan(7, 8, facecolor='#2ca02c', alpha=0.5)
axs[0].axvline(x=7.5, color='black', linestyle='--', label = "Chosen AR = 7.5")
axs[0].legend(loc = 3)
axs[1].plot(AR,induced_drag)
axs[1].set_xlabel(r'$AR$', fontsize=20)
axs[1].set_ylabel(r'$C_{Di}$', fontsize=20)
axs[1].axvspan(7, 8, facecolor='#2ca02c', alpha=0.5)
axs[1].axvline(x=7.5, color='black', linestyle='--', label = "Chosen AR = 7.5")
axs[1].axvline(x=9, color='purple', linestyle='-.', label = "AR with winglets = 7.5")
axs[1].legend(loc = 3)
plt.show()



