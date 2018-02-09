import elechouse
import pid
import comms
import sensors

import time
import micropython
# in case we crash during an interrupt, this lets more be printed
micropython.alloc_emergency_exception_buf(100)

# --"constants"--
LOOP_DELAY = 1         # microseconds to sleep between main loops
SER_BUS    = 6         # which hardware UART port is being used
SER_BAUD   = 115200    # serial communication speed
SIDE_TAG   = 'R'       # we're the right-side light
LIM_MAX_A  =  5000     # horizontal range max
LIM_MIN_A  = -2000     # horizontal range min
LIM_MAX_B  =  4000     # vertical range max
LIM_MIN_B  = -4000     # vertical range min
SERIAL_COUNT_LOOP = 10 # how many control loops per serial check
MOT_ACT_EPSILON   =  5 # minimum motor effort until 

# set to true to prevent entry into 'main' in case of resets during testing
TEST_ENDURANCE = False

# shared objects
serial    = None

encoder_a = None
motor_a   = None
control_a = None

encoder_b = None
motor_b   = None
control_b = None

def test_enc (encoder):
  enc = None
  old = 0
  if (encoder == 'A'):
    enc = encoder_a
  else:
    enc = encoder_b
  enc.Zero()
  while True:
    val = enc.Read()
    if (not (val == old)):
      print(val)
      old = val
      time.sleep_us(1)
# /end test_enc

def test_step (motor, setpoint):
  enc = None
  mot = None
  con = None
  old_pos = 0

  if (motor == 'A'):
    old_pos = encoder_a.Read()
    enc = encoder_a
    mot = motor_a
    con = control_a
  elif (motor == 'B'):
    old_pos = encoder_b.Read()
    enc = encoder_b
    mot = motor_b
    con = control_b

  print ('stepping motor',motor,'from',old_pos,'to',setpoint)
  mot.enable()
  last_time = time.ticks_us()
  try:
    while True:
      this_time = time.ticks_us()
      del_time  = time.ticks_diff(this_time, last_time)
      last_time = this_time

      new_pos = enc.Read()
#      v = new_pos - old_pos
#      old_pos = new_pos

      act = con.run(setpoint,new_pos,del_time)
    #  print('pos:',new_pos,'action:',act)
      if (motor == 'A'):
        act = act * -1 # flip the direction of A's rotation
      mot.set_speed(act)
      time.sleep_us(1)
  except KeyboardInterrupt:
    pass # ^C is the expected way to get out of this, for now
  finally:
    print('Stopped at',enc.Read())
    mot.stop()
    mot.disable()
# /end test_step

def test_con (controller, P,I,D,satmin,satmax):
  con = None
  if (controller == 'A'):
    con = control_a
  elif (controller == 'B'):
    con = control_b
  con.set_K_P(P)
  con.set_K_I(I)
  con.set_K_D(D)
  con.set_saturation(satmin,satmax)
# /end test_con

def init ():
  # -- set Up Systems --
  # serial port
  global serial
  serial = comms.Serial(SER_BUS, SER_BAUD)
  serial.side_tag = SIDE_TAG 

  # encoders
  global encoder_a
  encoder_a = sensors.Encoder(pyb.Timer(2), pyb.Pin.board.X4,  pyb.Pin.board.X3)
  global encoder_b
  encoder_b = sensors.Encoder(pyb.Timer(4), pyb.Pin.board.X10, pyb.Pin.board.X9)

  # motor drivers
  global motor_a
  motor_a = elechouse.Driver('X8',  'X7', 'X6','X5')
  global motor_b
  motor_b = elechouse.Driver('Y12','Y11','Y10','Y9')

  # PID controllers
  global control_a
  control_a = pid.Controller()
  global control_b
  control_b = pid.Controller()
# /end init

def main ():
  # for loop iteration
  old_pos_a = 0
  old_pos_b = 0

  motor_a.enable()
  motor_b.enable()

  # zero the encoders
  # assign some strict limits to make zeroing simpler
  control_a.set_K_P(1)
  control_b.set_K_P(1)
  control_a.set_saturation(-10,10)
  control_b.set_saturation(-10,10)

  # attempt to remember where we were on shutdown
  logfile = open('log/encoder.dat','rw')
  val = logfile.readline()
  if (val):
    encA.Set(int(val))
    encB.Set(int(logfile.readline()))
  else:
    encoder_a.Set(0)
    encoder_b.Set(0)

  # set up an interrupt on the index pin of the encoders, to zero them
#  ext_a = pyb.ExtInt(
#    pyb.Pin('Y8'),
#    pyb.ExtInt.IRQ_RISING,
#    pyb.Pin.PULL_NONE,
#    lambda a:encoder_a.Zero()
#  )

