
import threading
from inputs import get_gamepad
import time
import time
import sys
import rti.connextdds as dds
from man_ctrl import man_ctrl
#import signal

def gamepad_manager():

    global cmdvelo 
    global cmdangle 
    global l_bumper 
    global r_bumper 
    global arm_cmd 
    global lt_val 
    global ud_dpad 
    global lr_dpad 
    global MAX_JOY_VAL
    global shutdown_threads 

    while not shutdown_threads:
        try:
            event1 = get_gamepad()
            if event1[0].code == 'ABS_Y':
                cmdvelo = event1[0].state/(MAX_JOY_VAL)
                if -15/100 <= cmdvelo and cmdvelo <= 15/100:            #deadzone
                    cmdvelo = 0
            if event1[0].code == 'ABS_RX':
                cmdangle = event1[0].state/(-MAX_JOY_VAL)
                if -15/100 <= cmdangle and cmdangle <= 15/100:           #deadzone
                    cmdangle = 0
                if cmdangle > 1.0:  # Dont want 1.08 or something like this
                    cmdangle = 1.0

            ## Commands for payload arm actuation
            if event1[0].code == "ABS_Z":
                lt_val = event1[0].state 

            if event1[0].code == "ABS_RZ":
                rt_val = event1[0].state 

            if event1[0].code == "ABS_HAT0Y":
                ud_dpad = event1[0].state     
        
            if event1[0].code == "ABS_HAT0X":
                lr_dpad = event1[0].state
            
            ## Commands to signal Autonomous enable. Autonous enable not implemented yet 
            if event1[0].code == 'BTN_TR':
                r_bumper = event1[0].state
                print("Right bumper action")

            if event1[0].code == 'BTN_TL':
                l_bumper = event1[0].state
                print("Left bumper action")


        except Exception as e:
            """sets all values to default and posts error"""
            print(f"Gamepad Error: {e}")
            cmdvelo = 0
            cmdangle = 0
            l_bumper = 0
            r_bumper = 0
            arm_cmd = False
            lt_val = 0
            ud_dpad = 0
            lr_dpad = 0

            time.sleep(.01) #wait before rechecking if gamepad is plugged in

        #time.sleep(.002) #this sleep keeps the thread from running constantly, add time to reduce load on cpu cause there is no real parallel processing in python



class man_ctrlPublisher:

    
    @staticmethod
    def run_publisher(domain_id: int, sample_count: int):
        # A DomainParticipant allows an application to begin communicating in
        # a DDS domain. Typically there is one DomainParticipant per application.
        # DomainParticipant QoS is configured in USER_QOS_PROFILES.xml
        participant = dds.DomainParticipant(domain_id)

        # A Topic has a name and a datatype.
        topic = dds.Topic(participant, "man_ctrl", man_ctrl)

        # This DataWriter will write data on Topic "Example man_ctrl"
        # DataWriter QoS is configured in USER_QOS_PROFILES.xml
        writer = dds.DataWriter(participant.implicit_publisher, topic)
        ugv_manual = man_ctrl()

        
        global shutdown_threads

        gamepad_manager_thread = threading.Thread(target=gamepad_manager,args=(cmdvelo,cmdangle,l_bumper,r_bumper,arm_cmd,lt_val,ud_dpad,lr_dpad,MAX_JOY_VAL))
        gamepad_manager_thread.start()


        while True:
            try:
                #main loop
                if lt_val > 1000 and rt_val < 1000: # If the left trigger is pressed, send payload arm commands 
                    arm_cmd = True
                    ugv_manual.arm_cmd[0] += ud_dpad*2 
                    if ugv_manual.arm_cmd[0] < -100:
                        ugv_manual.arm_cmd[0] = -100
                    elif ugv_manual.arm_cmd[0] > 10:
                        ugv_manual.arm_cmd[0] = 10
                    print(f"Up/Down Dpad: {ud_dpad}, L/R Dpad: {lr_dpad}")
                elif rt_val > 1000 and lt_val < 1000: # If the right trigger is pressed, send payload arm commands
                    arm_cmd = True
                    ugv_manual.arm_cmd[1] += ud_dpad*2 
                    if ugv_manual.arm_cmd[1] < 0:
                        ugv_manual.arm_cmd[1] = 0
                    elif ugv_manual.arm_cmd[1] > 100:
                        ugv_manual.arm_cmd[1] = 100
                    print(f"Up/Down Dpad: {ud_dpad}, L/R Dpad: {lr_dpad}")

                else:             #If left trigger is not pressed, send arm commands
                    ugv_manual.linear_vel = cmdvelo
                    ugv_manual.steer_cmd = cmdangle
                    print(f"Linear Velocity: {ugv_manual.linear_vel}, Steering Angle: {ugv_manual.steer_cmd}")
                            

                writer.write(ugv_manual)
                time.sleep(.2) # delay between writes

            except KeyboardInterrupt:
                print("Loop interrupted by user")
                break

            except Exception as e:
                print(f"main error: {e}")

        shutdown_threads = True
        gamepad_manager_thread.join()         
        print("Preparing to shut down...")

        

    




if __name__ == "__main__":
    
    """initiallizes all values related to the 
    gamepad manager and starts the thread"""
    MAX_JOY_VAL = 2**15 # max input of 32,768
    cmdvelo = 0
    cmdangle = 0
    l_bumper = 0
    r_bumper = 0
    arm_cmd = False
    lt_val = 0
    rt_val = 0
    ud_dpad = 0
    lr_dpad = 0

    shutdown_threads = False
    
    man_ctrlPublisher.run_publisher(
            domain_id=0,
            sample_count=sys.maxsize)