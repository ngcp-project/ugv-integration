import socket
import math 
import re
import time

lat_lon_pattern = r"Lat:\s*([-\d.]+),\s*Lon:\s*([-\d.]+)"
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

linear_vel = -0.80  # Set a constant velocity for autonomy
steer_val = 0 # Does not matter what value is, Just need it send that data order in udp payload is maintained

def gps_to_local(lat_current, lon_current, lat_goal, lon_goal):
    """
    Convert two nearby GPS coordinates (in degrees) into
    local (dx, dy) coordinates (in meters).

    Approximation:
      1 degree latitude ~ 111,111 meters
      1 degree longitude ~ 111,111 * cos(mean_lat)
    """ 

    # Convert degrees to radians
    lat_c_rad = math.radians(lat_current)
    lon_c_rad = math.radians(lon_current)
    lat_g_rad = math.radians(lat_goal)
    lon_g_rad = math.radians(lon_goal)
    
    # Mean latitude for better precision in longitude conversion
    mean_lat_rad = (lat_c_rad + lat_g_rad) / 2.0
    
    # Approximate meters per degree
    M_PER_DEG_LAT = 111_111
    m_per_deg_lon = 111_111 * math.cos(mean_lat_rad)
    
    # Compute differences in degrees
    # For dx > 0 to mean "west", invert the usual (lon_goal - lon_current)
    # by swapping them: (lon_current - lon_goal)
    delta_lon_deg = lon_goal - lon_current
    
    # For dy, we keep it standard: (lat_goal - lat_current)
    # so dy > 0 means goal is north of current position
    delta_lat_deg = lat_goal - lat_current
    
    # Convert differences to meters
    dx = delta_lon_deg * m_per_deg_lon  # East-West axis, now +ve is west
    dy = delta_lat_deg * M_PER_DEG_LAT  # North-South axis, +ve is north

    # (Optional) If you want the raw angle from standard math (0°=+x, 90°=+y),
    # you could do:
    angle_standard = math.degrees(math.atan2(dy, dx))

    # Adjust angle so that it works in robots frame 
    angle_standard -= 90
    
    ## Goal Heading 
    if  -269.0 <= angle_standard and angle_standard <= -178.0:
        angle_standard += 360
    return angle_standard

def main():
    # Example GPS coordinates (in degrees)
    #### Cal Poly Pomona Coordinates
    # Right Outside Engineering Building
   #lat_current = 34.058832
   #lon_current = -117.821626
    
    #lat_goal = 34.059346
    #lon_goal = -117.8210931
    #lat_goal = 34.059333
    #lon_goal = -117.8212890
    #lat_goal = 34.059356
    #lon_goal = -117.8213272
    #lat_goal = 34.059341
    #lon_goal = -117.8212127
    lat_goal =  34.059322
    lon_goal = -117.8211898
    heading_lock = 0

    while heading_lock == 0:
        # UDP Receive (Print output to make sure that you got gps)
        xsens_data, client_address = host_sock.recvfrom(1024)  # Buffer size of 1024 bytes
        print(f"Received message: {xsens_data.decode()} from {client_address}")
        match = re.search(lat_lon_pattern, xsens_data.decode())
        if match:
            lat_str = match.group(1)
            lon_str = match.group(2)
            
            # Convert strings to floats
            lat_current = float(lat_str)
            lon_current = float(lon_str)
            
            print(lat_current)
            print(lon_current)
            goal_heading = gps_to_local(lat_current, lon_current, lat_goal, lon_goal)
            heading_lock += 1

    
        else:
            print("Could not find Lat, Lon in the string.")
    
    print(f"Goal Lat: {lat_goal}, Goal Lon: {lon_goal}, Current Lat: {lat_current}, Current Lon: {lon_current}")
    
    while True:
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
            udp_payload = f"{linear_vel}, {steer_val}, {heading_error}".encode()
            server_socket.sendto(udp_payload, (drive_nucelo_ip, drive_nucelo_port))
            #self.host_sock.sendto(payload, (self.client_add, self.client_port)) 
            time.sleep(.010)
            print(f"Goal Heading: {goal_heading}, Actual Heading: {actual_heading}, Error: {heading_error * 100}")
        else:
            print("Could not find Yaw string")

if __name__ == "__main__":
    main()
