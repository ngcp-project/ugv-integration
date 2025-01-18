
#  Copyright (c) 2003-2024 Movella Technologies B.V. or subsidiaries worldwide.
#  All rights reserved.
#  
#  Redistribution and use in source and binary forms, with or without modification,
#  are permitted provided that the following conditions are met:
#  
#  1.	Redistributions of source code must retain the above copyright notice,
#  	this list of conditions, and the following disclaimer.
#  
#  2.	Redistributions in binary form must reproduce the above copyright notice,
#  	this list of conditions, and the following disclaimer in the documentation
#  	and/or other materials provided with the distribution.
#  
#  3.	Neither the names of the copyright holders nor the names of their contributors
#  	may be used to endorse or promote products derived from this software without
#  	specific prior written permission.
#  
#  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY
#  EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
#  MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL
#  THE COPYRIGHT HOLDERS OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
#  SPECIAL, EXEMPLARY OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT 
#  OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
#  HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY OR
#  TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
#  SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.THE LAWS OF THE NETHERLANDS 
#  SHALL BE EXCLUSIVELY APPLICABLE AND ANY DISPUTES SHALL BE FINALLY SETTLED UNDER THE RULES 
#  OF ARBITRATION OF THE INTERNATIONAL CHAMBER OF COMMERCE IN THE HAGUE BY ONE OR MORE 
#  ARBITRATORS APPOINTED IN ACCORDANCE WITH SAID RULES.
#  

import sys
import xsensdeviceapi as xda
from threading import Lock
import socket

# ## UDP setup to Tx data to nucelo 
# server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# # Bind the server to an IP and port (localhost and port 12345 in this case)
# server_address = ('192.168.20.5', 12345)  # Replace with your server's IP
# server_socket.bind(server_address)

# # Define the known client IP and port
# client_ip = '192.168.20.21'
# client_port = 8   

# goal_heading = 0.0
# linear_vel = -0.70  # Set a constant velocity for autonomy
# steer_val = 0 # Does not matter what value is, Just need it send that data order in udp payload is maintained
# heading_lock = 0



class XdaCallback(xda.XsCallback):
    def __init__(self, max_buffer_size = 5):
        xda.XsCallback.__init__(self)
        self.m_maxNumberOfPacketsInBuffer = max_buffer_size
        self.m_packetBuffer = list()
        self.m_lock = Lock()
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # Server address (localhost and port 22222)
        self.server_address = ('localhost', 22222)

    def packetAvailable(self):
        self.m_lock.acquire()
        res = len(self.m_packetBuffer) > 0
        self.m_lock.release()
        return res

    def getNextPacket(self):
        self.m_lock.acquire()
        assert(len(self.m_packetBuffer) > 0)
        oldest_packet = xda.XsDataPacket(self.m_packetBuffer.pop(0))
        self.m_lock.release()
        return oldest_packet

    def onLiveDataAvailable(self, dev, packet):
        self.m_lock.acquire()
        assert(packet != 0)
        while len(self.m_packetBuffer) >= self.m_maxNumberOfPacketsInBuffer:
            self.m_packetBuffer.pop()
        self.m_packetBuffer.append(xda.XsDataPacket(packet))
        self.m_lock.release()


