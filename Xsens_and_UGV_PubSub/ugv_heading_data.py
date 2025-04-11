
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
# udp imports
import sys
import socket
import math 
import re
import time

import rti.connextdds as dds
from ugv_data import ugv_heading_data

class Xsens_dataPublisher:

    @staticmethod
    def run_publisher(domain_id: int, sample_count: int):

        # A DomainParticipant allows an application to begin communicating in
        # a DDS domain. Typically there is one DomainParticipant per application.
        # DomainParticipant QoS is configured in USER_QOS_PROFILES.xml
        participant = dds.DomainParticipant(domain_id = 1)

        # A Topic has a name and a datatype.
        topic = dds.Topic(participant, "ugv_heading_data", ugv_heading_data)
        # This DataWriter will write data on Topic "Example Xsens_data"
        # DataWriter QoS is configured in USER_QOS_PROFILES.xml
        writer = dds.DataWriter(participant.implicit_publisher, topic)


        # data from ugv_heading_data class        
        sample = ugv_heading_data()

        #udp implementation
        heading_pattern = r"Yaw:\s*([-\d\.]+)"

        host_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        host_add = "localhost"
        host_port = 20200
        host_sock.bind((host_add, host_port))

        ## UDP setup to Tx data to nucelo 
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # Bind the server to an IP and port (localhost and port 12345 in this case)
        # server_address = ('192.168.20.5', 12345)  # Replace with your server's IP
        # server_socket.bind(server_address)

        # Define the known client IP and port
        # drive_nucelo_ip = '192.168.20.21'
        # drive_nucelo_port = 8   

        linear_vel = -0.70  # Set a constant velocity for autonomy
        steer_val = 0 # Does not matter what value is, Just need it send that data order in udp payload is maintained

       
        #while True: 
        for count in range(sample_count):
            # Catch control-C interrupt
            
            
            # define goal heading of the Xsens
            goal_heading = 0  
            try:
                # Udp receive 
                xsens_data, client_address = host_sock.recvfrom(1024)
                #print(f"Received message: {xsens_data.decode()} from {client_address}")
                heading_match = re.search(heading_pattern, xsens_data.decode())
                if heading_match:
                    actual_heading_str = heading_match.group(1)
                    actual_heading = float(actual_heading_str)
                    heading_error = goal_heading - actual_heading
                    heading_error = heading_error/100
                    heading_error = round(heading_error, 3) #Three 3 places of precisions 
                    #udp_payload = f"{linear_vel}, {steer_val}, {heading_error}".encode()
                    #server_socket.sendto(udp_payload, (drive_nucelo_ip, drive_nucelo_port))
                    #self.host_sock.sendto(payload, (self.client_add, self.client_port)) 
                    #goal heading
                    #sample.goal_heading = goal_heading
                    sample.actual_heading = actual_heading
                    sample.heading_error = heading_error
                    
                    time.sleep(.010)
                    print(f"Goal Heading: {goal_heading}, Actual Heading: {actual_heading}, Error: {heading_error * 100}")
            
                    writer.write(sample)               
                else:
                    print("Could not find Yaw string")
        

                    # change time to determine how fast data is published
                    time.sleep(1)
            except KeyboardInterrupt:
                    break

        print("preparing to shut down...")


if __name__ == "__main__":
    Xsens_dataPublisher.run_publisher(
            domain_id=1,
            sample_count=sys.maxsize)

