## geom.py ##
## provides helper classes and functions related to geometic calculations ##

class Point:
  # create a Point at (x,y)
  def __init__(self, x=0, y=0):
    self.x = x
    self.y = y

  # returns the square of distance for speed
  def dist2 (self, other):
    delx = other.x - self.x
    dely = other.y - self.y
    return (delx**2 + dely**2)

  # returns actual distance for accuracy
  def dist (self, other):
    return dist(other)**0.5

  # returns the sum of two point vectors as a Point
  def add (self, other):
    xs = self.x + other.x
    ys = self.y + other.y
    return Point(xs,ys)

  # returns the difference between two point vectors as a Point
  def subtract (self, other):
    xs = self.x - other.x
    ys = self.y - other.y
    return Point(xs,ys)

  # sets the Point's new location instantly
  def move_to (self, x, y):
    self.x = x
    self.y = y

  # alternate version that accepts a tuple/array
  def move_to_array (self, coord):
    self.x = coord[0]
    self.y = coord[1]

  # returns the x-coordinate
  def get_x (self):
    return self.x

  # returns the y-coordinate
  def get_y (self):
    return self.y
