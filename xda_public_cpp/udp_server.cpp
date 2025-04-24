// Server side implementation of UDP client-server model 

#include <bits/stdc++.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <arpa/inet.h>
#include <netinet/in.h>



#define PORT    (20200)
#define MAXLINE (1030)

int main()
{
    int sockfd;
    char buffer[MAXLINE+1];
    const char *payload = "Hello From Server!";
    struct sockaddr_in server_addr, cli_addr;

    // Creating socket file descriptor 
    if ((sockfd = socket(AF_INET, SOCK_DGRAM, 0)) < 0)
    {
        perror("Socket Creating Failed");
        exit(EXIT_FAILURE);
    }

    memset(&server_addr, 0, sizeof(server_addr));
    memset(&cli_addr, 0, sizeof(cli_addr));

    //Filling Server Info 
    server_addr.sin_family = AF_INET; //IPv4
    server_addr.sin_addr.s_addr = inet_addr("127.0.0.1");;
    server_addr.sin_port = htons(PORT);

    //Bind the Socket with the server address 
    if ( bind(sockfd, (const struct sockaddr *)&server_addr, sizeof(server_addr)) < 0)
    {
        perror("bind failed");
        exit(EXIT_FAILURE);
    }

    socklen_t len;
    int n;

    len = sizeof(cli_addr); //Len is value/result 

    while(1)
    {
        n = recvfrom(sockfd, (char *)buffer, MAXLINE, 
            MSG_MORE, (struct sockaddr *)&cli_addr, &len);
        // usleep(10000);
        printf("Data %s\n", buffer);
        memset(buffer, 0, sizeof(buffer));
    }
    // buffer[n] = '\0';
    // printf("Client: %s\n", buffer);
    // sendto(sockfd, (const char *)payload, strlen(payload),
    //         MSG_CONFIRM, (const struct sockaddr *)&cli_addr, len);

    // std::cout << "Message sent." << std::endl;

    return 0;
}
