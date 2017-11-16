## comms.py ##
## Wrapper for the USB to RS-232 serial converters ##

import serial

class RS232:
  # track what we're processing inputs for
  __state__  = 0

  # stores which side the pyboard is on (L or R)
  __side__   = '?'

  # buffer for incoming data
  __inbox__  = [' ','A','+000','B','+000']

  # command index 'constants'
  CMD_SPA = 2
  CMD_SPB = 4
  CMD_ACK = 0

  # expected length of command data
  LEN_CMD = 4

  # sets up a serial connection on PORT at BAUD rate
  def __init__ (self, port, baud,
    parity=serial.PARITY_NONE,
    stop=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS
  ):
    # create and activate a serial port object
    self.ser = serial.Serial(port,baud,parity=parity,stopbits=stop,bytesize=bytesize)
    # check that the connection worked
    if not self.ser.isOpen():
      self.ser.open()
    # ask the pyboard to verify its side
    self.send('?')

  # call this when the serial port should be shut down
  def close (self):
    # notify the pyboard that we're shutting down
    self.send('K')
    # release the serial port
    self.ser.close()

  # check the incoming serial stream
  def update_inbox (self):
    # if we're ready to receive data from either encoder
    if self.is_waiting() and self.__state__ == 0:
      dat = self.recv()
      if dat == b'A' or dat == b'a':
        # we're writing this data to buffer slot A
        self.__state__ = 1
        print('Mode is now 1')
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

    # if we're reading into a buffer slot and we've received enough data
    elif self.is_waiting() > self.LEN_CMD-1:
      if self.__state__ == 1:
        self.__inbox__[self.CMD_SPA] = int(self.recv(self.LEN_CMD))
        self.__state__ = 0
      elif self.__state__ == 2:
        self.__inbox__[self.CMD_SPB] = int(self.recv(self.LEN_CMD))
        self.__state__ = 0

  # return a piece of data from the buffer
  def read_inbox (self, index):
    if index == self.CMD_SPA:
      ret = self.__inbox__[self.CMD_SPA]
    elif index == self.CMD_SPB:
      ret = self.__inbox__[self.CMD_SPB]
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

  # send a new target position to the pyboard
  def send_command (self, pos_a, pos_b):
    cmd_a = self.coord_to_enc (pos_a)
    cmd_b = self.coord_to_enc (pos_b)
    self.send ( 'A'+'{:+04}'.format(cmd_a) + 'B'+'{:+04}'.format(cmd_b) )

  # which side the attached pyboard is on (L or R)
  def get_side (self):
    return __side__

  # simple wrapper
  def recv (self, count=1):
    return self.ser.read(count)

  # simple wrapper
  def send (self, data):
    self.ser.write(data.encode())

  # returns the number of characters waiting
  def is_waiting (self):
    return self.ser.inWaiting()
