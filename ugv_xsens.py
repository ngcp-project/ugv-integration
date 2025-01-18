#1/usr/bin/env python3 
import rclpy 
from rclpy.node import Node 
from sensor_msgs.msg import Joy  # Important for manual control  
from sensor_msgs.msg import NavSatFix # lat & long info

from geometry_msgs.msg import Twist
from geometry_msgs.msg import Vector3Stamped # For Euler angles (Heading Info)
import socket
import time 

class Ugv_Xsens(Node):
    
    def __init__(self):
        super().__init__("Ugv_Xsens")
        
        self.heading_sub = self.create_subscription(Vector3Stamped, "filter/euler", self.euler_callback, 10)
        self.gps = self.create_subscription(Vector3Stamped, "filter/positionlla", self.gps_callback, 10)

        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # Server address (localhost and port 22222)
        self.server_address = ('localhost', 22222)

        self.goal_heading = 0.0
        self.linear_vel = -0.70  # Set a constant velocity for autonomy
        self.steer_val = 0 # Does not matter what value is, Just need it send that data order in udp payload is maintained
        self.euler_data_lock = 0

    def gps_callback(self, gps_msg):
        gps_data = f"Lat:{gps_msg.vector.x}, Lon:{gps_msg.vector.y}"
        self.client_socket.sendto(gps_data.encode(), self.server_address)
        print(gps_data)
        
        # Some sort of delay just to make sure GPS callback sends data first 
        if self.euler_data_lock <= 50:
            self.euler_data_lock += 1

    def euler_callback(self, euler_msg):
        if self.euler_data_lock >= 50:
            yaw = euler_msg.vector.z 
            yaw_str = f"Yaw: {yaw}"
            self.client_socket.sendto(yaw_str.encode(), self.server_address)
            print(yaw_str)

        

    # def euler_callback(self, euler_msg):
        
    #     self.act_heading = euler_msg.vector.z #Get actual yaw from xsens
    #     self.heading_error = self.goal_heading - self.act_heading
    #     self.heading_error = self.heading_error/100  #Scale down to a value that the nucelo can accept 
    #     udp_payload = f"{self.linear_vel}, {self.steer_val}, {self.heading_error}".encode()
    #     self.server_socket.sendto(udp_payload, (self.client_ip, self.client_port))
    #     #self.host_sock.sendto(payload, (self.client_add, self.client_port)) 
    #     print(f"Act_Heading: {self.act_heading}, Error: {self.heading_error}, Lin Vel: {self.linear_vel}")
    #     time.sleep(.010)

def main(args=None):
    rclpy.init(args=args)
    sensor_sub = Ugv_Xsens()
    rclpy.spin(sensor_sub)

    drive_publisher.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
