from scipy import signal
import numpy as np
import matplotlib.pyplot as plt

# second order pole transfer function
# H(s) = omega_0**2/(s^2 + 2*s*zeta*omega_0 + omega_0**2)

# R = 0.1
# L = 0.01
# C = 1000.0e-6

omega_0 = 1000.0    # resonant freq rad/s
zeta = 0.1          # damping factor

# sop = second order pole
num_sop = [omega_0**2]
den_sop = [1, 2*zeta*omega_0, omega_0**2]

sop_h = signal.lti(num_sop,den_sop)

w, mag, phase = signal.bode(sop_h, np.arange(100000))

# plt.figure()
plt.subplot(2, 1, 1)
plt.grid()
plt.title('Magnitude plot')
plt.xlabel('log(w)')
plt.ylabel('Mag in dB')
plt.semilogx(w,mag)
# plt.show()

# plt.figure()
plt.subplot(2, 1, 2)
plt.grid()
plt.title('Phase plot')
plt.xlabel('log(w)')
plt.ylabel('Phase in degrees')
plt.semilogx(w,phase)

plt.tight_layout()
plt.show()

# end of filter design



sop_h_z = sop_h.to_discrete(dt=200.0e-6, method='tustin')   
# tustin = bilinear or trapezoidal



# start of implementation

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
omega_noise = 2*np.pi*8000  # 10kHz noise component, switching frequency noise
# omega_noise = 2*np.pi*13*50  # 13th harmonic noise component
inp_mag = np.sqrt(2)*230    # input voltage

# sinusoidal input signal generation
inp_voltage_signal = inp_mag*( 1.0*np.sin(omega*time_array) + 0.2*np.sin(omega_noise*time_array) )

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
    
    # LC filter
    u[0] = volt_val
    
    # y[n] = ( den[1]*y[n-1] + num[0]*u[n] - num[1]*u[n-1] ) / den[0]
    y[0] = ( sop_h_z.num[0] * u[0] + sop_h_z.num[1] * u[1] + sop_h_z.num[2] * u[2] - sop_h_z.den[1] * y[1] - sop_h_z.den[2] * y[2] ) / sop_h_z.den[0]

    u[2] = u[1]     # u(n-2) = u(n-1)
    u[1] = u[0]     # u(n-1) = u(n)
    y[2] = y[1]     # y(n-2) = y(n-1)
    y[1] = y[0]     # y(n-1) = y(n)

    out_voltage_samples[volt_idx] = y[0]
    # end of filter

plt.figure()
plt.plot(time_array,inp_voltage_signal,label='full signal',ds='steps')
plt.plot(tsample_array,inp_voltage_samples,label='input signal',ds='steps')
plt.legend()
plt.show()

plt.figure()
plt.plot(tsample_array,out_voltage_samples,label='output signal',ds='steps')
plt.legend()
plt.show()

plt.figure()
plt.plot(tsample_array,inp_voltage_samples,label='input signal',ds='steps')
plt.plot(tsample_array,out_voltage_samples,label='output signal',ds='steps')
plt.legend()
plt.show()
