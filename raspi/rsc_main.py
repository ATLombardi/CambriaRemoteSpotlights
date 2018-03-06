## rsc_main.py ##
## the master file for the Remote Spotlight Controller code ##

# local project stuff
from touch_tracker import *
from graphics import *
from entity_spotlight import *
from comms import *

import pygame                      # for rendering
from threading import Thread, Lock # for the serial comms monitor
from time import sleep             # for delaying threads

# this defines how tall the on-screen buttons are
BUTTON_HEIGHT = 50

mail_a_lock = Lock()
mail_b_lock = Lock()

# continually updates a serial inbox. Don't use in the main thread!
class MailboxMonitor:
  def __init__ (self, mailbox, lock):
    self.__running = True
    self.m = mailbox
    self.lock = lock

  def terminate (self):
    self.__running = False

  def run (self):
    while self.__running:
      # this is a blocking function, so we just run it without delays
      # being in its own thread has benefits
      try:
        with self.lock:
          if (self.m != None):
            self.m.update_inbox()
        sleep(0.0001) # I doubt this is accurate, but it doesn't matter
      except SerialException as se:
        print ('Serial error: ', se)
# /MailboxMonitor


# The main program that will be run on the Raspberry Pi
def main ():
  print ("Starting up...")

  print ("init serial...")
  ser_a = None
  ser_b = None
  try:
    ser_a = RS232('/dev/ttyUSB0',115200)
    ser_b = RS232('/dev/ttyUSB1',115200)
  except:
    print ("Error when trying to connect to serial ports. Are both connected?")

  print ("done.") # with serial setup

  print ("init touch...")
  # not much setup for mouse, and it does a lot of the same things
  # so we'll just slip this in here
  is_mouse_pressed = False
  mouse_point = Point (-1,-1)

  # initialize touch tracking
  touch = Tracker ()
  touch.add_external_point(mouse_point)

  spot_l = Entity_Spotlight (x=100, y=150)
  spot_r = Entity_Spotlight (x=700, y=150)

  is_tracking_l = True
  is_tracking_r = True

  # send the spotlights to their home position - which should be the above
  spot_l.go_home()
  spot_r.go_home()

  # declare these for later, default location is home
  target_l = spot_l.get_target()
  target_r = spot_r.get_target()

  # these handle updating serial data incoming
  a_monitor = MailboxMonitor(ser_a, mail_a_lock)
  b_monitor = MailboxMonitor(ser_b, mail_b_lock)

  # threads to wrap the monitors, lets them run parallel to the main loop
  a_monitor_thread = Thread(target=a_monitor.run)
  b_monitor_thread = Thread(target=b_monitor.run)

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
  screen = pygame.display.set_mode( (0,0), pygame.FULLSCREEN)
#  pygame.mouse.set_visible(False)
  pygame.display.set_caption('Spotlight Controls')
  bg = Background('/home/pi/Pictures/stage.jpg',
    (0,BUTTON_HEIGHT), scale=(window_w,window_h-BUTTON_HEIGHT)
  )
  # initial render pass to show the background image
  pygame.display.flip()

  # Build a couple of buttons: exit, left and right spotlight toggles, and go-to home for each.
  # The first coordinate describes the X-location, and since we want a little space between
  # buttons, we have do do some simple math here.
  button_width = (window_w / 5.0) - 2
  buttons = (
    Rectangle(window_w-button_width-1,0, button_width,BUTTON_HEIGHT, color=(200,  0,  0), text='Exit!'),
    Rectangle(                      1,0, button_width,BUTTON_HEIGHT, text='Track Left'),
    Rectangle(         button_width+3,0, button_width,BUTTON_HEIGHT, text='Track right'),
    Rectangle(       2*button_width+5,0, button_width,BUTTON_HEIGHT, color=( 60,140,240), text='Home Left'),
    Rectangle(       3*button_width+7,0, button_width,BUTTON_HEIGHT, color=( 60,140,240), text='Home Right')
  )

  clock = pygame.time.Clock()
  print ("done.") # with pygame/render stuff

  # easy way to stop cleanly from inside loop
  should_stop = False
  # something to report when we stop
  exit_reason_number = -1

  # inboxes will be updated in separate threads
  a_monitor_thread.start()
  b_monitor_thread.start()

  # turn on touch events now, we are ready
  touch.active (True)
  
  a_point = Point(0,0)
  b_point = Point(0,0)

  print ("Start-up done. Running...")
  try:
    while not should_stop:
      # build a Point where the light says it is
      if (not mail_a_lock.locked()):
        mail_a_lock.acquire()
        if not ser_a == None:
          a_point = Point (
            ser_a.read_inbox(ser_a.CMD_SPA),
            ser_a.read_inbox(ser_a.CMD_SPB)
          )
        else:
         a_point = Point(0,0)
        mail_a_lock.release()
