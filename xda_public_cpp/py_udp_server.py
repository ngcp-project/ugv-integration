import socket
import pdb

# Set up the UDP server
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Bind the server to an IP and port (localhost and port 12345 in this case)

#server_address = ('192.168.1.157', 12345)
server_address = ("127.0.0.1", 20200)
#server_address = ('localhost', 12345)
server_socket.bind(server_address)

#breakpoint()

print("UDP server is waiting for a message...")

# Wait for a message from the client
while True:
    data, client_address = server_socket.recvfrom(1024)  # Buffer size of 1024 bytes
    print(f"Received message: {data.decode()} from {client_address}")

    # #if data.decode() == "Hello World":
    # if len(data.decode()) != 0:
    #     print(f"Message: {data.decode()}")
    #     print("Sending acknowledgment back to the client.")
    #     server_socket.sendto(b"Message received!", client_address)
    #     #break  # Optionally, you can exit after receiving the message

# Close the server socket
server_socket.close()