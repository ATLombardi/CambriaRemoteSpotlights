## rsc_main.py ##
## the master file for the Remote Spotlight Controller code ##

# local project stuff
from touch_tracker import *
from graphics import *
from entity_spotlight import *
from comms import *

import pygame                # for rendering
from threading import Thread # for the serial comms

# this defines how tall the on-screen buttons are
BUTTON_HEIGHT = 50

# continually updates a serial inbox. Don't use in the main thread!
class MailboxMonitor:
  def __init__ (self, mailbox):
    self.__running = True
    self.m = mailbox

  def terminate (self):
    self.__running = False

  def run (self):
    while self.__running:
      # this is a blocking function, so we just run it without delays
      # being in its own thread has benefits
      try:
        self.m.update_inbox()
      except SerialException as se:
        print ('Serial error: ', se)
# /MailboxMonitor


# The main program that will be run on the Raspberry Pi
def main ():
  print ("Starting up...")

  print ("init serial...")
  try:
    ser_a = RS232('/dev/ttyUSB0',115200)
#    ser_b = RS232('/dev/ttyUSB1',115200)
  except:
    print ("Error when trying to connect to serial ports!")

  print ("done.") # with serial setup

  print ("init touch...")
  # not much setup for mouse, and it does a lot of the same things
  # so we'll just slip this in here
  is_mouse_pressed = False
  mouse_point = Point (0,0)

  # initialize touch tracking
  touch = Tracker ()
  spot_l = Entity_Spotlight (x=200, y=200)
  spot_r = Entity_Spotlight (x=600, y=200)

  is_tracking_l = True
  is_tracking_r = True

  # send the spotlights to their home position - which should be the above
  spot_l.go_home()
  spot_r.go_home()

  # declare these for later, default location is home
  target_l = spot_l.get_target()
  target_r = spot_r.get_target()

  # these handle updating serial data incoming
  a_monitor = MailboxMonitor(ser_a)
#  b_monitor = MailboxMonitor(ser_b)

  # threads to wrap the monitors, lets them run parallel to the main loop
  a_monitor_thread = Thread(target=a_monitor.run)
#  b_monitor_thread = Thread(target=b_monitor.run)

  print ("done.") # with touch stuff

  print ("init pygame...")
  # prepare the pygame library
  pygame.init()
  # calculate window size - should be 800x480y
  display_info = pygame.display.Info()
  window_w = display_info.current_w;
  window_h = display_info.current_h;
  print ("window is:",window_w,",",window_h)
  # prepare the screen
  screen = pygame.display.set_mode( (0,0), pygame.NOFRAME)
#  pygame.mouse.set_visible(False)
  pygame.display.set_caption('Spotlight Controls')
  bg = Background('/home/pi/Pictures/stage.jpg',
    (0,BUTTON_HEIGHT), scale=(window_w,window_h-BUTTON_HEIGHT)
  )
  # initial render pass to show the background image
  pygame.display.flip()

  # build a couple of buttons: exit, and left and right spotlight toggles
  buttons = (
    Rectangle(window_w-199,0, 198,BUTTON_HEIGHT, text='Exit!', color=(200,0,0)),
    Rectangle(  1,0, 198,BUTTON_HEIGHT, text='Track Left'),
    Rectangle(201,0, 198,BUTTON_HEIGHT, text='Track right')
  )

#  clock = pygame.time.Clock()
  print ("done.") # with pygame/render stuff

  # easy way to stop cleanly from inside loop
  should_stop = False
  # something to report when we stop
  exit_reason_number = -1

  # inboxes will be updated in separate threads
  a_monitor_thread.start()
#  b_monitor_thread.start()

  # turn on touch events now, we are ready
  touch.active (True)

  print ("Start-up done. Running...")
  try:
    while not should_stop:
      # if the mouse is being dragged, update the relevant Point
      if is_mouse_pressed:
        mouse_point.move_to_array(pygame.mouse.get_pos())

      # build a Point where the light says it is
      a_point = Point (
        ser_a.read_inbox(ser_a.CMD_SPA),
        ser_a.read_inbox(ser_a.CMD_SPB)
      )
