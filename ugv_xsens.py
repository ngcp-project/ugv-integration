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

        # self.host_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # host_add = "localhost"
        # host_port = 22222
        # self.host_sock.bind((host_add, host_port))

        # self.client_add = "localhost"
        # self.client_port = 44444

        ## UDP setup to Tx data to nucelo 
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # Bind the server to an IP and port (localhost and port 12345 in this case)
        self.server_address = ('192.168.20.5', 12345)  # Replace with your server's IP
        self.server_socket.bind(self.server_address)

        # Define the known client IP and port
        self.client_ip = '192.168.20.21'
        self.client_port = 8   

        self.goal_heading = 0.0
        self.linear_vel = -0.70  # Set a constant velocity for autonomy
        self.steer_val = 0 # Does not matter what value is, Just need it send that data order in udp payload is maintained
    def euler_callback(self, euler_msg):
        
        self.act_heading = euler_msg.vector.z #Get actual yaw from xsens
        self.heading_error = self.goal_heading - self.act_heading
        self.heading_error = self.heading_error/100  #Scale down to a value that the nucalo can accept 
        udp_payload = f"{self.linear_vel}, {self.steer_val}, {self.heading_error}".encode()
        self.server_socket.sendto(udp_payload, (self.client_ip, self.client_port))
        #self.host_sock.sendto(payload, (self.client_add, self.client_port)) 
        print(f"Act_Heading: {self.act_heading}, Error: {self.heading_error}, Lin Vel: {self.linear_vel}")
        time.sleep(.010)

def main(args=None):
    rclpy.init(args=args)
    sensor_sub = Ugv_Xsens()
    rclpy.spin(sensor_sub)

    drive_publisher.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
