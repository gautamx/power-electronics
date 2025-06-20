"""
Open-loop Buck Converter Model v1
Author: Gautam
Date: June 2025
"""

# params
Vin = 24            # input voltage
Vout = 12           # output voltage
D = Vout/Vin        # duty cycle
Iout = 2            # output current
Pout = Vout * Iout  # output power

# Load
R = Vout/Iout

fsw = 50e3          # switching frequency
Tsw = 1/fsw         # switching time period
t_on = D * Tsw      # switch on time
t_off = (1-D) * Tsw # switch off time

# inductor value
delta_iL_pu = 0.1      # 10% inductor current ripple
delta_iL = delta_iL_pu * Iout
L = ((Vin - Vout) * t_on) / delta_iL

# capacitor value
delta_Vout_pu = 0.05   # 5% output voltage ripple
delta_Vout = delta_Vout_pu * Vout
C = (delta_iL * Tsw) / (8 * delta_Vout)

# simulation params
sim_time = 1e-3     # simulation time of 0.05s
time_step = 1e-7    # 0.1us time step
num_steps = int(sim_time/time_step)

dt = time_step
duty_cycle = D

#initializing the state variables
iL = 0
Vc = 0

# initializing arrays for data storage
time = []
inductor_current = []
capacitor_voltage = []
switching_state = []

# simulation loop
for i in range(num_steps):
    t = i * time_step

    # dividing the 't' value, which increments in units of 'time_step', with switching time period. 
    # The remainder (t_mod) keeps increasing until we hit the end of one cycle. 
    # After that the remainder (t_mod) is reset. This way we can track the switching time period with time steps.
    t_mod = t % Tsw

    # deciding whether switch is ON or OFF based on duty cycle
    if (t_mod < (duty_cycle*Tsw)):
        switch_state = True
    else:
        switch_state = False

    # calculating the
    if (switch_state):
        # when switch is ON
        # VL = L * diL/dt = Vin - Vout  
        # Vout=Vc but I have defined Vout as a constant for other purpose.
        diL_dt = (Vin - Vc) / L
        
        # iL = iC + iR
        # iC = C * dVc/dt
        # dVc_dt = (Tsw * diL_dt)/(8*C)     # another eqn which will give slightly different initial behaviour
        dVc_dt = (iL - (Vc/R)) / C              
    
    else:
    # when switch is OFF
        # VL = L * diL/dt = -Vc
        diL_dt = (-Vc)/L
        
        # dVc_dt = (Tsw * diL_dt)/(8*C)
        dVc_dt = (iL - (Vc/R)) / C
                  
    # calculating the state variables by integrating them
    # discrete integration is done using Euler method
    iL = iL + (diL_dt * time_step)
    Vc = Vc + (dVc_dt * time_step)

    time.append(t)
    inductor_current.append(iL)
    capacitor_voltage.append(Vc)
    if switch_state:
        switching_state.append(1)
    else:
        switching_state.append(0)


#plotting the data
import matplotlib.pyplot as plt

# Inductor Current plot
plt.subplot(3, 1, 1)
plt.plot(time, inductor_current, label='Inductor Current (iL)', color='b')
plt.ylabel('Current (A)')
plt.title('Inductor Current vs Time')
plt.grid(True)
plt.legend()

# Cap voltage plot
plt.subplot(3, 1, 2)
plt.plot(time, capacitor_voltage, label='Capacitor Voltage (Vc)', color='r')
plt.ylabel('Voltage (V)')
plt.title('Capacitor Voltage vs Time')
plt.grid(True)
plt.legend()

# Switch state plot
plt.subplot(3, 1, 3)
plt.plot(time, switching_state, label='Switching State', color='g')
plt.ylabel('State')
plt.title('Switching State vs Time')
plt.grid(True)
plt.legend()

plt.show()