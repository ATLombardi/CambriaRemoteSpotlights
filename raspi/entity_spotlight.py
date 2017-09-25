## entity_spotlight.py ##
## Implements a "spotlight beam" on screen ##

from entity import *
from graphics import Transparent_Circle

SPEED = 1 # used by simulated lights, >1 will vibrate

class Entity_Spotlight(Entity):
  def __init__(self, x=0, y=0):
    Entity.__init__(self, x=x, y=y)
    self.home = Point(x,y)
    self.icon = Transparent_Circle(x=x, y=y, r=100)

  # tells the spotlight to return to the original position
  def go_home (self):
    self.target = self.home

  # saves the spotlight's current position as 'home'
  def set_home (self):
    self.home = self.pos

  # draw the spotlight beam on screen
  def render (self):
    # TODO: put pygame rendering code here
    pass

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

    self.pos.inst_move_to (self_x, self_y)
    self.icon.move_to(self_x, self_y)

  def draw (self, display):
    self.icon.draw(display)
