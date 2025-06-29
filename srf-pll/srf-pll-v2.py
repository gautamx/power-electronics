'''
Synchronous Reference Frame - Phase Locked Loop v2
Version: 2
Author: Gautam
Date: June 2025
'''
import numpy as np
import math

# simulation params
t_sim = 1                       # simulation time in second
dt = 1e-4                       # simulation time step
fs = 1/dt                       # sampling frequency
t = np.arange(0, t_sim, dt)
num_steps = len(t)

# test input signal params
v_amp = 1                       # signal amplitude
f1 = 50                         # initial frequency
f2 = 100                        # final frequency after step
step_instant = 0.5              # instant @ which frequency step is introduced   

'''
Generating input signal

'''


# FIRST METHOD

# Generates a phase continuous frequency change signal
# Then we generate an orthogonal signal using derivative approximation in the PLL main loop
# But for some reason this creates an unstable output in this simulation
# Still investigating how to fix this  

# v_input = np.zeros(num_steps)
# for i in range(num_steps):
#     if t[i] < step_instant:
        
#         v_input[i] = v_amp * np.sin(2 * np.pi * f1 * t[i])

#     else:
 
#         # Calculate phase continuity at step
#         phase_at_step = 2 * np.pi * f1 * step_instant
#         v_input[i] = v_amp * np.sin(phase_at_step + 2 * np.pi * f2 * (t[i] - step_instant))


# SECOND METHOD
# Generate the frequency event with continuos phase angle
# And feed the angle to the sin and cosine terms 
# Creating an input sine term and orthogonal cosine term
# Crude way for a real implementation but works for demo

va = np.zeros(num_steps)
vb = np.zeros(num_steps)

for i in range(num_steps):
    if t[i] < step_instant:
        angle = 2 * np.pi * f1 * t[i]
    else:
        phase_at_step = 2 * np.pi * f1 * step_instant
        angle = phase_at_step + 2 * np.pi * f2 * (t[i] - step_instant)
    
    va[i] = v_amp * np.cos(angle)          # alpha component -- cosine b/c aligned w/ x-axis
    vb[i] = v_amp * np.sin(angle)          # beta component (true quadrature)
    


# Controller params
kp = 225                      # proportional gain
ki = 10000                    # integral gain
# Aggressive Kp & Ki params because of the range of operating frequencies 

f_grid = 50                   # grid frequency (Hz)
wnom = 2 * np.pi * f_grid     # nominal frequency in rad/s

# initializing PLL params
theta_pll = 0                 # phase estimate initialization
w_pll = 0                  # frequency estimate initialization
error = 0
integral_error = 0      
vd = 0                  # d-axis voltage
vq = 0                  # q-axis voltage

# initializing arrays for data storage
theta_pll_hist = np.zeros(num_steps)
w_pll_hist = np.zeros(num_steps)
f_pll_hist = np.zeros(num_steps)
vd_hist = np.zeros(num_steps)
vq_hist = np.zeros(num_steps)
error_hist = np.zeros(num_steps)
pi_output_hist = np.zeros(num_steps)

# PLL main loop
for k in range(num_steps):

    # FIRST METHOD with orthogonal signal generation

    # # current input sample
    # va_k = v_input[k]         # alpha component

    # # creating orthogonal component
    # # using previous sample approximation for derivative
    # if k > 0:
    #     vb_k = (v_input[k] - v_input[k-1]) / (w_pll * dt)
    #     # cos(w*t) = (1/w)*d/dt(sin(w*t)) = (1/w * dt) * (sin(i) - sin(i-1))
    # else:
    #     # for k = 0
    #     vb_k = 0

    # Creating an orthogonal signal with Hilbert Transform instead of derivative approximation
    # gives a more accurate signal and can work here 

    # Taking one voltage sample at a time
    va_k = va[k]
    vb_k = vb[k]

    # Park transformation alpha-beta to d-q
    cos_theta = np.cos(theta_pll)
    sin_theta = np.sin(theta_pll)

    vd = (va_k * cos_theta) + (vb_k * sin_theta)
    vq = (-va_k * sin_theta) + (vb_k * cos_theta)
    

    ############################################## PI controller implementation

    # vq is the error which we will drive to zero
    error = vq

    # integrating the error term with forward Euler method
    integral_error = integral_error + (error * dt)

    # calculating the PI controller output
    pi_output = (kp * error) + (ki * integral_error)

    # frequency estimate, we can also add wnom as the feed-forward term
    # w_pll = wnom + pi_output
    w_pll = pi_output

    # phase estimate, integrating w_pll using forward Euler method
    theta_pll = theta_pll + (w_pll * dt)

    # Wrap the phase [0, 2*pi]
    # theta_pll = np.mod(theta_pll, 2 * np.pi)
    if theta_pll > (2 * np.pi):
        theta_pll = theta_pll - (2 * np.pi)

    # Store the results
    theta_pll_hist[k] = theta_pll
    w_pll_hist[k] = w_pll
    f_pll_hist[k] = w_pll / (2 * np.pi)
    vd_hist[k] = vd
    vq_hist[k] = vq
    error_hist[k] = error
    pi_output_hist[k] = pi_output