if __name__ == '__main__':
    print("Creating XsControl object...")
    control = xda.XsControl_construct()
    assert(control != 0)

    xdaVersion = xda.XsVersion()
    xda.xdaVersion(xdaVersion)
    print("Using XDA version %s" % xdaVersion.toXsString())

    try:
        print("Scanning for devices...")
        portInfoArray =  xda.XsScanner_scanPorts()

        # Find an MTi device
        mtPort = xda.XsPortInfo()
        for i in range(portInfoArray.size()):
            if portInfoArray[i].deviceId().isMti() or portInfoArray[i].deviceId().isMtig():
                mtPort = portInfoArray[i]
                break

        if mtPort.empty():
            raise RuntimeError("No MTi device found. Aborting.")

        did = mtPort.deviceId()
        print("Found a device with:")
        print(" Device ID: %s" % did.toXsString())
        print(" Port name: %s" % mtPort.portName())

        print("Opening port...")
        if not control.openPort(mtPort.portName(), mtPort.baudrate()):
            raise RuntimeError("Could not open port. Aborting.")

        # Get the device object
        device = control.device(did)
        assert(device != 0)

        print("Device: %s, with ID: %s opened." % (device.productCode(), device.deviceId().toXsString()))

        # Create and attach callback handler to device
        callback = XdaCallback()
        device.addCallbackHandler(callback)

        # Put the device into configuration mode before configuring the device
        print("Putting device into configuration mode...")
        if not device.gotoConfig():
            raise RuntimeError("Could not put device into configuration mode. Aborting.")

        print("Configuring the device...")
        configArray = xda.XsOutputConfigurationArray()
        configArray.push_back(xda.XsOutputConfiguration(xda.XDI_PacketCounter, 0))
        configArray.push_back(xda.XsOutputConfiguration(xda.XDI_SampleTimeFine, 0))

        if device.deviceId().isImu():
            configArray.push_back(xda.XsOutputConfiguration(xda.XDI_Acceleration, 100))
            configArray.push_back(xda.XsOutputConfiguration(xda.XDI_RateOfTurn, 100))
            configArray.push_back(xda.XsOutputConfiguration(xda.XDI_MagneticField, 100))
        elif device.deviceId().isVru() or device.deviceId().isAhrs():
            configArray.push_back(xda.XsOutputConfiguration(xda.XDI_Quaternion, 100))
        elif device.deviceId().isGnss():
            configArray.push_back(xda.XsOutputConfiguration(xda.XDI_Quaternion, 100))
            configArray.push_back(xda.XsOutputConfiguration(xda.XDI_LatLon, 100))
            configArray.push_back(xda.XsOutputConfiguration(xda.XDI_AltitudeEllipsoid, 100))
            configArray.push_back(xda.XsOutputConfiguration(xda.XDI_VelocityXYZ, 100))
        else:
            raise RuntimeError("Unknown device while configuring. Aborting.")

        if not device.setOutputConfiguration(configArray):
            raise RuntimeError("Could not configure the device. Aborting.")

        print("Creating a log file...")
        logFileName = "logfile.mtb"
        if device.createLogFile(logFileName) != xda.XRV_OK:
            raise RuntimeError("Failed to create a log file. Aborting.")
        else:
            print("Created a log file: %s" % logFileName)

        print("Putting device into measurement mode...")
        if not device.gotoMeasurement():
            raise RuntimeError("Could not put device into measurement mode. Aborting.")

        print("Starting recording...")
        if not device.startRecording():
            raise RuntimeError("Failed to start recording. Aborting.")

        print("Main loop. Recording data for 10 seconds.")

        startTime = xda.XsTimeStamp_nowMs()
#        while xda.XsTimeStamp_nowMs() - startTime <= 10000:
        while True:
            if callback.packetAvailable():
                # Retrieve a packet
                packet = callback.getNextPacket()

                s = ""

                if packet.containsCalibratedData():
                    acc = packet.calibratedAcceleration()
                    s = "Acc X: %.2f" % acc[0] + ", Acc Y: %.2f" % acc[1] + ", Acc Z: %.2f" % acc[2]

                    gyr = packet.calibratedGyroscopeData()
                    s += " |Gyr X: %.2f" % gyr[0] + ", Gyr Y: %.2f" % gyr[1] + ", Gyr Z: %.2f" % gyr[2]

                    mag = packet.calibratedMagneticField()
                    s += " |Mag X: %.2f" % mag[0] + ", Mag Y: %.2f" % mag[1] + ", Mag Z: %.2f" % mag[2]

                if packet.containsOrientation():
                    quaternion = packet.orientationQuaternion()
                    s = "q0: %.2f" % quaternion[0] + ", q1: %.2f" % quaternion[1] + ", q2: %.2f" % quaternion[2] + ", q3: %.2f " % quaternion[3]

                    euler = packet.orientationEuler()
                    s += " |Roll: %.2f" % euler.x() + ", Pitch: %.2f" % euler.y() + ", Yaw: %.2f " % euler.z()

                if packet.containsLatitudeLongitude():
                    latlon = packet.latitudeLongitude()
                    s += " |Lat: %7.6f" % latlon[0] + ", Lon: %7.7f " % latlon[1]
                    print("Made it to LatLon")

                if packet.containsAltitude():
                    s += " |Alt: %7.2f " % packet.altitude()

                if packet.containsVelocity():
                    vel = packet.velocity(xda.XDI_CoordSysEnu)
                    s += " |E: %7.2f" % vel[0] + ", N: %7.2f" % vel[1] + ", U: %7.2f " % vel[2]
                
                callback.client_socket.sendto(s.encode(), callback.server_address)
                print("%s\r" % s, end="", flush=True)

        print("\nStopping recording...")
        if not device.stopRecording():
            raise RuntimeError("Failed to stop recording. Aborting.")

        print("Closing log file...")
        if not device.closeLogFile():
            raise RuntimeError("Failed to close log file. Aborting.")

        print("Removing callback handler...")
        device.removeCallbackHandler(callback)

        print("Closing port...")
        control.closePort(mtPort.portName())

        print("Closing XsControl object...")
        control.close()

    except RuntimeError as error:
        print(error)
        sys.exit(1)
    except:
        print("An unknown fatal error has occured. Aborting.")
        sys.exit(1)
    else:
        print("Successful exit.")
