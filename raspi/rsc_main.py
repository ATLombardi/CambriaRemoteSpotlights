## rsc_main.py ##
## the master file for the Remote Spotlight Controller code ##

import touch_tracker

def main ():
  # initialize touch tracking
  touch = Tracker ()
  spot_l = Entity_Spotlight (20, 0)
  spot_r = Entity_Spotlight (20,10)

  spot_l.go_home()
  spot_r.go_home()

  # easy way to stop cleanly from inside loop
  should_stop = False
  # something to report when we stop
  exit_reason_number = -1

  # turn on touch events now, we are ready
  touch.active (True)

  try:
    while not should_stop:
      delta = 0.1 # TODO: get an actual clock check here

      # set the spotlights to move towards the closest touch points
      spot_l.set_target(touch.find_closest(spot_l.x, spot_l.y ))
      spot_r.set_target(touch.find_closest(spot_r.x, spot_r.y ))

      # actually move the spotlights on-sceen
      spot_l.update(delta)
spot_r.update(delta)

  # handle exits cleanly
  except KeyboardInterrupt:
    print ("Received keyboard interrupt! Stopping...
  finally:
    # turn off these events just in case
    touch.active(False)
    if should_stop:
      # this is a clean exit
      exit_reason_number = 0
    # and finally, bail out
    exit (exit_reason_number)
