import matplotlib.pyplot as plt
import numpy as np
import scipy.interpolate



ka = 0.87
t_c = 0.12
CL = 0.3

sweep = np.linspace(0,50, 100)
MDD = ka / np.cos(np.deg2rad(sweep)) - t_c / (np.cos(np.deg2rad(sweep)))**2 - CL / (10*np.cos(np.deg2rad(sweep))**3)

f_sweep = scipy.interpolate.interp1d(MDD, sweep)
sweep_angle =  f_sweep(0.8)

fig, ax = plt.subplots(1,1)
ax.plot(sweep, MDD)
axs.axvline(x=sweep_angle, color='black', linestyle='--', label = f"Chosen sweep angle {sweep_angle}")
ax.grid()
ax.legend(loc=4)
plt.show()