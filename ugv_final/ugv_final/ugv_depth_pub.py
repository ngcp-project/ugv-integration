
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
from ugv import man_ctrl
from ugv import auto_ctrl
import socket
import array

DISTANCE_THRESH = 10.0 #10 Ft distance threshold 

payload_string = ""
obstacle_flag = 0
auto_enable = 0

velocity_val = 0.5
steering_angle = 0
heading_error = 0.1

PUB_DEPTH_DATA = False  #Flag for depth camera measurements 

class auto_ctlSubscriber:

    @staticmethod
    def process_data(reader):
        # take_data() returns copies of all the data samples in the reader
        # and removes them. To also take the SampleInfo meta-data, use take().
        # To not remove the data from the reader, use read_data() or read().
        global PUB_DEPTH_DATA

        samples = reader.take_data()
        for sample in samples:
            if sample.auto_en == True:
                PUB_DEPTH_DATA = True 
            else:
                PUB_DEPTH_DATA = False
        return len(samples)

    @staticmethod
    def run_subscriber(domain_id: int, sample_count: int):
        global PUB_DEPTH_DATA
        """ temporary Socket Setup before RTI stuff is fleshed out """
        host_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        host_add = "localhost"
        host_port = 11111
        host_sock.bind((host_add, host_port))

        # A DomainParticipant allows an application to begin communicating in
        # a DDS domain. Typically there is one DomainParticipant per application.
        # DomainParticipant QoS is configured in USER_QOS_PROFILES.xml
        participant = dds.DomainParticipant(domain_id)

        # A Topic has a name and a datatype.
        man_topic = dds.Topic(participant, "man_ctrl", man_ctrl)

        auto_topic = dds.Topic(participant, "auto_ctrl", auto_ctrl)

        # DataReader QoS is configured in USER_QOS_PROFILES.xml
        reader = dds.DataReader(participant.implicit_subscriber, man_topic)

        writer = dds.DataWriter(participant.implicit_publisher, auto_topic)

        # Initialize samples_read to zero
        samples_read = 0
        AutoObj = auto_ctrl() 

        # Associate a handler with the status condition. This will run when the
        # condition is triggered, in the context of the dispatch call (see below)
        # condition argument is not used
        def condition_handler(_):
            nonlocal samples_read
            nonlocal reader
            samples_read += auto_ctlSubscriber.process_data(reader)

        # Obtain the DataReader's Status Condition
        status_condition = dds.StatusCondition(reader)

        # Enable the "data available" status and set the handler.
        status_condition.enabled_statuses = dds.StatusMask.DATA_AVAILABLE
        status_condition.set_handler(condition_handler)

        # Create a WaitSet and attach the StatusCondition
        waitset = dds.WaitSet()
        waitset += status_condition

       

        while samples_read < sample_count:
            # Catch control-C interrupt
            try:
                if (PUB_DEPTH_DATA == True):
                    data, addr = host_sock.recvfrom(1024)
                    payload = data.decode() # Convert Byte array to python string type 
                    print(payload)
                    payload = payload.split(",")  # Parse string using comma delimiter
                    resized_payload = payload[2:7] # Only take the middle 5 elements of the list [2, 7)
                    payload_float_list = [float(measure) for measure in resized_payload] # Convert string elements to float elements so that they can be used for comparison
                    
                    # If any value is below the distance threshold set obstacle_flag 
                    if any(measure <= DISTANCE_THRESH for measure in payload_float_list):
                        obstacle_flag = True
                    else:
                        obstacle_flag = False
                    
                    AutoObj.object_distance = array.array("f", payload_float_list)
                    AutoObj.obstacle_flag = obstacle_flag
                    print(AutoObj)
                    # Dispatch will call the handlers associated to the WaitSet conditions
                    # when they activate
                    writer.write(AutoObj)
                    print("Autonomous Enabled")
                else: 
                    print("Depth Camera App sleeping for 1 seconds...")

                waitset.dispatch(dds.Duration(1))  # Wait up to 1s each time
            except KeyboardInterrupt:
                break

        print("preparing to shut down...")


if __name__ == "__main__":
    auto_ctlSubscriber.run_subscriber(
            domain_id=0,
            sample_count=sys.maxsize)