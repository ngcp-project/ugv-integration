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
        
        self.gnss_sub = self.create_subscription(Vector3Stamped, "filter/euler", self.euler_callback, 10)

        self.host_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        host_add = "localhost"
        host_port = 22222
        self.host_sock.bind((host_add, host_port))

        self.client_add = "localhost"
        self.client_port = 44444

        self.goal_heading = 0.0

    def euler_callback(self, euler_msg):
        
        self.act_heading = euler_msg.vector.z #Get actual yaw from xsens
        self.heading_error = self.goal_heading - self.act_heading
        payload = f"{self.heading_error}".encode()

        self.host_sock.sendto(payload, (self.client_add, self.client_port)) 
        print(f"Error: {self.heading_error}, Act_Heading: {self.act_heading}")
        time.sleep(.010)

def main(args=None):
    rclpy.init(args=args)
    sensor_sub = Ugv_Xsens()
    rclpy.spin(sensor_sub)

    drive_publisher.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()