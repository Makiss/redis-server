import socket
import threading
from app.resp_parser import RESPParser

def handle_client(connection):
    """Handle communication with a single client"""
    parser = RESPParser()
    buffer = b""

    try:
        while True:
            data = connection.recv(1024)
            if not data:
                break

            buffer += data
            parsed_data, bytes_consumed = parser.parse(buffer)

            if parsed_data is None:
                continue

            buffer = buffer[bytes_consumed:]

            if isinstance(parsed_data, list) and len(parsed_data) > 0:
                command = parsed_data[0].upper() if isinstance(parsed_data[0], str) else parsed_data[0].decode('utf-8').upper()

                if command == "PING":
                    response = b"+PONG\r\n"
                elif command == "ECHO" and len(parsed_data) > 1:
                    arg = parsed_data[1]
                    if not isinstance(arg, bytes):
                        arg = str(arg).encode('utf-8')
                    response = f"${len(arg)}\r\n".encode('utf-8') + arg + b"\r\n"
                else:
                    response = b"-ERR unknown command\r\n"
                
                connection.sendall(response)
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
