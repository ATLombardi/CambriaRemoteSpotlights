import elechouse
import pid
import comms
import sensors

from time import sleep_us

# --"constants"--
LOOP_DELAY = 10 # us
SER_BUS    = 2
SER_BAUD   = 115200

def main ():
    print ('connection successful')

    # -- Set Up Variables --
    # for loop iteration
    old_pos_a = 0
    old_pos_b = 0

    # -- set Up Systems --
    # serial port
    ser = comms.Serial(SER_BUS, SER_BAUD)

    # encoders
    encA = sensors.Encoder(pyb.Timer(4), pyb.Pin.board.X10, pyb.Pin.board.X9)
    encB = sensors.Encoder(pyb.Timer(2), pyb.Pin.board.X4, pyb.Pin.board.X3)

     # motor drivers
    motor_a = elechouse.Driver('X8',  'X7', 'X6','X5')
    motor_b = elechouse.Driver('Y12','Y11','Y10','Y9')

    # PID controllers
    control_a = pid.Controller(P=1)
    control_b = pid.Controller(P=1)

    motor_a.enable()
    motor_b.enable()

    # zero the encoders
    # -- TEMPORARY METHOD --
    encA.Zero()
    encB.Zero()

    # -- Enter Main Loop --
    while True:
        # read Serial
        setpoint_a = ser.get_cmd(ser.CMD_SPA)
        setpoint_b = ser.get_cmd(ser.CMD_SPB)

        # read encoders
        new_pos_a = encA.Read()
        v_a = new_pos_a - old_pos_a
        old_pos_a = new_pos_a

        new_pos_b = encB.Read()
        v_b = new_pos_b - old_pos_b
        old_pos_b = new_pos_b

        # run controllers
        act_a = control_a.run(setpoint_a,v_a,LOOP_DELAY)
        act_b = control_b.run(setpoint_b,v_b,LOOP_DELAY)

        # apply results
        motor_a.set_speed(act_a)
        motor_b.set_speed(act_b)

        # regulate loop rate
        sleep_us(LOOP_DELAY)
