# threads test

import threading
from inputs import get_gamepad
import time


MAX_JOY_VAL = 2**15 # max input of 32,768
cmdangle = 0
cmdvelo = 0

def gamepad_read_and_store():
    global cmdangle
    global cmdvelo
    global shutdown

    while not shutdown:
        try:
            event1 = get_gamepad()              #reads gamepad value, hangs when no inputs


            if event1[0].code == 'ABS_Y':
                cmdvelo = event1[0].state
                
                
            if event1[0].code == 'ABS_RX':
                cmdangle = event1[0].state

        except Exception as e:
            print(f"gamepad crashed :( Error: {e}")
            #from inputs import get_gamepad


def monitor_gamepad():
    if gamepad_thread.is_alive():
        gamepad_thread.join(.1)   # how long it'll wait for the update
    else:
        raise Exception("Gamepad_crashed")
        

    
if __name__ == "__main__":
    gamepad_threads = []
    shutdown = False

    gamepad_thread = threading.Thread(target=gamepad_read_and_store)
    time.sleep(.5)

    gamepad_thread.start()

    while 1:
    # Start of new code
        try:
            monitor_gamepad()
            print(f"Linear Velocity: {cmdvelo}, Steering Angle: {cmdangle}")


        except KeyboardInterrupt:
            break
        except Exception as e:
            print(e)


    shutdown = True
    gamepad_thread.join()          
    print("Preparing to shut down...")













