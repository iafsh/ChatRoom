import socket
import select

HEADER_LENGTH = 100
IP = "127.0.0.1"
PORT = 1235
# AF_INET == ipv4
# SOCK_STREAM == TCP
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

server_socket.bind((IP, PORT))
server_socket.listen()
sockets_list = [server_socket]
clients = {}


def recive(client_socket):
    try:
        message_header = client_socket.recv(HEADER_LENGTH)
        if not len(message_header):
            return False
        message_legth = int(message_header.decode("utf-8").strip())
        return {
            "header": message_header,
            "data": client_socket.recv(message_legth),
            "IsImage": client_socket.recv(1),
        }
    except Exception as e:
        return False


while True:
    read_sockets, _, exception_sockets = select.select(sockets_list, [], sockets_list)
    for notified_socket in read_sockets:
        # sb just connected to the server
        if notified_socket == server_socket:
            client_socket, client_address = server_socket.accept()
            user = recive(client_socket)
            if user is not False:
                sockets_list.append(client_socket)
                clients[client_socket] = user
                print(f"Accepted connection from {user['data'].decode('utf-8')}")
        else:
            message = recive(notified_socket)
            if message is False:
                print(
                    f"{clients[client_socket]['data'].decode('utf-8')} connection was lost"
                )
                sockets_list.remove(notified_socket)
                del clients[notified_socket]
                continue
            if message["IsImage"].decode("utf-8") == "1":
                print(f"recived image from {user['data'].decode('utf-8')}")
            else:
                print(
                    f"recived message from {user['data'].decode('utf-8')}:{message['data'].decode('utf-8')}"
                )
            user = clients[notified_socket]

            # sending msg to all other clients
            for client_socket in clients:
                if client_socket != notified_socket:
                    client_socket.send(
                        user["header"]
                        + user["data"]
                        + message["header"]
                        + message["data"]
                        + message["IsImage"]
                    )
    for notified_socket in exception_sockets:
        sockets_list.remove(notified_socket)
        clients.pop(notified_socket)
