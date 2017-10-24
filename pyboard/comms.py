## comms.py ##
# Wrapper for the UART serial interface on the pyboard.
# Handles sending / recieving data with the Raspberry Pi over RS-232.

from pyb import UART

class Serial:
    # the UART object this class uses
    __uart__ = None

    # command data array
    __cmds__  = [0,0,0]

    # reply data array
    __reply__ = ['A','000','B','000','']

    # command index 'constants'
    CMD_SPA = 1
    CMD_SPB = 3
    CMD_ACK = 4

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
                print('Mode is now 1')
            elif dat == b'B' or dat == b'b':
                self.__mode__ = 2
            elif dat == b'?':
                self.__reply__[self.CMD_ACK] = '!'
        elif self.is_waiting() > 3:
            if self.__mode__ == 1:
                self.__cmds__[self.CMD_SPA] = int(self.recv(3))
                self.__mode__ = 0
            elif self.__mode__ == 2:
                self.__cmds__[self.CMD_SPB] = int(self.recv(3))
                self.__mode__ = 0

    # pull the latest data from the command list
    def read_cmd (self, index):
        if index == CMD_SPA:
            ret = self.__cmds__[self.CMD_SPA]
        elif index == CMD_SPB:
            ret = self.__cmds__[self.CMD_SPB]
        else:
            ret = 0
        return ret

    # put some data into the reply buffer
    def refresh_reply (self, ra, rb):
        self.__reply__[self.CMD_SPA] = '{:03}'.format(ra)
        self.__reply__[self.CMD_SPB] = '{:03}'.format(rb)

    # send a reply to the master
    def send_reply (self):
        for x in range (len(self.__reply__)):
            self.send(self.__reply__[x])
        self.__reply__[self.CMD_ACK] = ' '
