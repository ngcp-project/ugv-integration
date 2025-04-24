import socket
import math 
import re
import time

heading_pattern = r"Yaw:\s*([-\d\.]+)"

host_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
host_add = "localhost"
host_port = 20200
host_sock.bind((host_add, host_port))

## UDP setup to Tx data to nucelo 
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Bind the server to an IP and port (localhost and port 12345 in this case)
server_address = ('192.168.20.5', 12345)  # Replace with your server's IP
server_socket.bind(server_address)

# Define the known client IP and port
drive_nucelo_ip = '192.168.20.21'
drive_nucelo_port = 8   

linear_vel = 0.20  # Set a constant velocity for autonomy
steer_val = 0 # Does not matter what value is, Just need it send that data order in udp payload is maintained


def main():

    # define goal heading of the Xsens
    goal_heading = 0  

    while True:
        # Udp receive 
        xsens_data, client_address = host_sock.recvfrom(1024)
        #print(f"Received message: {xsens_data.decode()} from {client_address}")
        heading_match = re.search(heading_pattern, xsens_data.decode())
        if heading_match:
            actual_heading_str = heading_match.group(1)
            actual_heading = float(actual_heading_str)
            heading_error = goal_heading - actual_heading
            print(heading_error)
            #heading_error = heading_error/100
            heading_error = round(heading_error, 3) #Three 3 places of precisions 
            udp_payload = f"{linear_vel}, {steer_val}, {heading_error}".encode()
            server_socket.sendto(udp_payload, (drive_nucelo_ip, drive_nucelo_port))
            #self.host_sock.sendto(payload, (self.client_add, self.client_port)) 
            time.sleep(.010)
            print(f"Goal Heading: {goal_heading}, Actual Heading: {actual_heading}, Error: {heading_error}")
        else:
            print("Could not find Yaw string")

if __name__ == "__main__":
    main()
