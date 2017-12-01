import pyb

class Encoder:
  ''' This class creates an encoder counter that counts the position of a
  Pittman motor with an attached quadrature encoder. The code uses the
  pyboard (pyb) module for MicroPython to access the pins in one of the timer
  modules. '''

  def __init__(self, tim, pinA, pinB):
    '''  Initialize the encoder and both of its channels.
  
    @param tim The number of the timer module to be used.
    @param pinA The first input pin that the encoder is connected to.
    @param pinB The second input pin that the encoder is connected to. '''

    self.tim=tim
    self.tim.init(prescaler=0,period=65535)
    self.ch1 = self.tim.channel(1,pyb.Timer.ENC_A,pin=pinA)
    self.ch2 = self.tim.channel(2,pyb.Timer.ENC_B,pin=pinB)
    self.oldcount = 0 


  def Read(self):
    ''' This method reads the encoder. '''

    self.newcount = self.tim.counter()
    self.delta = self.newcount - self.oldcount
    self.delta &= 0xFFFF

    # Saturate to signed 16-bit int.
    if self.delta > 32767:
      self.delta -= 65535
    else:
      pass

    self.oldcount += self.delta
    return (self.oldcount)


  def Zero(self):
    ''' This method sets the encoder value to zero. '''
    return self.tim.counter(0)


  def Set(self, value):
    ''' This method sets the encoder value to an arbitrary number. '''
    return self.tim.counter(value)
