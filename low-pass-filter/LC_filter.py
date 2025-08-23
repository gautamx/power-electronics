import numpy as np
import matplotlib.pyplot as plt

# deciding time-step
# typical power converter switching frequency ~5kHz
# cycle time period of 200us -- sampling time

# time-step should be << 200us
# let time-step for signal generation be 1us

t_duration = 0.4
t_step = 1.0e-6

num_samples = int(t_duration/t_step)

# generate an array from 0 to (10^6 - 1)
# mult t_step to get each time instant
time_array = np.arange(num_samples)*t_step

freq = 50.0     # 50Hz
omega = 2*np.pi*freq    # rad/s
# omega_noise = 2*np.pi*10000  # 10kHz noise component, switching frequency noise
omega_noise = 2*np.pi*13*50  # 13th harmonic noise component
mag = np.sqrt(2)*230    # input voltage
C = 500.0e-6    # 500uF capacitor
R = 0.05        # 0.05 ohm     
# 'R' assumed in series with inductor to avoid dc offset due to lossless system 
# small resistor in series with inductor to emulate lossy circuit
L = 0.001       # 1mH inductor
# time constant R*C will decide the settling time
# settling time = 4*R*C

# sinusoidal input signal generation
inp_voltage_signal = mag*( np.sin(omega*time_array) + 0.1*np.sin(omega_noise*time_array) )

# add harmonics and random noise
# inp_voltage_signal = mag*(np.sin(omega*time_array) \
#                     + 0.02 * np.sin(3*omega*time_array) \
#                     + 0.05 * np.random.normal(0, 1, len(time_array)))

t_sample = 200.0e-6
num_skip = int(t_sample/t_step)

tsample_array = time_array[::num_skip]
inp_voltage_samples = inp_voltage_signal[::num_skip]

# initialize our output
out_voltage_samples = np.zeros(inp_voltage_samples.size)

# filter input
u = np.zeros(3)     # present value u[0]=vin(n) and past value u[1]=vin(n-1), u[2]=vin(n-2)
y = np.zeros(3)     # present value y[0]=vout(n) and past value y[1]=vout(n-1), y[2]=vout(n-2)

# ISR with hardware here
# calculate the output
for volt_idx, volt_val in np.ndenumerate(inp_voltage_samples):
    
    # capacitor filter
    u[0] = volt_val
    
    # v(n) = ( (1/LC)*(vin(n) + 2*vin(n-1) + vin(n-2)) ) \
    #       - ( vout(n-1)*(-2*(2/T)*(2/T) + 2/LC) ) \
    #       - ( vout(n-2)*((2/T)*(2/T) - 2R/LT + 1/LC) ) \
    #       / ((2/T)*(2/T) + 2R/LT + 1/LC))
    y[0] = ( ( (1/(L*C))*(u[0] + 2*u[1] + u[2]) ) \
            - ( (y[1]) * (((-2)*((2/t_sample)**2)) + (2/(L*C))) ) \
            - ( (y[2]) * ((((2/t_sample)**2)) - ((2*R)/(L*t_sample)) + (1/(L*C))) ) ) \
            / ( ((2/t_sample)**2) + (2*R/(L*t_sample)) + (1/(L*C)) )

    u[2] = u[1]     # u(n-2) = u(n-1)
    u[1] = u[0]     # u(n-1) = u(n)
    y[2] = y[1]     # u(n-2) = u(n-1)
    y[1] = y[0]     # y(n-1) = y(n)

    out_voltage_samples[volt_idx] = y[0]
    # end of filter

# plt.figure()
# plt.plot(time_array,inp_voltage_signal,label='full signal',ds='steps')
# plt.plot(tsample_array,inp_voltage_samples,label='input signal',ds='steps')
# plt.legend()
# plt.show()

# plt.figure()
# plt.plot(tsample_array,out_voltage_samples,label='output signal',ds='steps')
# plt.legend()
# plt.show()

plt.figure()
plt.plot(tsample_array,inp_voltage_samples,label='input signal',ds='steps')
plt.plot(tsample_array,out_voltage_samples,label='output signal',ds='steps')
plt.legend()
plt.show()
