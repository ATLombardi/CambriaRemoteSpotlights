import elechouse
import pid
import comms
import sensors

import time

# --"constants"--
#LOOP_DELAY = 10 # us
SER_BUS    = 6
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
    control_a = pid.Controller(P=5, I=0.0001, D=0)
    control_b = pid.Controller(P=1)

    motor_a.enable()
    motor_b.enable()

    # zero the encoders
    # -- TEMPORARY METHOD --
    encA.Zero()
    encB.Zero()

    # note the time
    last_time = time.ticks_us()
    # make this exist, for later use
    this_time = last_time

    # -- Enter Main Loop --
    while not ser.should_close():
        # determine loop speed
        this_time = time.ticks_us()
        del_time  = time.ticks_diff(this_time, last_time)
        last_time = this_time

        # read Serial
        ser.update_cmds()
        setpoint_a = ser.read_cmd(ser.CMD_SPA)
        setpoint_b = ser.read_cmd(ser.CMD_SPB)

        # read encoders
        new_pos_a = encA.Read()
        v_a = new_pos_a - old_pos_a
        old_pos_a = new_pos_a

        new_pos_b = encB.Read()
        v_b = new_pos_b - old_pos_b
        old_pos_b = new_pos_b

        # update serial feedback
#        print ('a:',new_pos_a,' b:',new_pos_b)
        ser.refresh_reply(new_pos_a, new_pos_b)
        ser.send_reply()

        # run controllers
        act_a = control_a.run(setpoint_a,new_pos_a,del_time)
        act_b = control_b.run(setpoint_b,new_pos_b,del_time)

        # apply results
        motor_a.set_speed(act_a)
        motor_b.set_speed(act_b)

        # regulate loop rate
#        if LOOP_DELAY < del_time:
#          print ('Loop took a long time! ',del_time)
#        sleep_us(LOOP_DELAY)

    # after the serial port tells us to shut down
    print ('Master closed serial port, disabling motors...')
    motor_a.disable()
    motor_b.disable()
    print ('System stopped. Good night.')
