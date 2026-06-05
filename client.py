import socket
import threading

from config import load_config

config = load_config()

HOST = config["host"]
PORT = config["port"]

client = socket.socket(
    socket.AF_INET,
    socket.SOCK_STREAM
)

client.connect((HOST, PORT))


def receive_messages():

    while True:

        try:

            message = client.recv(1024).decode()

            if message:
                print(message)

            else:
                break

        except:
            break


username = input("Enter username: ")

client.send(username.encode())

response = client.recv(1024).decode()

print(response)

if response == "USERNAME_ACCEPTED":

    receive_thread = threading.Thread(
        target=receive_messages
    )

    receive_thread.daemon = True
    receive_thread.start()

    while True:

        command = input()

        client.send(command.encode())

        if command == "/quit":
            break

client.close()
