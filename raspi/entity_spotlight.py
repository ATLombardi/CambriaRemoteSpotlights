## entity_spotlight.py ##
## Implements a "spotlight beam" on screen ##

import entity

class Entity_Spotlight(Entity):
  def __init__(self):
    Entity.__init__()
	self.home = Point()

  def __init__(self, x, y):
    Entity.__init(x,y)
    self.home = Point(x,y)

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
    if self.pos.x < self.target.x:
      self.pos.x += 1
    elif self.pos.x > self.target.x:
      self.pos.x -= 1
    if self.pos.y < self.target.y:
      self.pos.y += 1
    elif self.pos.y > self.target.y:
      self.pos.y -= 1
