import socket
import threading

# Server setup
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Allows reuse of port
server.bind(('localhost', 55556))  # Changed to 55556
server.listen()

clients = []
nicknames = []

# Broadcast message to all clients
def broadcast(message):
    for client in clients:
        client.send(message)

# Handle individual client
def handle_client(client):
    while True:
        try:
            # Receive and broadcast message
            message = client.recv(1024)
            broadcast(message)
        except:
            # Remove and close client on error (e.g., disconnect)
            index = clients.index(client)
            clients.remove(client)
            client.close()
            nickname = nicknames[index]
            broadcast(f'{nickname} left the chat!'.encode('utf-8'))
            nicknames.remove(nickname)
            break

# Accept connections
def receive():
    while True:
        client, address = server.accept()
        print(f"Connected with {str(address)}")

        # Request and store nickname with error handling
        try:
            client.send('NICK'.encode('utf-8'))
            nickname = client.recv(1024).decode('utf-8')
            nicknames.append(nickname)
            clients.append(client)

            # Print and broadcast nickname
            print(f'Nickname of the client is {nickname}!')
            broadcast(f'{nickname} joined the chat!'.encode('utf-8'))
            client.send('Connected to the server!'.encode('utf-8'))

            # Start handling thread for client
            thread = threading.Thread(target=handle_client, args=(client,))
            thread.start()
        except Exception as e:
            print(f"Error with client {address}: {e}")
            client.close()

print("Server is listening...")
receive()