import elechouse
import pid
import comms

from time import sleep_us

# --"constants"--
LOOP_DELAY = 10 # us
SER_BUS    = 2
SER_BAUD   = 115200

def main ():
    print ('connection successful')

    # -- Set Up Variables --
    # target position
    setpoint_a = 0

    # for loop iteration
    old_pos_a = 0

    # -- set Up Systems --
    ser = comms.Serial(SER_BUS, SER_BAUD)

    motor_a = elechouse.Driver('B7','B6','B5','B4')
    motor_a.enable()
    control_vel_a = pid.Controller(P=1)

    # -- Enter Main Loop --
    while True:
        # read Serial
        setpoint_a = ser.get_cmd(ser.CMD_SPA)
        setpoint_b = ser.get_cmd(ser.CMD_SPB)

        # read encoders
        new_pos_a = 0
        v_a = new_pos_a - old_pos_a
        old_pos_a = new_pos_a

        # run controllers
        act_a = control_vel_a.run(setpoint_a,v_a,LOOP_DELAY)

        # apply results
        #print ('motor A:', act_a)
        motor_a.set_speed(act_a)

        # regulate loop rate
        sleep_us(LOOP_DELAY)