# Calculate actual phase for comparison
theta_actual = np.zeros(num_steps)
for i in range(num_steps):
    if t[i] < step_instant:
        theta_actual[i] = 2 * np.pi * f1 * t[i]
    else:
        # theta_actual[i] = 2 * np.pi * f2 * t[i]
        phase_at_step = 2 * np.pi * f1 * step_instant
        theta_actual[i] = phase_at_step + 2 * np.pi * f2 * (t[i] - step_instant)

    # Wrap the phase [0, 2*pi]
    # theta_actual = np.mod(theta_actual, 2 * np.pi)
    if theta_actual[i] > (2 * np.pi):
        theta_actual[i] = theta_actual[i] - (2 * np.pi)

# plotting the data
import matplotlib.pyplot as plt

# Plot 1: Input signal and PLL tracking
plt.subplot(2, 2, 1)
plt.plot(t, va, label='Input Signal', color='b', linestyle='--')
plt.plot(t, np.cos(theta_pll_hist), label='PLL', color='r', linestyle='-')
plt.ylabel('Amplitude')
plt.title('Input Signal vs PLL')
plt.grid(True)
plt.legend()
plt.xlim([0.4, 0.6])

# # Plot 2: Frequency estimation
plt.subplot(2, 2, 2)
plt.plot(t, f_pll_hist, label='Estimated Frequency', color='b')
plt.axhline(y=f1, color='b', linestyle='--', alpha=0.7, label=f'Target {f1} Hz')
plt.axhline(y=f2, color='g', linestyle='--', alpha=0.7, label=f'Target {f2} Hz')
plt.axvline(x=step_instant, color='k', linestyle=':', alpha=0.7, label='Frequency Step')
plt.ylabel('Frequency (Hz)')
plt.title('Frequency Estimation')
plt.grid(True)
plt.legend()
# plt.ylim([48, 54])
# plt.xlim([-0.2, 1])

# # Plot 3: Phase comparison
# plt.subplot(3, 2, 3)
# plt.plot(t, theta_actual, 'b-', label='theta_actual', linewidth=1)
# plt.plot(t, theta_pll_hist, 'r--', label='theta_pll', linewidth=1)
# plt.plot(t, theta_actual - (theta_pll_hist - (np.pi/2)))
# plt.xlabel('Time')
# plt.ylabel('Phase (rad)')
# plt.title('Phase Estimation')
# plt.legend()
# plt.grid(True)
# plt.xlim([0.4, 0.6])

# # Plot 4: dq components
plt.subplot(2, 2, 3)  # Row 3, column 2, position 4
plt.plot(t, vd_hist, 'b-', label='Vd (d-axis)', linewidth=1)
plt.plot(t, vq_hist, 'r-', label='Vq (q-axis)', linewidth=1)
plt.xlabel('Time')
plt.ylabel('Voltage')
plt.title('DQ Components')
plt.legend()
plt.grid(True)
# plt.xlim([-0.2, 1])


# # Plot 5: Phase error
plt.subplot(2, 2, 4)
plt.plot(t, error_hist, 'r-', label='Phase Error (Vq)', linewidth=1)
plt.plot(t, pi_output_hist, 'b-', label='PI output', linewidth=1)
plt.ylabel('Error')
plt.title('Phase Error Signal')
plt.legend()
plt.grid(True)
# plt.xlim([-0.2, 1])

plt.tight_layout()
plt.show()