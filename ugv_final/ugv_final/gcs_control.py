
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
# import rti.connextdds as dds
# from ugv import man_ctrl
# from ugv import auto_ctrl
from inputs import get_gamepad
import signal 

SCALE_FACTOR = -32700
MAX_JOY_VAL = 2**15 # max input of 32,768
LOWER_ELBOW_SERV_LIM = -360.0
UPPER_ELBOW_SERV_LIM = 360.0 
DEAD_ZONE_THRESH = 15/100
UPPER_STEER_CMD_LIMIT = 1.0 

auto_en = False
linear_vel = 0.0
steer_val = 0.0
arm_cmd = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]  # Ten wide arm commands 

cmd_vel = 0
cmd_steer = 0
l_bumper = 0
r_bumper = 0
lt_val = 0
rt_val = 0
ud_dpad = 0
lr_dpad = 0
a_btn = 0


def timeout_handler(signum, frame):
    global auto_en
    global linear_vel
    global arm_cmd
    global l_bumper
    global r_bumper
    global lt_val
    global rt_val
    global ud_dpad

    ## Need to lat
    # ch the autonomous mode enable to one state 
    if l_bumper == 1 and r_bumper == 1: # Enable Autonomous 
            auto_en = not auto_en
            print(f"Autonomous Enable: {auto_en}")
            # man_obj.auto_en = not man_obj.auto_en # Toggle Autonomous Boolean
            # auto_obj.auto_en = not auto_obj.auto_en # Toggle Autonomous Boolean
    if auto_en == True:
        print("Autonomous Mode Enabled")
        signal.setitimer(signal.ITIMER_REAL, 0.02)
    else:
        if lt_val > 1000 and rt_val < 1000: # If the left trigger is pressed, send payload arm commands  
            arm_cmd[1] += ud_dpad*2 # Increment arm_cmd[1] by 2 
            if arm_cmd[1] < LOWER_ELBOW_SERV_LIM:
                arm_cmd[1] = LOWER_ELBOW_SERV_LIM 
            elif arm_cmd[1] > UPPER_ELBOW_SERV_LIM:
                arm_cmd[1] = UPPER_ELBOW_SERV_LIM
        elif rt_val > 1000 and lt_val < 1000: # If the right trigger is pressed, send payload arm commands
            arm_cmd[0] += ud_dpad*2 
            if arm_cmd[0] < -360.0:
                arm_cmd[0] = -360.0
            elif arm_cmd[0] > 360.0:
                arm_cmd[0] = 360.0
            print(f"Up/Down Dpad: {ud_dpad}, L/R Dpad: {lr_dpad}")
        else:
            linear_vel = cmd_vel
            steer_cmd = cmd_steer
            print(f"Linear Velocity: {linear_vel}, Steering Angle: {steer_cmd}")
        
        # man_writer.write(man_obj) #Publish man_obj data values 
        signal.setitimer(signal.ITIMER_REAL, 0.02)

def main():
    signal.signal(signal.SIGALRM, timeout_handler)  #Routes alarm to timeout handler
    signal.setitimer(signal.ITIMER_REAL, 0.02)      #timer delay in seconds, float
    global cmd_vel
    global cmd_steer
    global rt_val
    global lt_val
    global ud_dpad
    global lr_dpad
    
    while(1):
        try:
            # Modify the data to be sent here
            event1 = get_gamepad()
            if event1[0].code == "ABS_Y":
                cmd_vel = event1[0].state/(MAX_JOY_VAL)
                if -DEAD_ZONE_THRESH <= cmd_vel and cmd_vel <= DEAD_ZONE_THRESH:
                    cmd_vel = 0
            if event1[0].code == "ABS_RX":
                cmd_steer = event1[0].state/(-MAX_JOY_VAL)
                if -DEAD_ZONE_THRESH <= cmd_steer and cmd_steer <= DEAD_ZONE_THRESH:
                    cmd_steer = 0
                if cmd_steer > UPPER_STEER_CMD_LIMIT: 
                    cmd_steer = UPPER_STEER_CMD_LIMIT
            
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

            # if l_bumper == 1 and r_bumper == 1:
            #     if event1[0].code == "BTN_SOUTH"
                    

        except KeyboardInterrupt:
            break

    print("preparing to shut down...")
    

if __name__ == "__main__":
    main()
    

