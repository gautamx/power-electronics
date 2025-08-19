import numpy as np
import matplotlib.pyplot as plt

# deciding time-step
# typical power converter switching frequency ~5kHz
# cycle time period of 200us -- sampling time

# time-step should be << 200us
# let time-step for signal generation be 1us

t_duration = 1.0
t_step = 1.0e-6

num_samples = int(t_duration/t_step)

# generate an array from 0 to (10^6 - 1)
# mult t_step to get each time instant
time_array = np.arange(num_samples)*t_step

freq = 50.0     # 50Hz
omega = 2*np.pi*freq    # rad/s
mag = np.sqrt(2)*230.0
L = 1.0e-3    # 1mH inductor
R = 1.0e-2    # 0.2 ohm loss resistor
# settling time = 4*time constant = 4*L/R

# sinusoidal input signal generation
voltage_signal = mag*np.sin(omega*time_array)

t_sample = 200.0e-6
num_skip = int(t_sample/t_step)

tsample_array = time_array[::num_skip]
voltage_samples = voltage_signal[::num_skip]

# initialize the output
current_samples = np.zeros(voltage_samples.size)

# filter input
u = np.zeros(2)     # present value u[0]=v(n) and past value u[1]=v(n-1)
y = np.zeros(2)     # present value y[0]=i(n) and past value y[1]=i(n-1)

# ISR with hardware here
# calculate the output
for voltage_idx, voltage_val in np.ndenumerate(voltage_samples):
    
    # capacitor filter
    u[0] = voltage_val
    # i(n) = (T*v(n) + T*v(n-1) + 2*L*i(n-1))/(2*L)
    # y[0] = (t_sample*u[0] + t_sample*u[1] + 2*L*y[1])/(2*L)
    
    # i(n) = (T*v(n) + T*v(n-1) + 2*L*i(n-1) - T*R*i(n-1))/(2*L + T*R)
    y[0] = (t_sample*u[0] + t_sample*u[1] + 2*L*y[1] - t_sample*R*y[1])/(2*L + t_sample*R)

    u[1] = u[0]     # u(n-1) = u(n)
    y[1] = y[0]     # y(n-1) = y(n)

    current_samples[voltage_idx] = y[0]
    # end of filter


plt.plot(time_array,voltage_signal,label='full signal',ds='steps')
plt.plot(tsample_array,voltage_samples,label='input signal',ds='steps')
plt.legend()
plt.show()

plt.figure()
# following plot has dc offset b/c ideal ind or lack of integration constant
plt.plot(tsample_array,current_samples,label='output signal',ds='steps')
plt.legend()
plt.show()
