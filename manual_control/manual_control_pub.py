
# (c) Copyright, Real-Time Innovations, 2022.  All rights reserved.
# RTI grants Licensee a license to use, modify, compile, and create derivative
# works of the software solely for use with RTI Connext DDS. Licensee may
# redistribute copies of the software provided that all such copies are subject
# to this license. The software is provided "as is", with no warranty of any
# type, including any warranty for fitness for any purpose. RTI is under no
# obligation to maintain or support the software. RTI shall not be liable for
# any incidental or consequential damages arising out of the use or inability
# to use the software.

import time
import sys
import rti.connextdds as dds
from man_ctrl import man_ctrl
from inputs import get_gamepad
import signal

SCALE_FACTOR = -32700
MAX_JOY_VAL = 2**15 # max input of 32,768

class ugvgroundvehiclePublisher:
    @staticmethod
    def run_publisher(domain_id: int, sample_count: int):
        # A DomainParticipant allows an application to begin communicating in
        # a DDS domain. Typically there is one DomainParticipant per application.
        # DomainParticipant QoS is configured in USER_QOS_PROFILES.xml
        participant = dds.DomainParticipant(domain_id)

        # A Topic has a name and a datatype.
        topic = dds.Topic(participant, "man_ctrl", man_ctrl)

        # This DataWriter will write data on Topic "Example ugvgroundvehicle"
        # DataWriter QoS is configured in USER_QOS_PROFILES.xml
        writer = dds.DataWriter(participant.implicit_publisher, topic)
        ugv_manual = man_ctrl()

        def timeout_handler(signum, frame):             #on alarm, writes velo and steering angle to publisher
            if lt_val > 1000 and rt_val < 1000: # If the left trigger is pressed, send payload arm commands 
                arm_cmd = True
                if ugv_manual.arm_cmd[0] >= -100 and ugv_manual.arm_cmd[0] <= 20:
                    ugv_manual.arm_cmd[0] += ud_dpad*2 
                print(f"Up/Down Dpad: {ud_dpad}, L/R Dpad: {lr_dpad}")
            elif rt_val > 1000 and lt_val < 1000: # If the right trigger is pressed, send payload arm commands
                arm_cmd = True
                if ugv_manual.arm_cmd[1] >= 0 and ugv_manual.arm_cmd[1] <= 20:
                    ugv_manual.arm_cmd[1] += ud_dpad*2 
                print(f"Up/Down Dpad: {ud_dpad}, L/R Dpad: {lr_dpad}")

            else:             #If left trigger is not pressed, send arm commands
                ugv_manual.linear_vel = cmdvelo
                ugv_manual.steer_cmd = cmdangle
                print(f"Linear Velocity: {ugv_manual.linear_vel}, Steering Angle: {ugv_manual.steer_cmd}")
                        
            writer.write(ugv_manual)
            signal.setitimer(signal.ITIMER_REAL, 0.02) # Decreased from 20ms to 2ms (Chris)
            #raise Exception                             #triggers exception in the try block

        cmdvelo = 0
        cmdangle = 0
        l_bumper = 0
        r_bumper = 0
        arm_cmd = False
        lt_val = 0
        rt_val = 0
        ud_dpad = 0
        lr_dpad = 0

        signal.signal(signal.SIGALRM, timeout_handler)  #Routes alarm to timeout handler
        signal.setitimer(signal.ITIMER_REAL, 0.02)      #timer delay in seconds, float

        for count in range(sample_count):
        # Start of new code
            try:
                event1 = get_gamepad()              #reads gamepad value, hangs when no inputs
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
            except KeyboardInterrupt:
                break
        print("Preparing to shut down...")


if __name__ == "__main__":
    ugvgroundvehiclePublisher.run_publisher(
            domain_id=0,
            sample_count=sys.maxsize)


