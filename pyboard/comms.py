## comms.py ##
# Wrapper for the UART serial interface on the pyboard.
# Handles sending / recieving data with the Raspberry Pi over RS-232.

from pyb import UART

class Serial:
    # the UART object this class uses
    __uart__ = None

    # indicates that we recently got a message
    __flag_reply__ = False

    # command data array
    __cmds__  = [0,0,0,0,0]

    # reply data array
    __reply__ = ['','A','000','B','000']

    # expected length of command data
    LEN_CMD = 4

    # command index 'constants'
    CMD_SPA = 2
    CMD_SPB = 4
    CMD_ACK = 0

    # stores which side this unit is on (R or L)
    side_tag = '!' # defaults to "doesn't know", set from main

    # stores whether we've seen a shutdown notice from the Pi
    __flag_down__ = False

    # data-input mode tracking
    __mode__ = 0

    # create a new Serial object
    def __init__ (self, bus_num, baud, b=8, p=None, s=1):
        self.__uart__ = UART(bus_num, baud)
        self.__uart__.init(baud, bits=b, parity=p, stop=s)

    # simple wrapper
    def recv (self, count=1):
        return self.__uart__.read(count)

    # simple wrapper
    def send (self, data):
#        print ('>>',data)
        self.__uart__.write(data)

    # returns the number of characters waiting
    def is_waiting (self):
        return self.__uart__.any()

    # refresh the local command cache
    def update_cmds (self):
        if self.is_waiting() and self.__mode__ == 0:
            dat = self.recv()
            if dat == b'A' or dat == b'a':
                self.__mode__ = 1
#                print('Mode is now 1')
            elif dat == b'B' or dat == b'b':
                self.__mode__ = 2
            elif dat == b'?':
                self.__reply__[self.CMD_ACK] = self.side_tag
            elif dat == b'K':
                self.__flag_down__ = True
        elif self.is_waiting() > self.LEN_CMD-1:
            if self.__mode__ == 1:
                self.__cmds__[self.CMD_SPA] = int(self.recv(self.LEN_CMD))
                self.__mode__ = 0
                self.__flag_reply__ = True
#                print('Read:',self.__cmds__[self.CMD_SPA],'and Mode is now 0.')
            elif self.__mode__ == 2:
                self.__cmds__[self.CMD_SPB] = int(self.recv(self.LEN_CMD))
                self.__mode__ = 0
                self.__flag_reply__ = True

    # pull the latest data from the command list
    def read_cmd (self, index):
        if index == self.CMD_SPA:
            ret = self.__cmds__[self.CMD_SPA]
        elif index == self.CMD_SPB:
            ret = self.__cmds__[self.CMD_SPB]
        else:
            ret = 0
        return ret

    # put some data into the reply buffer
    def refresh_reply (self, ra, rb):
        self.__reply__[self.CMD_SPA] = '{:+06}'.format(ra)
        self.__reply__[self.CMD_SPB] = '{:+06}'.format(rb)
#        print('built:',self.__reply__)

    # send a reply to the master
    def send_reply (self):
        if self.__flag_reply__:
            for x in range (len(self.__reply__)):
                self.send(self.__reply__[x])
            self.__reply__[self.CMD_ACK] = ' '
            self.__flag_reply__ = False;
#            print ('replied')

    # check whether the shutdown flag is raised
    def should_close (self):
        return self.__flag_down__

# for testing serial communication
def ser_test ():
  from time import sleep_us
  mail = Serial(6,115200)
  x = 0
  y = 0
  while True:
    mail.update_cmds()
    x = mail.read_cmd(mail.CMD_SPA)
    y = mail.read_cmd(mail.CMD_SPB)
    mail.refresh_reply(x,y)
    mail.send_reply()
    sleep_us(10)
