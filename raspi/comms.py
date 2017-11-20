## comms.py ##
## Wrapper for the USB to RS-232 serial converters ##

import serial
import re # regex library

class RS232:
  # track what we're processing inputs for
  __state__  = 0

  # track whether we should send a reply
  __flag_reply__ = True

  # stores which side the pyboard is on (L or R)
  __side__   = '?'

  # buffer for incoming data
  __inbox__  = [' ','A','+000','B','+000']

  # command index 'constants'
  CMD_SPA = 2
  CMD_SPB = 4
  CMD_ACK = 0

  # regex representing +,-, and 0-9
  VALUE = re.compile(b"[+\-0-9]+")

  # expected length of command data
  LEN_CMD = 3

  # sets up a serial connection on PORT at BAUD rate
  def __init__ (self, port, baud,
    parity=serial.PARITY_NONE,
    stop=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS
  ):
    # create and activate a serial port object
    self.ser = serial.Serial(port,baud,
      timeout=None,
      parity=parity,
      stopbits=stop,
      bytesize=bytesize
    )
    # check that the connection worked
    if not self.ser.isOpen():
      self.ser.open()
    # flush the buffer, deleting everything in it
    self.ser.reset_input_buffer()
    # ask the pyboard to verify its side
#    self.send('?')

  # call this when the serial port should be shut down
  def close (self):
    # notify the pyboard that we're shutting down
    self.send('K')
    # flush the buffer, deleting everything in it
    self.ser.reset_input_buffer()
    # release the serial port
    self.ser.close()

  # check the incoming serial stream
  def update_inbox (self):
    if self.is_waiting():
      # read in an initial character
      dat = self.recv()
#      print ('dat=',dat)
      if self.__state__ == 0:
        if dat == b'A' or dat == b'a':
          # we're writing this data to buffer slot A
          self.__state__ = 1
#          print('Mode is now 1')
        elif dat == b'B' or dat == b'b':
          # we're writing this data to buffer slot B
          self.__state__ = 2
        elif dat == b'L':
          # the attached pyboard has reported it's on the Left
          self.__side__ = 'L'
        elif dat == b'R':
          # the attached pyboard has reported it's on the right
          self.__side__ = 'R'
        elif dat == b'!':
          # the attached pyboard has no idea which side it is on
          self.__side__ = ' '
          print ("Warning: Pyboard orientation is unknown.")

      # states 1 and 2 are 'read in numbers'
      else:
        val = []
        should_check = True
        # until we see a valid terminating character, stay here
        # TODO = possibly rework to avoid Blocking behavior
        while should_check:
          if self.VALUE.match(dat): # valid digit
            val.append(dat)
            dat = self.recv()
          elif dat == b',' or dat == b'\n': # terminating chars
            should_check = False

        # convert it from a list into a number
        if len(val) > 0:
          try:
            val = int(''.join(map(bytes.decode,val)))
          except ValueError:
            print ('Error decoding',val)
            val = 0
        else:
          val = 0

        # store the result of the conversion
        if self.__state__ == 1:
          self.__inbox__[self.CMD_SPA] = val
        elif self.__state__ == 2:
          self.__inbox__[self.CMD_SPB] = val

        # return to state 0
        self.__state__ = 0
        # indicate that we can reply now
        self.__flag_reply__ = True

  # return a piece of data from the buffer
  def read_inbox (self, index):
    if index == self.CMD_SPA:
      ret = self.__inbox__[self.CMD_SPA]
      ret = self.enc_to_coord(int(ret))
    elif index == self.CMD_SPB:
      ret = self.__inbox__[self.CMD_SPB]
      ret = self.enc_to_coord(int(ret))
    elif index == self.CMD_ACK:
      ret = self.__inbox__[self.CMD_ACK]
    else:
      ret = 0
    return ret

  # translate screen coordinates into encoder counts
  # -- TO DO --
  def coord_to_enc (self, coord):
    if self.__side__ == 'L': # left-side spotlight
      ret = coord # DO MATH HERE
    elif self.__side__ == 'R': # right-side spotlight
      ret = coord # DO MATH HERE
    else:
      ret = coord
    return ret

  # translate encoder counts into screen coordinates
  # -- TO DO --
  def enc_to_coord (self, enc):
    if self.__side__ == 'L':
      ret = enc
    elif self.__side__ == 'R':
      ret = enc
    else:
      ret = enc
    return ret

  # send a new target position to the pyboard
  def send_command (self, pos_a, pos_b):
    if self.__flag_reply__:
      cmd_a = self.coord_to_enc (pos_a)
      cmd_b = self.coord_to_enc (pos_b)
      self.send ( 'A'+'{:+04}'.format(cmd_a)+','+'B'+'{:+04}'.format(cmd_b)+'\n' )
      self.__flag_reply__ = False

  # which side the attached pyboard is on (L or R)
  def get_side (self):
    return self.__side__

  # simple wrapper
  def recv (self, count=1):
    return self.ser.read(count)

  # simple wrapper
  def send (self, data):
    self.ser.write(data.encode())

  # returns the number of characters waiting
  def is_waiting (self):
    return self.ser.inWaiting()
