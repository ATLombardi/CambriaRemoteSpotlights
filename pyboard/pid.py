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
    self.err_sum = 0
    self.err_win = 0
    self.act_old = 0

  # iterate on the control loop. This requires a setpoint goal,
  # an 'actual' reading from the targetted system, and the time
  # since the last iteration
  def run (self, setpoint, actual, delta_t):
    err = setpoint - actual

    # proportional action
    errp = err * self.P

    # integral action
    self.err_sum += (err * self.I) - (self.err_win * self.windup)

    # derivative action
    err_der = (self.act_old - actual) * self.D / delta_t
    self.err_old = err

    # evaluate total action
    act = errp + self.err_sum + err_der

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

  def set_saturation(self, neg, pos):
    self.sat_neg = neg
    self.sat_pos = pos