#      print (a_point.get_x(), ',', a_point.get_y())

#      b_point = Point (
#        ser_b.read_inbox(ser_b.CMD_SPA),
#        ser_b.read_inbox(ser_b.CMD_SPB)
#      )

      # if spotlight A is on the left
      if ser_a.get_side() == 'L':
        # get spotlight positions in relative, convert to abs coords
        spot_l.move_to(a_point.add(spot_l.get_home()))
#        spot_r.move_to(b_point.add(spot_r.get_home()))
      else:
        spot_r.move_to(a_point.add(spot_r.get_home()))
#        spot_l.move_to(b_point.add(spot_r.get_home()))

      # get current location of each light
      pos_l = spot_l.get_location()
      pos_r = spot_r.get_location()

      # find closest touch point to each light
      target_l = touch.find_closest(
        pos_l.get_x(),pos_l.get_y(),
        mins=(BUTTON_HEIGHT,0),
        fail_point=target_l
      )
      target_r = touch.find_closest(
        pos_r.get_x(),pos_r.get_y(),
        mins=(BUTTON_HEIGHT,0),
        fail_point=target_r
      )

      # set the spotlights to move towards the closest touch points
      spot_l.set_target(target_l)
      spot_r.set_target(target_r)

      # convert to relative coords
      rel_l = target_l.subtract(spot_l.get_home())
      rel_r = target_r.subtract(spot_r.get_home())

#      print ('t: ',target_r.get_x(), ',', target_r.get_y())

      # send the target values to the lights
      if ser_a.get_side() == 'L':
        ser_a.send_command(rel_l.get_x(), rel_l.get_y())
#        ser_b.send_command(rel_r.get_x(), rel_r.get_y())
      else:
        ser_a.send_command(rel_r.get_x(), rel_r.get_y())
#        ser_b.send_command(rel_l.get_x(), rel_l.get_y())

      # actually do rendering, starting with the background
#      screen.fill( (255,255,255) )
      bg.draw(screen)

      # set the buttons' color depending on their tracking toggle
      if is_tracking_l:
        buttons[1].set_color( (0,128,0) )
      else:
        buttons[1].set_color( (128,0,0) )

      if is_tracking_r:
        buttons[2].set_color( (0,128,0) )
      else:
        buttons[2].set_color( (128,0,0) )

      # draw the buttons
      for b in buttons:
        b.draw(screen)

      # next the lights
      spot_l.draw(screen)
      spot_r.draw(screen)

      # finish rendering
      pygame.display.update()

      # check for keyboard events and such
      for event in pygame.event.get():
        if event.type == pygame.QUIT:
          should_stop = True
          exit_reason_number = 1
        elif event.type == pygame.KEYDOWN:
          should_stop = True
          exit_reason_number = 2
        elif event.type == pygame.MOUSEBUTTONDOWN:
          # if we're clicking outside of bounds, check for buttons
          pos = pygame.mouse.get_pos()
          is_mouse_pressed = True
          if pos[1] <= BUTTON_HEIGHT:
            for x in range(0,len(buttons)):
              if buttons[x].contains(pos):
                is_mouse_pressed = False # don't track, we're outside bounds
                if x == 0: # exit button
                  should_stop = True
                  exit_reason_number = 3
                elif x == 1: # left button
                  is_tracking_l = not is_tracking_l
                elif x == 2: # right button
                  is_tracking_r = not is_tracking_r
        elif event.type == pygame.MOUSEBUTTONUP:
          is_mouse_pressed = False

#      clock.tick (240)

  # handle exits cleanly
  except KeyboardInterrupt:
    print ("Received keyboard interrupt! Stopping...")
  except Exception as e:
    print (e)
  finally:
    # turn off these events and release the threads
    touch.active(False)
    a_monitor.terminate()
#    b_monitor.terminate()
    ser_a.close()
#    ser_b.close()
    a_monitor_thread.join()
#    b_monitor_thread.join()
    print ("Exit reason: ", exit_reason_number)
    # and finally, bail out
    exit (exit_reason_number)

# if we just run this file, we'll trigger this
if __name__ == "__main__":
  main()
