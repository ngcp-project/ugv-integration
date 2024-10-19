## This program prints the output of an xbox controller to stdout

from inputs import get_gamepad

while 1:
    events = get_gamepad()
    for event in events:
  #      print(event.ev_type, event.code)
         print(event.state)