#      print (a_point.get_x(), ',', a_point.get_y())

      if (not mail_b_lock.locked()):
        mail_b_lock.acquire()
        if not ser_b == None:
          b_point = Point (
            ser_b.read_inbox(ser_b.CMD_SPA),
            ser_b.read_inbox(ser_b.CMD_SPB)
          )
        else:
          b_point = Point(0,0)
        mail_b_lock.release()

      # if spotlight A is on the left
      if (not ser_a == None) and (ser_a.get_side() == 'L'):
        # get spotlight positions in relative, convert to abs coords
        spot_l.move_to(a_point.add(spot_l.get_home()))
        spot_r.move_to(b_point.add(spot_r.get_home()))
      else:
        spot_r.move_to(a_point.add(spot_r.get_home()))
        spot_l.move_to(b_point.add(spot_l.get_home()))

      # get current location of each light
      pos_l = spot_l.get_location()
      pos_r = spot_r.get_location()

      # if the mouse is being dragged, update the relevant Point
      if is_mouse_pressed:
        mouse_point.move_to_array(pygame.mouse.get_pos())

      # find closest touch point to each light
      if is_tracking_l:
        target_l = touch.find_closest(
          pos_l.get_x(),pos_l.get_y(),
          mins=(0,BUTTON_HEIGHT),
          fail_point=target_l
        )

      if is_tracking_r:
        target_r = touch.find_closest(
          pos_r.get_x(),pos_r.get_y(),
          mins=(0,BUTTON_HEIGHT),
          fail_point=target_r
        )

      # set the spotlights to move towards the targets
      spot_l.set_target(target_l)
      spot_r.set_target(target_r)

      # convert to relative coords
      rel_l = target_l.subtract(spot_l.get_home())
      rel_r = target_r.subtract(spot_r.get_home())

#      print ('t: ',target_r.get_x(), ',', target_r.get_y())

      # send the target values to the lights
      if not ser_a == None:
        if ser_a.get_side() == 'L':
          ser_a.send_command(rel_l.get_x(), rel_l.get_y())
        else:
          ser_a.send_command(rel_r.get_x(), rel_r.get_y())
  
      if not ser_b == None:
        if ser_b.get_side() == 'R':
          ser_b.send_command(rel_r.get_x(), rel_r.get_y())
        else:
          ser_b.send_command(rel_l.get_x(), rel_l.get_y())

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
                elif x == 1: # left enable toggle
                  is_tracking_l = not is_tracking_l
                elif x == 2: # right enable toggle
                  is_tracking_r = not is_tracking_r
                elif x == 3: # left home button
                  # disable tracking to make this easier on the user
                  is_tracking_l = False
                  target_l = spot_l.get_home()
                elif x == 4: # right home button
                  is_tracking_r = False
                  target_r = spot_r.get_home()
                break # we found and resolved a button, stop the For-loop
        elif event.type == pygame.MOUSEBUTTONUP:
          is_mouse_pressed = False

      clock.tick (60) # limit framerate

  # handle exits cleanly
  except KeyboardInterrupt:
    print ("Received keyboard interrupt! Stopping...")
  except Exception as e:
    print (e)
  finally:
    # turn off these events and release the threads
    touch.active(False)
    a_monitor.terminate()
    b_monitor.terminate()
    if not ser_a == None:
      ser_a.close()
    if not ser_b == None:
      ser_b.close()
    a_monitor_thread.join(timeout=5)
    b_monitor_thread.join(timeout=5)
    print ("Exit reason: ", exit_reason_number)
    # and finally, bail out
    exit (exit_reason_number)

# if we just run this file, we'll trigger this
if __name__ == "__main__":
  main()
