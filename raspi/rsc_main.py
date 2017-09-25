## rsc_main.py ##
## the master file for the Remote Spotlight Controller code ##

from touch_tracker import *
from graphics import *
from entity_spotlight import *

import pygame

def main ():
  print ("Starting up...")

  print ("init touch...")
  # initialize touch tracking
  touch = Tracker ()
  spot_l = Entity_Spotlight (x=200, y=200)
  spot_r = Entity_Spotlight (x=600, y=200)

  spot_l.go_home()
  spot_r.go_home()
  print ("done.")

  print ("init pygame...")
  # prepare the pygame window
  pygame.init()

  screen = pygame.display.set_mode( (800,480) ) # , pygame.FULLSCREEN)
  pygame.display.set_caption('Spotlight Controls')
  bg = Background('/home/pi/Pictures/stage.jpg', (0,0) )
#  pygame.display.flip()

  clock = pygame.time.Clock()
  print ("done.")

  # easy way to stop cleanly from inside loop
  should_stop = False
  # something to report when we stop
  exit_reason_number = -1

  # turn on touch events now, we are ready
  touch.active (True)

  print ("Start-up done. Running...")
  try:
    while not should_stop:
      delta = 0.1 # TODO: get an actual clock check here

      # set the spotlights to move towards the closest touch points
      pos_l = spot_l.get_location()
      pos_r = spot_r.get_location()

      spot_l.set_target(touch.find_closest(pos_l.get_x(), pos_l.get_y() ))
      spot_r.set_target(touch.find_closest(pos_r.get_x(), pos_r.get_y() ))

      spot_l.update(delta)
      spot_r.update(delta)

      # actually do rendering
      screen.fill( (255,255,255) )
      bg.draw(screen)

      spot_l.draw(screen)
      spot_r.draw(screen)

      pygame.display.update()

      for event in pygame.event.get():
        if event.type == pygame.QUIT:
          should_stop = true
          exit_reason_number = 1
        elif event.type == pygame.KEYDOWN:
          should_stop = true
          exit_reason_number = 2

      clock.tick (60)

  # handle exits cleanly
  except KeyboardInterrupt:
    print ("Received keyboard interrupt! Stopping...")
  finally:
    # turn off these events just in case
    touch.active(False)
    print ("Exit reason: ", exit_reason_number)
    # and finally, bail out
    exit (exit_reason_number)

if __name__ == "__main__":
  main()
