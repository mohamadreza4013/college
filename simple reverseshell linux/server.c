#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <netinet/in.h>
#include <arpa/inet.h>
//my server first send command to the oldest client and goes for next client
#define BUFFER_SIZE 1024
#define MAX_CLIENTS 10
void process_chunk(const char* chunk, int chunk_length) {
    // Process the received chunk here
    printf(" %s ", chunk);
}

void receive_chunks(int client_socket) {
    char buffer[BUFFER_SIZE];
    memset(buffer, 0, BUFFER_SIZE);
    int is_end = 0; // Indicates whether the end of transmission has been received

    while (!is_end) {
        ssize_t bytes_received = recv(client_socket, buffer, BUFFER_SIZE, 0);
            if (bytes_received == 3 && strncmp(buffer, "END", 3) == 0) {
                is_end = 1;
                break;
            }
        if (bytes_received < 0) {
            perror("Error receiving data");
            exit(EXIT_FAILURE);
        } else if (bytes_received == 0) {
            break;  // Connection closed by client
        } else {
            process_chunk(buffer, bytes_received);
            memset(buffer, 0, BUFFER_SIZE);
            // Check if the end of transmission indicator is received
        
        }
    }
}
int main(int argc, char* argv[]) {
    if (argc != 2) {
        printf("Usage: %s <port>\n", argv[0]);
        return 1;
    }
    int port = atoi(argv[1]);
    int sockfd, client_socket;
    struct sockaddr_in server, client;
    socklen_t client_len;
    int newSocket;
	struct sockaddr_in newAddr;
pid_t childpid;
char client_ip[INET_ADDRSTRLEN];

    // Create socket
    sockfd = socket(AF_INET, SOCK_STREAM, 0);
    if (sockfd < 0) {
        perror("Socket creation failed");
        return 1;
    }

    // Set up server details
    server.sin_family = AF_INET;
    server.sin_port = htons(port);
    server.sin_addr.s_addr = INADDR_ANY;

    // Bind the socket to the specified IP address and port
    if (bind(sockfd, (struct sockaddr*) &server, sizeof(server)) < 0) {
        perror("Binding failed");
        return 1;
    }

    // Listen for incoming connections
    if (listen(sockfd, MAX_CLIENTS) < 0) {
        perror("Listening failed");
        return 1;
    }

    printf("Server listening for incoming connections on port %d...\n", port);
while(1){
    client_len = sizeof(client);
    client_socket = accept(sockfd, (struct sockaddr*) &client, &client_len);
    if (client_socket < 0) {
        perror("Error accepting client connection");
        return 1;
    }
     if((childpid=fork())==0){
    
    while (1) {
        getpeername(client_socket, (struct sockaddr*)&client, &client_len);
    inet_ntop(AF_INET, &(client.sin_addr), client_ip, INET_ADDRSTRLEN);
        printf("Enter command to send to client with ip %s: ",client_ip);
        char command[BUFFER_SIZE];
        fgets(command, sizeof(command), stdin);

        // Remove newline character
        command[strcspn(command, "\n")] = '\0';

        // Send command to client
        int bytes_sent = send(client_socket, command, strlen(command), 0);
        if (bytes_sent < 0) {
            perror("Error sending command to client");
            break;
        }

        if (strcmp(command, "exit") == 0) {
            break;
        }
        getpeername(client_socket, (struct sockaddr*)&client, &client_len);
 inet_ntop(AF_INET, &(client.sin_addr), client_ip, INET_ADDRSTRLEN);
        
       
        // Receive output from client
       receive_chunks( client_socket);
          
    printf("<=client outputwith %s ip\n",client_ip);
    }
    }
    }
    close(client_socket);
     close(sockfd);
    return 0;
}
