import numpy as np
import matplotlib.pyplot as plt

# sinusoid signal
# generate a signal with duration of 1 sec

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

freq = 50.0
omega = 2*np.pi*freq
mag = 5.0

# sinusoidal input signal generation
inp_signal = mag*np.sin(omega*time_array)

t_sample = 200.0e-6
num_skip = int(t_sample/t_step)

tsamp_array = time_array[::num_skip]
sample_signal = inp_signal[::num_skip]

print(len(tsamp_array))
print(len(time_array))

plt.plot(time_array,inp_signal,label='full signal',ds='steps')
plt.plot(tsamp_array,sample_signal,label='sample signal',ds='steps')
plt.legend()
plt.show()