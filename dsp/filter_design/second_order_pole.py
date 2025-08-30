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