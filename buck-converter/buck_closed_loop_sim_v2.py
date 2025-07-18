"""
Closed-loop Buck Converter Model v2
Author: Gautam
Date: June 2025
"""
import math

# params
Vin = 24            # input voltage
Iout = 2            # output current
D = 0.5             # initial duty cycle

fsw = 50e3          # switching frequency
Tsw = 1/fsw         # switching time period

# Controller params
Vref = 18           # reference output voltage
Kp = 0.05
Ki = 5
nominal_duty = Vref/Vin     # feedforward term
duty_min = 0.1
duty_max = 0.9

# Load
R = Vref/Iout       # using variable load for constant current 
# R = 10              # constant load

t_on = nominal_duty * Tsw

# inductor value
delta_iL_pu = 0.1      # 10% inductor current ripple
delta_iL = delta_iL_pu * Iout
L = ((Vin - Vref) * t_on) / delta_iL

# capacitor value
delta_Vout_pu = 0.05   # 5% output voltage ripple
delta_Vout = delta_Vout_pu * Vref
C = (delta_iL * Tsw) / (8 * delta_Vout)

# simulation params
sim_time = 5e-3     # simulation time of 0.05s
time_step = 1e-7     # 0.1us time step
num_steps = int(sim_time/time_step)
# print(num_steps)

dt = time_step

#initializing the state variables
iL = 0
Vc = 0
error = 0           # PI controller error term
integral_error = 0  # PI controller integral error term
pi_output = 0
duty_cycle = nominal_duty

# initializing arrays for data storage
time = []
inductor_current = []
capacitor_voltage = []
switching_state = []
controller_output = []
error_term = []

# simulation loop
for i in range(num_steps):
    t = i * time_step

    if i > num_steps/2:
        Vref = 12
        nominal_duty = Vref/Vin     
        # necessary to update nominal duty otherwise the controller action will not follow reference correctly

    # dividing the 't' value, which increments in units of 'time_step', with switching time period. 
    # The remainder (t_mod) keeps increasing until we hit the end of one cycle. 
    # After that the remainder (t_mod) is reset. This way we can track the switching time period with time steps.
    t_mod = t % Tsw

    # PI controller - operating at switching frequency
    controller_step = int(Tsw/time_step)
    if (i % controller_step == 0):    # will execute once every cycle
        
        #calculate error
        error = Vref - Vc

        # update integral term
        integral_error = integral_error + (error * Tsw)     
        # because we are updating this term once every cycle not every time-step

        # PI controller output
        pi_output = Kp*error + Ki*integral_error
        # print(pi_output)

        # duty cycle with feed forward term 'nominal_duty'
        duty_cycle = nominal_duty + pi_output

        # Clamp duty cycle to limits
        if duty_cycle > duty_max:
            duty_cycle = duty_max
        
        elif duty_cycle < duty_min:
            duty_cycle = duty_min

    # deciding whether switch is ON or OFF based on duty cycle
    if (t_mod < (duty_cycle*Tsw)):
        switch_state = True
    else:
        switch_state = False

    # calculating the
    if (switch_state):
        # when switch is ON
        # VL = L * diL/dt = Vin - Vc  
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

    # Only append when controller actually updates
    if (i % controller_step == 0):
        controller_output.append(pi_output)
        error_term.append(error)   

#plotting the data
import matplotlib.pyplot as plt

# Inductor Current plot
plt.subplot(3, 2, 1)
plt.plot(time, inductor_current, label='Inductor Current (iL)', color='b')
plt.ylabel('Current (A)')
plt.title('Inductor Current vs Time')
plt.grid(True)
plt.legend()

# Cap voltage plot
plt.subplot(3, 2, 5)
plt.plot(time, capacitor_voltage, label='Capacitor Voltage (Vc)', color='r')
plt.ylabel('Voltage (V)')
plt.title('Capacitor Voltage vs Time')
plt.grid(True)
plt.legend()

# Switch state plot
plt.subplot(3, 2, 3)
plt.plot(time, switching_state, label='Switching State', color='g')
plt.ylabel('State')
plt.title('Switching State vs Time')
plt.grid(True)
plt.legend()

# error plot
plt.subplot(3, 2, 2)
plt.plot(error_term, label='Error', color='r')
plt.ylabel('error')
plt.title('error vs Time')
plt.grid(True)
plt.legend()

# controller output plot
plt.subplot(3, 2, 4)
plt.plot(controller_output, label='Controller Output', color='b')
plt.ylabel('PI output')
plt.title('PI Output vs Time')
plt.grid(True)
plt.legend()

plt.tight_layout()
plt.show()