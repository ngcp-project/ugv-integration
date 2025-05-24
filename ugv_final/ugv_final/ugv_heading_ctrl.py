
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
import time 
import re 
import socket

PUB_XSENS_DATA = False

heading_error_client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
heading_error_server = ('localhost', 33333)

class loggerSubscriber:

    @staticmethod
    def process_data(reader):
        global PUB_XSENS_DATA
        # take_data() returns copies of all the data samples in the reader
        # and removes them. To also take the SampleInfo meta-data, use take().
        # To not remove the data from the reader, use read_data() or read().
        samples = reader.take_data()
        for sample in samples:
            if sample.auto_en == True:
                PUB_XSENS_DATA = True
            else:
                PUB_XSENS_DATA = False
    
        return len(samples)

    @staticmethod
    def run_subscriber(domain_id: int, sample_count: int):
        global PUB_XSENS_DATA
        heading_pattern = r"Yaw:\s*([-\d\.]+)"

        ## UDP Socket to receive data from Xsens Application 
        host_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        host_add = "localhost"
        host_port = 20200
        host_sock.bind((host_add, host_port))

        # A DomainParticipant allows an application to begin communicating in
        # a DDS domain. Typically there is one DomainParticipant per application.
        # DomainParticipant QoS is configured in USER_QOS_PROFILES.xml
        participant = dds.DomainParticipant(domain_id)

        # A Topic has a name and a datatype.
        man_topic = dds.Topic(participant, "man_ctrl", man_ctrl)
        auto_topic = dds.Topic(participant, "auto_ctrl", auto_ctrl)

        # This DataReader reads data on Topic "Example logger".
        # DataReader QoS is configured in USER_QOS_PROFILES.xml
        reader = dds.DataReader(participant.implicit_subscriber, man_topic)
        writer = dds.DataWriter(participant.implicit_publisher, auto_topic)
        # Initialize samples_read to zero
        samples_read = 0
        xsens_obj = auto_ctrl()

        # Associate a handler with the status condition. This will run when the
        # condition is triggered, in the context of the dispatch call (see below)
        # condition argument is not used
        def condition_handler(_):
            nonlocal samples_read
            nonlocal reader
            samples_read += loggerSubscriber.process_data(reader)

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
                if (PUB_XSENS_DATA == True): 
                    GOAL_HEADING = 0
                   # Receive Data from other Xsens Application 
                    xsens_data, client_address = host_sock.recvfrom(1024)
                    heading_match = re.search(heading_pattern, xsens_data.decode())
                    if heading_match:
                        actual_heading_str = heading_match.group(1)
                        actual_heading = float(actual_heading_str)
                        heading_error = GOAL_HEADING - actual_heading
                        print(heading_error)
                        #heading_error = heading_error/100
                        heading_error = round(heading_error, 3) #Three 3 places of precisions
                        print(heading_error)
                        heading_error_payload = f"{heading_error}".encode()
                        heading_error_client.sendto(heading_error_payload, heading_error_server)
                        xsens_obj.heading_error = float(heading_error)
                        writer.write(xsens_obj)
                        time.sleep(0.10)
                # Dispatch will call the handlers associated to the WaitSet conditions
                # when they activate
                    waitset.dispatch(dds.Duration(1))  # Wait up to 1s each time
                    print("Waiting for New manual Data")
                else:
                    print("(Xsens Pub): Autonomous Mode Not enabled")

                waitset.dispatch(dds.Duration(1))  # Wait up to 1s each time
            except KeyboardInterrupt:
                break

        print("preparing to shut down...")


if __name__ == "__main__":
    loggerSubscriber.run_subscriber(
            domain_id=0,
            sample_count=sys.maxsize)
