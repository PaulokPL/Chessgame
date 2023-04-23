import socket
import threading

HOST = '192.168.0.19'
PORT = 0

clients = []

def handle_client(client_socket, addr):
    print(f"[NEW CONNECTION] {addr} connected.")

    clients.append(client_socket)

    while True:
        try:
            message = client_socket.recv(1024).decode()
            for c in clients:
                if c != client_socket:
                    c.send(message.encode())
        except:
            remove_client(client_socket)
            break

def remove_client(client_socket):
    clients.remove(client_socket)
    print(f"[DISCONNECTED] {client_socket.getpeername()} disconnected.")

def start_server():
    print("[STARTING] Server is starting...")

    server_socket = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
    server_socket.bind((HOST, 0))
    server_socket.listen()

    print(server_socket.getsockname())
    print(f"[LISTENING] Server is listening on {HOST}:{PORT}")

    while True:
        client_socket, addr = server_socket.accept()

        client_thread = threading.Thread(target=handle_client, args=(client_socket, addr))
        client_thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")

if __name__ == '__main__':
    start_server()