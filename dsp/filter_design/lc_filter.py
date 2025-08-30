from scipy import signal
import numpy as np
import matplotlib.pyplot as plt

# LC filter transfer function
# H(s) = 1/(s^2*LC + s*RC + 1)

R = 0.1
L = 0.01
C = 1000.0e-6

num_lc = [1]
den_lc = [L*C, R*C, 1]

lc_h = signal.lti(num_lc,den_lc)

w, mag, phase = signal.bode(lc_h, np.arange(100000))

# plt.figure()
plt.subplot(2, 1, 1)
plt.grid()
plt.semilogx(w,mag)
# plt.show()

# plt.figure()
plt.subplot(2, 1, 2)
plt.grid()
plt.semilogx(w,phase)
plt.show()