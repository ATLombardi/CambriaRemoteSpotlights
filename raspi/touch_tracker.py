## touch_tracker.py ##
## Handles the FT5406 touchscreen library setup and interpretation ##

debug = False

from geom import Point
from ft5406 import Touchscreen, TS_PRESS, TS_RELEASE, TS_MOVE

class Tracker:
  # list for storing location updates
  points = [ Point(-1,-1) for p in range(10) ]

  # returns the closest point to the supplied coords
  def find_closest (self, x, y, mins=(0,0), dist=100000, fail_point=None):
#    print ("searching around ",x,",",y)
#    print ('fail point is',fail_point.get_x(),',',fail_point.get_y())
    temp    = Point (x,y)
    result  = Point (x,y)
    succeed = False
    for p in self.points:
      latest = temp.dist2(p)
      if 0 < latest < dist and p.get_x() > mins[0] and p.get_y() > mins[1]:
        dist = latest
        result.move_to(p.get_x(), p.get_y())
        succeed = True
        if debug:
          print ("found: ",result.get_x(), ",", result.get_y())
    if not succeed and fail_point != None and fail_point.get_x()>0:
#      print ('search failed, going to',fail_point.get_x(),',',fail_point.get_y())
      result.move_to(fail_point.get_x(), fail_point.get_y())
    return result

  # called when a touch starts
  def __touch_down (self, touch):
    if debug:
      print ("pressed",touch.slot, ":", touch.x, ",", touch.y)
    # save the data from this touch point
    self.points[touch.slot].move_to(touch.x, touch.y)

  # called when a touch ends
  def __touch_lift (self, touch):
    if debug:
      print ("released",touch.slot, ":", touch.x, ",", touch.y)
    # we'll use negative coords to mark this point as invalid
    self.points[touch.slot].move_to(-1, -1)

  # called when a touch moves
  def __touch_move (self, touch):
    if debug:
      print ("moved",touch.slot, ":", touch.x, ",", touch.y)
    # update the coords of the point
    self.points[touch.slot].move_to(touch.x, touch.y)

  # what to do when an event happens
  def __touch_handler (self, event, touch):
    if event == TS_PRESS:
      self.__touch_down (touch)

    if event == TS_RELEASE:
      self.__touch_lift (touch)

    if event == TS_MOVE:
      self.__touch_move (touch)

  # set everything up with this
  def __init__ (self):
    self.ts = Touchscreen()

    for touch in self.ts.touches:
      touch.on_press   = self.__touch_handler
      touch.on_release = self.__touch_handler
      touch.on_move    = self.__touch_handler

  # enable or disable touch events
  def active (self, bool):
    if bool == True:
      self.ts.run()
    else:
      self.ts.stop()

# test code, only runs when this file run directly (IE, not imported)
if __name__ == '__main__':
  from sys import exit
  from time import sleep

  debug = True
  t = Tracker()
  t.active (True)

  c = 0

  try:
    while True:
      c += 1
      if c == 1000:
        c = 0
        print (".")
        sleep(1)
  except KeyboardInterrupt:
    print ("stopping!")
  finally:
    t.active (False)
    exit(1)
