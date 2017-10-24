## elechouse.py ##
## Contains an implementation of the dual-channel motor driver sold by Elechouse. ##

# Controlling the driver:
#   _____________________________
#  |                             |
#  | EN  RPWM DIS LPWM   RESULT  |
#  |=============================|
#  | 1   PWM  0   1      forward |
#  | 1   1    0   PWM    reverse |
#  | 1   1    0   1      brake   |
#  | 0   1    0   1      coast   |
#  | X   X    1   X      disable |
#  |_____________________________|
#
#  PWM frequency should be 1-60 kHz.
#  Smaller frequency == higher speed.
#
#  Reference: http://www.elechouse.com/elechouse/index.php?main_page=product_info&cPath=100_146&products_id=2179

from pyb import Pin, Timer

# Driver class. Implements half of the board - either A or B.
class Driver:

    # static variable to keep track of which timer channels are in use
    __channel_in_use__ = [ 0, 0, 0, 0]
    
    # static dictionary for the channel numbers
    __channel_dict__ = {
        'X9'  : 1,
        'B6'  : 1,
        'X10' : 2,
        'B7'  : 2,
        'Y3'  : 3,
        'B8'  : 3,
        'Y4'  : 4,
        'B9'  : 4
    }

    __timer__ = Timer(4)

    # private method that handles timer and pin initialization
    def __set_up_channel__(self, pin_name):
        # we'll return this for other functions to reference
        timer_channel = None
        if not Driver.__channel_in_use__[0]:
            # set the timer to run at 50kHz
            Driver.__timer__.init(freq=50000)
        if pin_name in Driver.__channel_dict__:
            chnum = Driver.__channel_dict__[pin_name]
            if not (Driver.__channel_in_use__[chnum-1]):
                # mark channel as used (array is zero-indexed, hence -1
                Driver.__channel_in_use__[chnum-1] = 1
                # initialize channel to PWM mode with zero duty cycle
                timer_channel = Driver.__timer__.channel(
                    chnum,
                    Timer.PWM,
                    pulse_width_percent=0,
                    pin=Pin(pin_name,Pin.ALT,af=2)
                )
            else:
                print ('Error, channel ',chnum,' is already in use!')
        else:
            print ('Error, ',pin_name,' is not a valid channel.')
        return timer_channel

    # create an instance. Channel is purely cosmetic, the actual
    # control depends on wiring
    def __init__(self, pin_name_left, pin_name_right, pin_name_en, pin_name_dis, channel='A'):
        self.name  = channel
        self.dis   = Pin(pin_name_dis, Pin.OUT_PP)
        # make sure motor starts out disabled	
        self.dis.high()
        self.en    = Pin(pin_name_en,  Pin.OUT_PP)
        # make sure motor starts out coasting
        self.en.low()
        self.speed = 0
        self.lchan = self.__set_up_channel__(pin_name_left)
        self.rchan = self.__set_up_channel__(pin_name_right)

    # get the cosmetic name of this instance
    def get_channel (self):
        return self.name

    # returns a tuple of the driver's various state data
    def get_status (self):
        return [
            'drive channel',   self.name,
            'output enabled',  self.en.value(),
            'output disabled', self.dis.value(),
            'speed setting',   self.speed
        ]

    # stop the motors with brake or coast
    def stop (self, brake=True):
        self.speed = 0
        self.lchan.pulse_width_percent(100)
        self.rchan.pulse_width_percent(100)
        self.en.value(brake)

    # enable the motors
    def enable (self):
        self.stop()
        self.dis.low()
        self.en.high()

    # disable the motors
    def disable (self):
        self.stop()
        self.dis.high()
        self.en.low()

    # set the driving speed (PWM %) of this driver
    def set_speed (self, speed):
        if speed < 0:
            if speed < -100:
                speed = -100
            self.speed = speed
            if not (self.lchan == None):
                # speed is negative here, so addition is subtraction
                self.lchan.pulse_width_percent(100+speed)
                self.rchan.pulse_width_percent(100)
            else:
                print ('Fake Channel speed set to ',speed)
        else:
            if speed > 100:
                speed = 100
            self.speed = speed
            if not (self.rchan == None):
                # smaller PWM duty cycles = faster speed
                self.lchan.pulse_width_percent(100)
                self.rchan.pulse_width_percent(100-speed)
            else:
                print ('Fake Channel speed set to ',speed)

