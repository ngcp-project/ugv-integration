
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
from ugv import auto_ctrl
import socket
import re

# Create Socket for Xsens 
xsens_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Another udp server and client to receive Xsens Data 
xsens_client_address = ("localhost", 20200)
xsens_socket.bind(xsens_client_address)

float_regex = r"[-+]?\d*\.\d+|\d+"


class XsensClass:

    @staticmethod
    def run_publisher(domain_id: int, sample_count: int):

        # A DomainParticipant allows an application to begin communicating in
        # a DDS domain. Typically there is one DomainParticipant per application.
        # DomainParticipant QoS is configured in USER_QOS_PROFILES.xml
        participant = dds.DomainParticipant(domain_id = 0)

        # A Topic has a name and a datatype.
        auto_topic = dds.Topic(participant, "auto_ctrl", auto_ctrl)

        # This DataWriter will write data on Topic "Example logger"
        # DataWriter QoS is configured in USER_QOS_PROFILES.xml
        auto_writer = dds.DataWriter(participant.implicit_publisher, auto_topic)
        auto_obj = auto_ctrl()      
        goal_heading = 0  

        for count in range(sample_count):
            # Catch control-C interrupt
            try:
                xsens_payload, client_address = xsens_socket.recvfrom(100)
                xsens_payload = xsens_payload.decode()
                data_vals = re.findall(float_regex, xsens_payload)
                data_vals = [float(data) for data in data_vals] 
                actual_heading = data_vals[0]
                heading_error = (goal_heading - actual_heading)
                heading_error = round(heading_error, 2)
                print(heading_error)

                auto_obj.heading_error = heading_error

                # Modify the data to be sent here
                
                print(f"Writing logger, count {count}")
                auto_writer.write(auto_obj)
                #time.sleep(1)
            except KeyboardInterrupt:
                break

        print("preparing to shut down...")


if __name__ == "__main__":
    XsensClass.run_publisher(
            domain_id=0,
            sample_count=sys.maxsize)
