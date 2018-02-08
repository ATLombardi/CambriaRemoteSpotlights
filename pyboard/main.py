import elechouse
import pid
import comms
import sensors

import time
import micropython
# in case we crash during an interrupt, this lets more be printed
micropython.alloc_emergency_exception_buf(100)

# --"constants"--
#LOOP_DELAY = 10 # us
SER_BUS    = 6
SER_BAUD   = 115200
SIDE_TAG   = 'R' # we're the right light

# set to true to prevent entry into 'main' in case of resets during testing
TEST_ENDURANCE = True

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
      v = new_pos - old_pos
      old_pos = new_pos

      act = con.run(setpoint,new_pos,del_time)
    #  print('pos:',new_pos,'action:',act)
      if (SIDE_TAG == 'R'):
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
#  motor_b.enable()

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
  ext_a = pyb.ExtInt(
    pyb.Pin('Y8'),
    pyb.ExtInt.IRQ_RISING,
    pyb.Pin.PULL_NONE,
    lambda a:encoder_a.Zero()
  )

  ext_b = pyb.ExtInt(
    pyb.Pin('X2'),
    pyb.ExtInt.IRQ_RISING,
    pyb.Pin.PULL_NONE,
    lambda b:encoder_b.Zero()
  )

  # now let's try to get to what we thought was zero
  zeroing_last = encoder_a.Read()
  zeroing_now  = zeroing_last
  while not (zeroing_last == 0) and not (zeroing_now == 0):
    # read in the encoder value
    zeroing_now = encoder_a.Read()
    # evaluate the clamped P controller (del_time isn't important when K_D is 0)
    speed = control_a.run(0,zeroing_now,100)
    if (SIDE_TAG == 'R'):
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
  control_a.set_K_P(0.007)
  control_a.set_K_I(0)
  control_a.set_K_D(0.012)
  control_a.set_saturation(-20,20)
  
  control_b.set_K_P(1)
  control_b.set_K_I(0)
  control_b.set_K_D(0)
  control_b.set_saturation(-40,40)

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

#    test_counter += del_time

#    if test_counter >= 1000000:
#      test_light.toggle()
#      test_counter = 0

    # read Serial
    serial.update_cmds()
    setpoint_a = serial.read_cmd(serial.CMD_SPA)
#    setpoint_b = serial.read_cmd(serial.CMD_SPB)

    # read encoders
    new_pos_a = encoder_a.Read()
    v_a = new_pos_a - old_pos_a
    old_pos_a = new_pos_a

    new_pos_b = encoder_b.Read()
    v_b = new_pos_b - old_pos_b
    old_pos_b = new_pos_b

    # update serial feedback
#    print ('a:',new_pos_a,' b:',new_pos_b)
    serial.refresh_reply(new_pos_a, new_pos_b)
    serial.send_reply()

    # run controllers
    act_a = control_a.run(setpoint_a,new_pos_a,del_time)
    if (SIDE_TAG == 'R'):
      act_a = act_a * -1 # flip the direction of A's rotation

#    act_b = control_b.run(setpoint_b,new_pos_b,del_time)

    # apply results
    motor_a.set_speed(act_a)
#    motor_b.set_speed(act_b)
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
