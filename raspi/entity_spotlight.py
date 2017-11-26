## entity_spotlight.py ##
## Implements a "spotlight beam" on screen ##

from entity import *
from graphics import Transparent_Circle, Cross

SPEED = 1 # used by simulated lights, >1 will vibrate

class Entity_Spotlight(Entity):
  def __init__(self, x=0, y=0):
    Entity.__init__(self, x=x, y=y)
    self.home   = Point(x,y)
    self.target = Point(x,y)
    self.icon = Transparent_Circle(x=x, y=y, r=100)
    self.targ = Cross(x=x, y=y, r=20)

  # tells the spotlight to return to the original position
  def go_home (self):
    self.target = self.home

  # returns the home position of this light
  def get_home (self):
    return self.home

  # saves the spotlight's current position as 'home'
  def set_home (self):
    self.home = self.pos

  # sets the target position
  def set_target (self, point):
    self.target = point

  def get_target (self):
    return self.target

  # draw the spotlight beam on screen
#  def render (self):
    # TODO: put pygame rendering code here
#    pass

  # overrides the teleport_to in Entity
  def teleport_to (self, point):
#    print ("sent to ",point.get_x())
    self.pos.move_to(point.get_x(), point.get_y())

  # overrides the teleport_to in Entity
  def teleport_to (self, point):
#    print ("sent to",point.get_x())
    self.pos.move_to(point.get_x(), point.get_y())

  # updates the spotlight's beam on screen
  def update (self, delta_t):
    # put serial reading code here

    # move towards the target
    # TODO: remove this simulation in favor of actual feedback
    self_x = self.pos.get_x()
    self_y = self.pos.get_y()
    targ_x = self.target.get_x()
    targ_y = self.target.get_y()

    if self_x < targ_x:
      self_x += SPEED
    elif self_x > targ_x:
      self_x -= SPEED

    if self_y < targ_y:
      self_y += SPEED
    elif self_y > targ_y:
      self_y -= SPEED

    self.pos.move_to (self_x, self_y)
    self.icon.move_to(self_x, self_y)

  def draw (self, display):
    self.icon.move_to(self.pos.get_x(), self.pos.get_y())
    self.targ.move_to(self.target.get_x(), self.target.get_y())
    self.icon.draw(display)
    self.targ.draw(display)
