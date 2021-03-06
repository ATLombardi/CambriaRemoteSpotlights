## pid.py ##
# A generic implementation of PID control
# Supports P,I,D, integral windup prevention, and result saturation

class Controller:

  # setu up a controller, optionally configuring gains and saturation
  def __init__ (self, P=0,I=0,D=0, W=0, bottom=-100,top=100):
    self.set_K_P(P)
    self.set_K_I(I)
    self.set_K_D(D)
    self.set_K_W(W)
    self.set_saturation(bottom,top)
    self.err_sum     = 0
    self.err_win     = 0
    self.err_old     = 0
    self.report      = 0
    self.err_avg_del = 0

  # iterate on the control loop. This requires a setpoint goal,
  # an 'actual' reading from the targetted system, and the time
  # since the last iteration
  def run (self, setpoint, sensor, delta_t):
    err = setpoint - sensor

    # proportional action
    errp = err * self.P

    # integral action
    self.err_sum += ( (err*self.I) - (self.err_win*self.windup) ) * delta_t

    # derivative action
    # avg += (in - avg)/k, k = 2^n, n = number of samples
    self.err_avg_del += ((err-self.err_old) - self.err_avg_del) /32
    err_der = self.err_avg_del * self.D / delta_t
    if (-1 < err_der < 1):
      err_der = 0

    # evaluate total action
    act = errp + self.err_sum + err_der

#    if (self.report == 0):
#      print('P:',errp,' I:',self.err_sum,' D:',err_der,' t:',delta_t,' e:',err,' eo:',self.err_old)
#      self.report = 10
#    else:
#      self.report -= 1

    self.err_old = err
    self.err_win = act # storing this temporarily

    # saturation limits
    if act < self.sat_neg:
      act = self.sat_neg
    elif act > self.sat_pos:
      act = self.sat_pos

    self.err_win -= act # now it's correct
    return act

  # assign or update the proportional gain
  def set_K_P (self, value):
    self.P = value

  # assign or update the integral gain
  def set_K_I (self, value):
    self.I = value

  # assign or update the derivative gain
  def set_K_D (self, value):
    self.D = value

  # assign or update the integral windup prevention factor
  def set_K_W (self, value):
    self.windup = value

  # assign or update the clamping limits on the output
  def set_saturation(self, neg, pos):
    self.sat_neg = neg
    self.sat_pos = pos

# get the proportional gain
  def get_K_P (self):
    return self.P

  # get the integral gain
  def get_K_I (self):
    return self.I

  # get the derivative gain
  def get_K_D (self):
    return self.D

  # get the integral windup prevention factor
  def get_K_W (self):
    return self.windup

  # get the clamping limits on the output
  def get_saturation(self):
    return (self.sat_neg,self.sat_pos)
