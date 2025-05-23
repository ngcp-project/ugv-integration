import ast
import sys
import threading
import time
import rti.connextdds as dds
from datetime import datetime

sys.path.insert(1, "../")
# sys.path.append('/Users/olenamolla/Desktop/NGCP/gcs-infrastructure')
from Communication.XBee.XBee import XBee
from Communication.XBee.Frames.x81 import x81
from Logger.Logger import Logger

sys.path.insert(1, "../../")
from ugv import man_ctrl, auto_ctrl

# Constants
TAG_COMMAND = 0x01
TAG_TELEMETRY = 0x02
TAG_ACK = 0x03

COMMANDS = {
    5: "MANUAL_CONTROL",
}

#Vehicle Setup
VEHICLE_NAME = "MRA"  # Change this to the current vehicle: "MRA", "MEA", or "ERU"
GCS_MAC = "0013A20042435A3D"  # MAC of the GCS XBee

logger = Logger(log_to_console = False)
vehicle_xbee = XBee(port="/dev/ttyUSB0", baudrate=115200, logger=logger)  # !!! set correct port !!!
vehicle_xbee.open()

#To receive commands
def listen_for_commands():
    domain_id = 0
    sample_count=sys.maxsize
    last_sent_time = time.time()

    SCALE_FACTOR = -32700
    MAX_JOY_VAL = 2**15 # max input of 32,768
    LOWER_ELBOW_SERV_LIM = -360.0
    UPPER_ELBOW_SERV_LIM = 360.0 
    DEAD_ZONE_THRESH = 15/100
    UPPER_STEER_CMD_LIMIT = 1.0 
    INC_DEC_VAL = 5

    cmd_vel = 0
    cmd_steer = 0
    l_bumper = 0
    r_bumper = 0
    lt_val = 0
    rt_val = 0
    ud_dpad = 0
    lr_dpad = 0
    a_btn = 0
    b_btn = 0
    x_btn = 0
    y_btn = 0

    # A DomainParticipant allows an application to begin communicating in
    # a DDS domain. Typically there is one DomainParticipant per application.
    # DomainParticipant QoS is configured in USER_QOS_PROFILES.xml
    participant = dds.DomainParticipant(domain_id)

    # Create manual control topic 
    man_topic = dds.Topic(participant, "man_ctrl", man_ctrl)

    # Create autonomous control topic 
    auto_topic = dds.Topic(participant, "auto_ctrl", auto_ctrl)

    # Create Autonomous and Manual Control DataWriters"
    # DataWriter QoS is configured in USER_QOS_PROFILES.xml
    man_writer = dds.DataWriter(participant.implicit_publisher, man_topic)
    auto_writer = dds.DataWriter(participant.implicit_publisher, auto_topic)

    ## Instantiate auto_ctrl and man_ctrl objects
    man_obj = man_ctrl()   
    auto_obj = auto_ctrl()    
    
    while True:
        frame: x81 = vehicle_xbee.retrieve_data()
        if frame:
            payload = frame.data.encode() if isinstance(frame.data, str) else frame.data
            tag = payload[0]
            cmd = payload.decode()[1]
            body = payload.decode()[2:]

            if tag == TAG_COMMAND:
                try:
                    cmd_id = int(cmd)
                    cmd_name = COMMANDS.get(cmd_id, "UNKNOWN_COMMAND")
                    print(f"Received Command: [{cmd_id}] {cmd_name}")
                            
                    ack_msg = chr(TAG_ACK) + str(cmd_id)
                    vehicle_xbee.transmit_data(ack_msg, address=GCS_MAC)
                    print(f"Sent ACK for command [{cmd_id}] {cmd_name}")
                    
                    body = ast.literal_eval(body)
                    print(body)

                    event1 = body
                
                    if event1['code'] == "ABS_Y":
                        cmd_vel = event1['state']/(MAX_JOY_VAL)
                        if -DEAD_ZONE_THRESH <= cmd_vel and cmd_vel <= DEAD_ZONE_THRESH:
                            cmd_vel = 0
                    if event1['code'] == "ABS_RX":
                        cmd_steer = event1['state']/(-MAX_JOY_VAL)
                        if -DEAD_ZONE_THRESH <= cmd_steer and cmd_steer <= DEAD_ZONE_THRESH:
                            cmd_steer = 0
                        if cmd_steer > UPPER_STEER_CMD_LIMIT: 
                            cmd_steer = UPPER_STEER_CMD_LIMIT
                    
                    ## Commands for payload arm actuation
                    if event1['code'] == "ABS_Z":
                        lt_val = event1['state'] 

                    if event1['code'] == "ABS_RZ":
                        rt_val = event1['state'] 

                    if event1['code'] == "ABS_HAT0Y":
                        ud_dpad = event1['state']     
                
                    if event1['code'] == "ABS_HAT0X":
                        lr_dpad = event1['state']
                    
                    ## Commands to signal Autonomous enable. Autonous enable not implemented yet 
                    if event1['code'] == 'BTN_TR':
                        r_bumper = event1['state']
                        print("Right bumper action")

                    if event1['code'] == 'BTN_TL':
                        l_bumper = event1['state']
                        print("Left bumper action")

                    if event1['code'] == "BTN_SOUTH":  # A button is pressed 
                        a_btn = event1['state']
                    
                    if event1['code'] == "BTN_EAST":  # B button is pressed 
                        b_btn = event1['state']

                    if event1['code'] == "BTN_NORTH":  # X button is pressed 
                        x_btn = event1['state']
                
                    if event1['code'] == "BTN_WEST":  # Y button is pressed 
                        y_btn = event1['state']
                    
                    ## Need to latch the autonomous mode enable to one state 
                    if l_bumper == 1 and r_bumper == 1 and a_btn == 1: # Enable Autonomous 
                        man_obj.auto_en = not man_obj.auto_en # Toggle Autonomous Boolean
                        auto_obj.auto_en = not auto_obj.auto_en # Toggle Autonomous Boolean
                        
                    if man_obj.auto_en == True:
                        print("Autonomous Mode Enabled")
                        man_writer.write(man_obj) #Publish man_obj data values 
                        auto_writer.write(auto_obj) # Publish Autonomous data values 
                    else:
                        if lt_val > 1000 and rt_val < 1000: # If the left trigger is pressed, send payload arm commands 
                            #arm_cmd = True
                            man_obj.arm_cmd[1] += ud_dpad*INC_DEC_VAL # Increment arm_cmd[1]
                            if man_obj.arm_cmd[1] < LOWER_ELBOW_SERV_LIM:
                                man_obj.arm_cmd[1] = LOWER_ELBOW_SERV_LIM 
                            elif man_obj.arm_cmd[1] > UPPER_ELBOW_SERV_LIM:
                                man_obj.arm_cmd[1] = UPPER_ELBOW_SERV_LIM
                            man_obj.arm_cmd[0] += lr_dpad*INC_DEC_VAL 
                            if man_obj.arm_cmd[0] < -360.0:
                                man_obj.arm_cmd[0] = -360.0
                            elif man_obj.arm_cmd[0] > 360.0:
                                man_obj.arm_cmd[0] = 360.0
                            print(f"Up/Down Dpad: {ud_dpad}, L/R Dpad: {lr_dpad}")

                            if a_btn == 1 or b_btn == 1:
                                man_obj.arm_cmd[2] += a_btn*INC_DEC_VAL #Increment arm_cmd[2] 
                                man_obj.arm_cmd[2] -= b_btn*INC_DEC_VAL #Decrement arm_cmd[2]
                            if x_btn == 1 or y_btn == 1:
                                man_obj.arm_cmd[3] += x_btn*INC_DEC_VAL #Increment arm_cmd[3]
                                man_obj.arm_cmd[3] -= y_btn*INC_DEC_VAL #Decrement arm_cmd[3]

                        elif rt_val > 1000 and lt_val < 1000: # If the right trigger is pressed, send payload arm commands
                            print("The right trigger is enabled")
                            man_obj.arm_cmd[4] += a_btn*INC_DEC_VAL
                            man_obj.arm_cmd[4] -= b_btn*INC_DEC_VAL
                            
                        else:
                            man_obj.linear_vel = cmd_vel
                            man_obj.steer_cmd = cmd_steer
                            print(f"Linear Velocity: {man_obj.linear_vel}, Steering Angle: {man_obj.steer_cmd}")
                    
                    man_writer.write(man_obj) #Publish man_obj data values 

                    last_sent_time = time.time()
                    
                except ValueError:
                    print(f"Failed to decode command ID from body: '{body}'")
        else:
            curr_time = time.time()
            if(curr_time - last_sent_time >= 1 and man_obj.auto_en == False):
                print("No Input Detected: Stopping")
                
                stop_man_obj = man_ctrl()
                man_writer.write(stop_man_obj)

        time.sleep(0.00005)



def main():
    # thread = threading.Thread(target=listen_for_commands, daemon=True)
    # thread.start()

    print("Listening for manual control...")

    try:
        listen_for_commands()
    except KeyboardInterrupt:
        print("\nShutting down...")
        vehicle_xbee.close()

if __name__ == "__main__":
    main()
