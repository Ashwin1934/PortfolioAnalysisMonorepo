#include <iostream>
#include <winsock2.h>
#include <ws2tcpip.h>

// Link with the Ws2_32.lib library
#pragma comment(lib, "ws2_32.lib")

// compile with g++ -o udp_server.exe udp_server.cpp -lws2_32
// run executable with .\executable_name.exe
int main() {
    // Initialize Winsock
    WSADATA wsaData;
    int result = WSAStartup(MAKEWORD(2, 2), &wsaData);
    if (result != 0) {
        std::cerr << "WSAStartup failed with error: " << result << std::endl;
        return 1;
    }

    // Create a UDP socket
    SOCKET sockfd = socket(AF_INET, SOCK_DGRAM, 0);
    if (sockfd == INVALID_SOCKET) {
        std::cerr << "Socket creation failed with error: " << WSAGetLastError() << std::endl;
        WSACleanup();
        return 1;
    }

    // Set up the server address structure
    sockaddr_in servaddr;
    ZeroMemory(&servaddr, sizeof(servaddr));
    servaddr.sin_family = AF_INET;            // IPv4
    servaddr.sin_addr.s_addr = inet_addr("127.0.0.1"); // Listen on localhost
    servaddr.sin_port = htons(5005);           // Port number

    // Bind the socket to the IP and port
    if (bind(sockfd, reinterpret_cast<sockaddr*>(&servaddr), sizeof(servaddr)) == SOCKET_ERROR) {
        std::cerr << "Bind failed with error: " << WSAGetLastError() << std::endl;
        closesocket(sockfd);
        WSACleanup();
        return 1;
    }

    std::cout << "UDP server up and listening on 127.0.0.1:5005" << std::endl;

    // Main loop to receive data
    while (true) {
        char buffer[1024];
        sockaddr_in cliaddr;
        int cliaddrLen = sizeof(cliaddr);

        // Receive a message from the client
        int n = recvfrom(sockfd, buffer, sizeof(buffer) - 1, 0, reinterpret_cast<sockaddr*>(&cliaddr), &cliaddrLen);
        if (n == SOCKET_ERROR) {
            std::cerr << "recvfrom failed with error: " << WSAGetLastError() << std::endl;
            continue;
        }
        buffer[n] = '\0'; // Null-terminate the received data

        // Print the received message along with the sender's address and port
        std::cout << "Received message: " << buffer
                  << " from " << inet_ntoa(cliaddr.sin_addr)
                  << ":" << ntohs(cliaddr.sin_port) << std::endl;
    }

    // Cleanup (unreachable in this infinite loop)
    closesocket(sockfd);
    WSACleanup();
    return 0;
}
