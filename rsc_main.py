## rsc_main.py ##
## the master file for the Remote Spotlight Controller code ##

import touch_tracker

def main ():
  # initialize touch tracking
  touch = Tracker ()

  # do stuff
  pass

  # easy way to stop cleanly from inside loop
  should_stop = False
  # something to report when we stop
  exit_reason_number = -1

  # turn on touch events now, we are ready
  touch.active (True)

  try:
    while not should_stop:
      # render and stuff
      pass

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
