import socket
import threading

def handle_client(connection):
    """Handle communication with a single client"""
    try:
        while True:
            data = connection.recv(1024)
            if not data:
                break
            connection.sendall(b"+PONG\r\n")
    except Exception as e:
        print(f"Error handling client: {e}")
    finally:
        connection.close()

def main():
    print("Logs from your program will appear here!")

    server_socket = socket.create_server(("localhost", 6379), reuse_port=True)
    
    try:
        while True:
            connection, client_address = server_socket.accept()
            print(f"New connection from {client_address}")
            
            threading.Thread(
                target=handle_client,
                args=(connection,)
            ).start()
    except KeyboardInterrupt:
        print("Server shutting down")
    finally:
        server_socket.close()


if __name__ == "__main__":
    main()
