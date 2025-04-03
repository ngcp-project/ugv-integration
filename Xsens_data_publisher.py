
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
from datetime import datetime
from Xsens_data import Xsens_data
from Xsens_data import ugv_data

class Xsens_dataPublisher:

    @staticmethod
    def run_publisher(domain_id: int, sample_count: int):

        # A DomainParticipant allows an application to begin communicating in
        # a DDS domain. Typically there is one DomainParticipant per application.
        # DomainParticipant QoS is configured in USER_QOS_PROFILES.xml
        participant = dds.DomainParticipant(domain_id = 0)

        # A Topic has a name and a datatype.
        topic = dds.Topic(participant, "Xsens_data", Xsens_data)
        topic1 = dds.Topic(participant, "ugv_data", ugv_data)
        # This DataWriter will write data on Topic "Example Xsens_data"
        # DataWriter QoS is configured in USER_QOS_PROFILES.xml
        writer = dds.DataWriter(participant.implicit_publisher, topic)
        writer1 = dds.DataWriter(participant.implicit_publisher, topic1)


        # this would sample from xsens driver
        sample = Xsens_data()
        # data from ugv_data class        
        sample1 = ugv_data()
       
        #while True: 
        for count in range(sample_count):
            # Catch control-C interrupt
            
            # create human readable time
            timestamp = time.time()
            readable_time = datetime.fromtimestamp(timestamp).strftime('%H:%M:%S')
            try:

                    ''' PSEUDO DATA'''
                    sample.accel_x = 0.1 * count  # Simulate changing acceleration data
                    sample.accel_y = 0.2 * count
                    sample.accel_z = 9.8 + (0.1 * count)  # Simulate gravity-based value
                    sample.gyro_x = 0.05 * count  # Simulate gyro data
                    sample.gyro_y = 0.1 * count
                    sample.gyro_z = 0.2 * count
                    sample.roll = 5.0 + (0.1 * count)  # Simulate orientation data
                    sample.pitch = 10.0 + (0.2 * count)
                    sample.yaw = 15.0 + (0.3 * count)
                    sample.latitude = 37.7749 + (0.0001 * count)  # Simulate GPS data
                    sample.longitude = -122.4194 + (0.0001 * count)

                    '''UGV sample data'''
                    sample1.goal_heading= 15.01 + count
                    sample1.actual_heading = 16.01 + count
                    sample1.error_heading = 17.01 + count
                    
                    # Modify the data to be sent here
                    # replace example data with MTi data
                    print(f"Timestamp: {readable_time} \n",
                        f"Acceleration Data: X: {sample.accel_x:.3f}, Y: {sample.accel_y:.3f} Z: {sample.accel_z:.3f} \n",
                        f"Gyro Data: X: {sample.gyro_x:.3f}, Y: {sample.gyro_y:.3f}, Z {sample.gyro_z:.3f} \n",
                        f"Orientation: Roll: {sample.roll:.3f}, Pitch: {sample.pitch:.3f} Yaw: {sample.yaw:.3f} \n",
                        f"GPS: Longitude: {sample.longitude}, Latitude: {sample.latitude} \n"
                        #ugv data
                        f"Goal Heading: {sample1.goal_heading:.3f} \n"
                        f"Actual Heading: {sample1.actual_heading:.3f} \n"
                        f"Error Heading: {sample1.error_heading:.3f} \n"
                        )
                    writer1.write(sample1)
                    writer.write(sample)
                    # change time to determine how fast data is published
                    time.sleep(1)
            except KeyboardInterrupt:
                    break

        print("preparing to shut down...")


if __name__ == "__main__":
    Xsens_dataPublisher.run_publisher(
            domain_id=0,
            sample_count=sys.maxsize)

