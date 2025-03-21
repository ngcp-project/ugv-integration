// UDP Client
#include <iostream>
#include <winsock2.h>
#include <ws2tcpip.h>
#include <string>

#pragma comment(lib, "ws2_32.lib")


int main() {
 WSADATA wsaData;
 if (WSAStartup(MAKEWORD(2, 2), &wsaData) != 0) {
 std::cerr << "WSAStartup failed." << std::endl;
 return 1;
 }

 SOCKET clientSocket = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP);
 if (clientSocket == INVALID_SOCKET) {
 std::cerr << "Socket creation failed." << std::endl;
 WSACleanup();
 return 1;
 }

 sockaddr_in serverAddr;
 serverAddr.sin_family = AF_INET;
 serverAddr.sin_port = htons(12345);
 inet_pton(AF_INET, "127.0.0.1", &serverAddr.sin_addr);

 std::string message;
 std::cout << "Enter message to send: ";
 std::getline(std::cin, message);

 int bytesSent = sendto(clientSocket, message.c_str(), message.length(), 0, (sockaddr*)&serverAddr, sizeof(serverAddr));
 if (bytesSent == SOCKET_ERROR) {
 std::cerr << "sendto failed." << std::endl;
 closesocket(clientSocket);
 WSACleanup();
 return 1;
 }

 char buffer[512];
 sockaddr_in serverResponseAddr;
 int serverResponseAddrLen = sizeof(serverResponseAddr);

 int bytesReceived = recvfrom(clientSocket, buffer, sizeof(buffer), 0, (sockaddr*)&serverResponseAddr, &serverResponseAddrLen);
 if (bytesReceived == SOCKET_ERROR) {
 std::cerr << "recvfrom failed." << std::endl;
 closesocket(clientSocket);
 WSACleanup();
 return 1;
 }

 buffer[bytesReceived] = '\0';
 std::cout << "Received from server: " << buffer << std::endl;

 closesocket(clientSocket);
 WSACleanup();
 return 0;
}