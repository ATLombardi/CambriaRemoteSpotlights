## rsc_main.py ##
## the master file for the Remote Spotlight Controller code ##

from touch_tracker import *
from graphics import *
from entity_spotlight import *
from comms import *

import pygame
import sys

def main ():
  print ("Starting up...")

  print ("init serial...")
  try:
    ser_a = RS232('/dev/ttyUSB0',115200)
#    ser_b = RS232('/dev/ttyUSB1',115200)
  except:
    print ("Error when trying to connect to serial ports!")
<<<<<<< HEAD
=======
  print ("done.")

  print ("init touch...")
  # initialize touch tracking
  touch = Tracker ()
  spot_l = Entity_Spotlight (x=200, y=200)
  spot_r = Entity_Spotlight (x=600, y=200)

  spot_l.go_home()
  spot_r.go_home()
>>>>>>> 47ff271a97738205e85f66bb1a7ae9089d9f3ba4
  print ("done.")

  print ("init pygame...")
  # prepare the pygame window
  pygame.init()
  display_info = pygame.display.Info()
  window_w = display_info.current_w;
  window_h = display_info.current_h;
  print ("window is:",window_w,",",window_h)
  screen = pygame.display.set_mode( (0,0), pygame.NOFRAME)
  pygame.mouse.set_visible(False)
  pygame.display.set_caption('Spotlight Controls')
  bg = Background('/home/pi/Pictures/stage.jpg', (0,0) )
  pygame.display.flip()

#  pygame.event.post(pygame.event.Event(pygame.MOUSEBUTTONDOWN,pos=(0,0),button=1))
#  pygame.event.post(pygame.event.Event(pygame.MOUSEBUTTONUP,pos=(0,0),button=1))

  clock = pygame.time.Clock()
  print ("done.")

  # initialize touch tracking
  print ("init touch...")
  touch = Tracker ()
  spot_l = Entity_Spotlight (x=200, y=200)
  spot_r = Entity_Spotlight (x=600, y=200)

  spot_l.go_home()
  spot_r.go_home()
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

      # see if we got an update from the pyboards
      ser_a.update_inbox()
#      ser_b.update_inbox()

      # build a Point where the light says it is
      a_point = Point (
        ser_a.read_inbox(ser_a.CMD_SPA),
        ser_a.read_inbox(ser_a.CMD_SPB)
      )

#      b_point = Point (
#        ser_b.read_inbox(ser_b.CMD_SPA),
#        ser_b.read_inbox(ser_b.CMD_SPB)
#      )

      # if spotlight A is on the left
      if ser_a.get_side() == 'L':
        # get spotlight positions in relative, convert to abs coords
        spot_l.teleport_to(a_point.add(spot_l.get_home()))
#        spot_r.teleport_to(b_point.add(spot_r.get_home()))
      else:
        spot_r.teleport_to(a_point.add(spot_r.get_home()))
#        spot_l.teleport_to(b_point.add(spot_r.get_home()))

      # get current location of each light
      pos_l = spot_l.get_location()
      pos_r = spot_r.get_location()

<<<<<<< HEAD
      # find closest touch point to each light
      target_l = touch.find_closest(pos_l.get_x(), pos_l.get_y() )
      target_r = touch.find_closest(pos_r.get_x(), pos_r.get_y() )

      # set the spotlights to move towards the closest touch points
      spot_l.set_target(target_l)
      spot_r.set_target(target_r)

      # convert to relative coords
      target_l = target_l.subtract(spot_l.get_home())
      target_r = target_r.subtract(spot_r.get_home())

      if ser_a.get_side() == 'L':
        ser_a.send_command(target_l.get_x(), target_l.get_y())
#        ser_b.send_command(pos_r.get_x(), pos_r.get_y())
      else:
        ser_a.send_command(target_r.get_x(), target_r.get_y())
#        ser_b.send_command(pos_l.get_x(), pos_l.get_y())
=======
      target_l = touch.find_closest(pos_l.get_x(), pos_l.get_y() )
      target_r = touch.find_closest(pos_r.get_x(), pos_r.get_y() )

      target_l = target_l.subtract(spot_l.get_home())
      target_r = target_r.subtract(spot_r.get_home())

      ser_a.update_inbox()
#      ser_b.update_inbox()

      a_point = Point (
        ser_a.read_inbox(ser_a.CMD_SPA),
        ser_a.read_inbox(ser_a.CMD_SPB)
      )

#      b_point = Point (
#        ser_b.read_inbox(ser_b.CMD_SPA),
#        ser_b.read_inbox(ser_b.CMD_SPB)
#      )

      if ser_a.get_side() == 'L':
        spot_l.teleport_to(a_point.add(spot_l.get_home()))
#        spot_r.teleport_to(b_point.add(spot_r.get_home()))
        ser_a.send_command(target_l.get_x(), target_l.get_y())
#        ser_b.send_command(target_r.get_x(), target_r.get_y())
      else:
        spot_r.teleport_to(a_point.add(spot_r.get_home()))
#        spot_l.teleport_to(b_point.add(spot_l.get_home()))
        ser_a.send_command(target_r.get_x(), target_r.get_y())
#        ser_b.send_command(target_l.get_x(), target_l.get_y())
>>>>>>> 47ff271a97738205e85f66bb1a7ae9089d9f3ba4

      # actually do rendering
      screen.fill( (255,255,255) )
      bg.draw(screen)

      spot_l.draw(screen)
      spot_r.draw(screen)

      pygame.display.update()

      for event in pygame.event.get():
        if event.type == pygame.QUIT:
          should_stop = True
          exit_reason_number = 1
        elif event.type == pygame.KEYDOWN:
          should_stop = True
          exit_reason_number = 2

      clock.tick (240)

  # handle exits cleanly
  except KeyboardInterrupt:
    print ("Received keyboard interrupt! Stopping...")
  except Exception as e:
    print (e)
  finally:
    # turn off these events just in case
    touch.active(False)
    print ("Exit reason: ", exit_reason_number)
    # and finally, bail out
    exit (exit_reason_number)

if __name__ == "__main__":
  main()
