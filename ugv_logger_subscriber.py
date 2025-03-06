
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
from Xsens_data import Xsens_data
from datetime import datetime
class Xsens_dataSubscriber:

    @staticmethod
    def process_data(reader):
        # take_data() returns copies of all the data samples in the reader
        # and removes them. To also take the SampleInfo meta-data, use take().
        # To not remove the data from the reader, use read_data() or read().
        samples = reader.take_data()
        
        #make logger for xsens
        filename = 'Xsens_logger.txt'
        for sample in samples:
            # create human readable time
            timestamp = time.time()
            readable_time = datetime.fromtimestamp(timestamp).strftime('%D, %H:%M:%S')
            
            data_string = ( 
                # MTi related data
                f"\n"
                f"Timestamp: {readable_time} \n"
                f"Acceleration Data: X: {sample.accel_x:.3f}, Y: {sample.accel_y:.3f} Z: {sample.accel_z:.3f} \n"
                f"Gyro Data: X: {sample.gyro_x:.3f}, Y: {sample.gyro_y:.3f}, Z {sample.gyro_z:.3f} \n"
                f"Orientation: Roll: {sample.roll:.3f}, Pitch: {sample.pitch:.3f} Yaw: {sample.yaw:.3f} \n"
                f"GPS: Longitude: {sample.longitude}, Latitude: {sample.latitude} \n"
                # add UGV data below
                )
            print(data_string)
       
        with open (filename, 'a') as f:
            f.write(data_string + '\n')
                    
            return len(samples)

    @staticmethod
    def run_subscriber(domain_id: int, sample_count: int):

        # A DomainParticipant allows an application to begin communicating in
        # a DDS domain. Typically there is one DomainParticipant per application.
        # DomainParticipant QoS is configured in USER_QOS_PROFILES.xml
        participant = dds.DomainParticipant(domain_id = 0)

        # A Topic has a name and a datatype.
        topic = dds.Topic(participant, "Xsens_data", Xsens_data)

        # This DataReader reads data on Topic "Example Xsens_data".
        # DataReader QoS is configured in USER_QOS_PROFILES.xml
        reader = dds.DataReader(participant.implicit_subscriber, topic)

        # Initialize samples_read to zero
        samples_read = 0

        # Associate a handler with the status condition. This will run when the
        # condition is triggered, in the context of the dispatch call (see below)
        # condition argument is not used
        def condition_handler(_):
            nonlocal samples_read
            nonlocal reader
            samples_read += Xsens_dataSubscriber.process_data(reader)

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
                # Dispatch will call the handlers associated to the WaitSet conditions
                waitset.dispatch(dds.Duration(1))  # Wait up to 1s each time
            except KeyboardInterrupt:
                break

        print("preparing to shut down...")


if __name__ == "__main__":
    Xsens_dataSubscriber.run_subscriber(
            domain_id=0,
            sample_count=sys.maxsize)
