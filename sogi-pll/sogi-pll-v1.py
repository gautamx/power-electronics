'''
Second Order Generalized Integrator - Phase Locked Loop v1
Version: 1
Author: Gautam
Date: July 2025
'''

import numpy as np
import matplotlib.pyplot as plt

# simulation params
fs = 10000        # sampling frequency (Hz)
dt = 1/fs         # sim time step
t_sim = 0.6       # sim time
t = np.arange(0, t_sim, dt)
num_steps = len(t)    # number of steps in sim


# input signal
f_in = 50.0      # input signal freq
w_in = 2*np.pi*f_in     # angular freq (omega)

# add harmonics and random noise
v_in = np.sin(w_in*t) \
       + 0.02 * np.sin(3*w_in*t) \
       + 0.05 * np.random.normal(0, 1, len(t))


# SOGI-PLL params
k = 1.0                 # gain of SOGI
w_nom = 2*np.pi*50      # nominal grid angular freq (omega)
kp = 20     # PLL PI controller proportional gain
ki = 5      # PLL PI controller integral gain


# State variables
v_alpha = 0.0
v_beta = 0.0

x1 = 0.0     # ~ v_alpha - SOGI output in-phase component
x2 = 0.0     # ~ v-beta - SOGI output quadrature component

theta_est = 0.0     # initializing estimated phase angle
w_est = w_nom       # initializing estimated frequency (omega)

vd = 0.0       # direct component
vq = 0.0       # quadrature component
vq_int = 0.0   # vq integrator

# data storage arrays
theta_log = []
f_log = []
vq_log = []
v_alpha_log = []
v_beta_log = []

##############################################################
# simulation loop
##############################################################
for n in range(num_steps):

    vin = v_in[n]   # input voltage at each step

    # ===== SOGI =====
    # error input
    e = vin - x1

    # SOGI states
    dx1 = w_nom * ( (k*e) - x2 )
    dx2 = w_nom * x1
    # SOGI behaves like a band-pass filter centered at w_nom
    # w_est changes over time which would destabilize or detune the filter
    # it would constantly shift the center frequency of the filter

    x1 += dx1 * dt
    x2 += dx2 * dt

    v_alpha = x1
    v_beta = x2

    # ===== Park Transform =====
    cos_theta = np.cos(theta_est)
    sin_theta = np.sin(theta_est)
    # in MCU implementation we use a lookup table here

    vd = v_alpha*cos_theta + v_beta*sin_theta
    vq = v_alpha*(-sin_theta) + v_beta*cos_theta

    # ===== PLL PI Controller =====
    vq_int += vq * dt   # vq integrator
    
    w_est = (kp*vq) + (ki*vq_int) + w_nom

    theta_est += w_est * dt
    # wrap theta_est to 0 to 2*pi
    if theta_est > 2*np.pi:
        theta_est -= 2*np.pi

    # data logging
    theta_log.append(theta_est)
    f_log.append(w_est/(2*np.pi))
    vq_log.append(vq)
    v_alpha_log.append(v_alpha)
    v_beta_log.append(v_beta)

# ===== Plot results =====
plt.figure(figsize=(10, 6))
plt.subplot(2, 1, 1)
plt.plot(t, v_in, label="Input Voltage")
plt.title("SOGI-PLL Estimation")
plt.ylabel("Voltage (V)")
plt.xlim([0, 0.2])
plt.grid()

plt.subplot(2, 1, 2)
plt.plot(t, v_alpha_log, label="v_alpha", color='green')
plt.plot(t, v_beta_log, label="v_beta", color='blue')
plt.ylabel("v_alpha & v_beta")
plt.xlabel("Time (s)")
plt.xlim([0, 0.2])
plt.grid()
plt.legend()


plt.figure(figsize=(10, 6))
plt.subplot(2, 1, 1)
plt.plot(t, f_log, label="Estimated Frequency", color='orange')
plt.axhline(f_in, color='gray', linestyle='--', label="Actual Frequency")
plt.ylabel("Frequency (Hz)")
plt.grid()
plt.legend()

plt.subplot(2, 1, 2)
plt.plot(t, vq_log, label="vq", color='green')
plt.ylabel("vq")
plt.xlabel("Time (s)")
plt.grid()

plt.tight_layout()
plt.show()