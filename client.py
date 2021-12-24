import socket
import errno
import sys

HEADER_LENGTH = 100
IP = "127.0.0.1"
PORT = 1235
ISIMAGE = "0".encode("utf-8")
my_username = input("Plaese enter your name ")
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((IP, PORT))
client_socket.setblocking(False)  # we wont block reciving we will handel it with errno

username = my_username.encode("utf-8")
username_header = f"{len(username):<{HEADER_LENGTH}}".encode("utf-8")
client_socket.send(username_header + username + ISIMAGE)
print("type '.' if you want to see all new messages")
print("type 'exit' if you want to exit")
print("type 'image' if you want to send an image")


def sendingimage():
    filename = input('plaese enter image name i.e "superman.jpg": ')
    ISIMAGE = "1".encode("utf-8")
    file = open(filename, "rb")
    image_data = file.read()
    image_header = f"{len(image_data):<{HEADER_LENGTH}}".encode("utf-8")
    client_socket.send(image_header + image_data + ISIMAGE)
    ISIMAGE = "0".encode("utf-8")
    file.close()


def saveimage(data):
    file = open("recived_image.jpg", "wb")
    file.write(data)
    file.close


while True:  # for sending
    message = input(f"{my_username} :> ")
    if message == "exit":
        break
    if message == "image":
        sendingimage()
        continue
    if message:
        message = message.encode("utf-8")
        message_header = f"{len(message):<{HEADER_LENGTH}}".encode("utf-8")
        client_socket.send(message_header + message + ISIMAGE)

    try:
        while True:  # for reciving
            username_header = client_socket.recv(HEADER_LENGTH)
            if not len(username_header):
                print("server closed the connection")
                break
            username_length = int(username_header.decode("utf-8"))
            theirusername = client_socket.recv(username_length).decode("utf-8")

            inbox_message_header = client_socket.recv(HEADER_LENGTH)
            inbox_message_length = int(inbox_message_header.decode("utf-8").strip())
            inbox_message = client_socket.recv(inbox_message_length)
            is_this_message_an_image = client_socket.recv(1).decode("utf-8")
            if is_this_message_an_image == "1":
                saveimage(inbox_message)
            else:
                if inbox_message.decode("utf-8") != ".":
                    inbox_message = inbox_message.decode("utf-8")
                    print(f"{theirusername}", ":> ", f"{inbox_message}")
    except IOError as e:
        if e.errno == errno.EAGAIN or e.errno == errno.EWOULDBLOCK:
            continue
    except Exception as k:
        print("ERROR", k)
        break
