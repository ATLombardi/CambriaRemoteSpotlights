## entity.py ##
## An object on the Raspberry Pi's screen ##
from geom import Point

class Entity:
  # create an entity at (x,y)
  def __init__ (self, x=0, y=0):
    self.pos    = Point(x, y)
    self.target = Point(x, y)

  # set the target for motion updates
  def set_target (self, point):
    self.target.move_to(point.get_x(), point.get_y())

  # set this entity to a location immediately
  def move_to (self, point):
    self.pos.move_to(point.get_x(), point.get_y())

  def get_location (self):
    return self.pos

  # allow the entity to move itself
  def update (self, delta_t):
    # child classes will override this
    pass
