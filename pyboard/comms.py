## comms.py ##
# Wrapper for the UART serial interface on the pyboard.
# Handles sending / recieving data with the Raspberry Pi over RS-232.

from pyb import UART
import re # regex library

class Serial:
    # the UART object this class uses
    __uart__ = None

    # indicates that we recently got a message
    __flag_reply__ = False

    # command data array
    __cmds__  = [0,0,0,0,0,0]

    # reply data array
    __reply__ = ['','A','000',',','B','000','\n']

    # expected length of command data
    LEN_CMD = 4

    # correct command number formatting
    # allows + OR - OR 0-9
    FORM_CMD = re.compile(b'\+|\-|\d')

    # command index 'constants'
    CMD_SPA = 2
    CMD_SPB = 5
    CMD_ACK = 0

    # stores which side this unit is on (R or L)
    side_tag = '!' # defaults to "doesn't know", set from main

    # stores whether we've seen a shutdown notice from the Pi
    __flag_down__ = False

    # data-input mode tracking
    __state__ = 0

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
        # don't do anything if there's nothing to be read
        if self.is_waiting():
            # read in an initial character
            dat = self.recv()
            # state 0 is 'waiting for command'
            if self.__state__ == 0:
                if dat == b'A' or dat == b'a': # read into cmd A
                    self.__state__ = 1
                    print('moving to state A')
                elif dat == b'B' or dat == b'b': # read into cmd B
                    self.__state__ = 2
                    print('moving to state B')
                elif dat == b'?': # identity request
                    self.__reply__[self.CMD_ACK] = self.side_tag
                elif dat == b'K': # shutdown alert
                    self.__flag_down__ = True

            # state 1 and 2 are 'reading in numbers'
            else:
                val = []
                should_check = True
                # until we see a valid terminating character, stay here
                # TODO - possibly rework to avoid Blocking behavior
                while should_check:
                    if self.is_waiting():
                        dat = self.recv()
                        print(dat)
                        if self.FORM_CMD.match(dat): # valid digit, keep
                            val.append(dat)
                            print('->')
                        elif dat == b',' or dat == b'\n': # terminating chars
                            should_check = False

                # now parse the array into a number
                if len(val) > 0:
                    try:
                        # make an int from the combined decoded characters in val
                        val = int(''.join(map(bytes.decode,val)))
                    except ValueError:
                        print ('Error decoding',val)
                        val = 0
                else:
                    val = 0

                # store the successful conversion into the proper location
                if self.__state__ == 1:
                    self.__cmds__[self.CMD_SPA] = val
                    print ('A is now',val)
                elif self.__state__ == 2:
                    self.__cmds__[self.CMD_SPB] = val
                    print ('B is now',val)

                # return to state zero
                self.__state__ = 0
                # indicate that we can reply now
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
    mail.update_cmds()
    x = mail.read_cmd(mail.CMD_SPA)
    y = mail.read_cmd(mail.CMD_SPB)
#    print('x:',x,', y:',y)
    mail.refresh_reply(x,y)
    mail.send_reply()
    sleep_us(10)