#  ext_b = pyb.ExtInt(
#    pyb.Pin('X2'),
#    pyb.ExtInt.IRQ_RISING,
#    pyb.Pin.PULL_NONE,
#    lambda b:encoder_b.Zero()
#  )

  # now let's try to get to what we thought was zero
  zeroing_last = encoder_a.Read()
  zeroing_now  = zeroing_last
  while not (zeroing_last == 0) and not (zeroing_now == 0):
    # read in the encoder value
    zeroing_now = encoder_a.Read()
    # evaluate the clamped P controller (del_time isn't important when K_D is 0)
    speed = control_a.run(0,zeroing_now,100)
    speed = speed * -1 # flip the direction of A's rotation
    motor_a.set_speed( speed )
    zeroing_last = zeroing_now
  # finished, stop motor
  motor_a.stop()

  # try to get to zero with B
#  zeroing_last = encoder_b.Read()
#  zeroing_now  = zeroing_last
#  while not (zeroing_last == 0) and not (zeroing_now == 0):
#    zeroing_now = encoder_b.Read()
#    motor_b.set_speed(zeroing_act_b)
#    zeroing_last = zeroing_now
#    motor_b.set_speed(act_b)
#    act_b = control_b.run(setpoint_b,new_pos_b,del_time)
  # finished, stop motor
#  motor_b.stop()

  # assign the actual values used during run time
  control_a.set_K_P(   0.010)
  control_a.set_K_I(   0)
  control_a.set_K_D(5000)
  control_a.set_K_W(   0)
  control_a.set_saturation(-20,20)
  
  control_b.set_K_P(   0.050)
  control_b.set_K_I(   0)
  control_b.set_K_D(5000)
  control_b.set_K_W(   0)
  control_b.set_saturation(-20,20)

  # note the time
  last_time = time.ticks_us()
  # make this exist, for later use
  this_time = last_time
  
  # serial clock division
  serial_count = 0

  setpoint_a = encoder_a.Read()
  setpoint_b = encoder_b.Read()
  del_t_hic = 0
  # -- Enter Main Loop --
  while not serial.should_close():
    # determine loop speed
    this_time = time.ticks_us()
    del_time  = time.ticks_diff(this_time, last_time)
    last_time = this_time

    # read Serial
    if (serial_count == SERIAL_COUNT_LOOP):
      serial.update_cmds()
      setpoint_a = serial.read_cmd(serial.CMD_SPA)
      setpoint_b = serial.read_cmd(serial.CMD_SPB)

    # soft limits on the motor's range of motion. Motor A is reversed
    if (setpoint_a >= LIM_MAX_A):
      setpoint_a = LIM_MAX_A
    elif (setpoint_a <= LIM_MIN_A):
      setpoint_a = LIM_MIN_A

    # soft limits to prevent going beyond safe ranges
    if (setpoint_b >= LIM_MAX_B):
      setpoint_b = LIM_MAX_B
    elif (setpoint_b <= LIM_MIN_B):
      setpoint_b = LIM_MIN_B

    # read encoders
    new_pos_a = encoder_a.Read()
    new_pos_b = encoder_b.Read()

    # update serial feedback
#    print ('a:',new_pos_a,' b:',new_pos_b)
    if (serial_count == SERIAL_COUNT_LOOP):
#      serial.refresh_reply(new_pos_a, new_pos_b)
#      serial.send_reply()
      serial_count = 0
    else:
      serial_count += 1

    # run controllers
    # motor A needs to turn "backwards" WRT the encoder's positive
    act_a = -1 * control_a.run(setpoint_a,new_pos_a,del_time)
    act_b = control_b.run(setpoint_b,new_pos_b,del_time)

#    print('a:',act_a,' b:',act_b)
#    if (-MOT_ACT_EPSILON < act_a < MOT_ACT_EPSILON):
#      act_a = 0 # let's just cut this off, prevent rounding
#
#    if (-MOT_ACT_EPSILON < act_b < MOT_ACT_EPSILON):
#      act_b = 0

    # apply results
    motor_a.set_speed(act_a)
    motor_b.set_speed(act_b)

    time.sleep_us(LOOP_DELAY)
  # -- End Main Loop --

  # after the serial port tells us to shut down
  print ('Master closed serial port, disabling motors...')
  motor_a.disable()
  motor_b.disable()

  print ('Storing last known encoder positions...')
  logfile.seek(0)
  logfile.write('{:06d}'.format(encoder_a.Read()) )
  logfile.write('{:06d}'.format(encoder_b.Read()) )
  time.sleep(1)
  logfile.close()
  print ('System stopped. Good night.')

  machine.soft_reset()
  # wait for serial connection signal

# this will be true if the pyboard is running this file
if __name__ == "__main__":
  # pre-run escape routine: if we want to avoid running 'main'
  sw = pyb.Switch()
  l4 = pyb.LED(4)
  # indicate that the USR button window is open - hold to skip 'main'
  l4.on()
  time.sleep(1)
  l4.off()
  
  init()
  # if there's a USB connection, let them know we're ready for debugging
  print ('connection successful')
  if not sw() and not TEST_ENDURANCE:
    main()
