## entity.py ##
## An object on the Raspberry Pi's screen ##
from geom import Point

class Entity:
  # create an entity at (0,0)
  def __init__ (self):
    self.pos    = Point()
    self.target = Point()

  # create an entity at (x,y)
  def __init__ (self, x, y):
    self.sim    = sim
    self.pos    = Point(x, y)
    self.target = Point(x, y)

  # set the target for motion updates
  def set_target (self, x, y):
    target.inst_move_to(x,y)

  def get_location (self):
    return self.pos

  # allow the entity to move itself
  def update (self, delta_t):
    # child classes will override this
	pass
