import socket
import threading

from user_manager import UserManager
from chat_room_manager import ChatRoomManager
from message_manager import MessageManager
from invitation_manager import InvitationManager
from logger import setup_logger
from config import load_config

config = load_config()

HOST = config["host"]
PORT = config["port"]

logger = setup_logger()

user_manager = UserManager()
room_manager = ChatRoomManager()
message_manager = MessageManager()
invitation_manager = InvitationManager()

room_manager.create_room("General")


def broadcast_to_room(room_name, sender_username, message):
    formatted_message = message_manager.format_message(sender_username, message)

    for username in room_manager.get_users_in_room(room_name):
        if username != sender_username:
            user_socket = user_manager.users.get(username)

            if user_socket:
                user_socket.send(formatted_message.encode())

    logger.info(f"Message sent by {sender_username} in room {room_name}")


def handle_client(client_socket, address):
    print(f"New connection: {address}")
    logger.info(f"New connection from {address}")

    username = client_socket.recv(1024).decode()

    if not user_manager.add_user(username, client_socket):
        client_socket.send("USERNAME_TAKEN".encode())
        logger.warning(f"Duplicate username attempt: {username}")
        client_socket.close()
        return

    client_socket.send("USERNAME_ACCEPTED".encode())

    print(f"User connected: {username}")
    logger.info(f"User connected: {username}")

    current_room = "General"
    room_manager.join_room(current_room, username)

    while True:
        try:
            command = client_socket.recv(1024).decode()

            if not command:
                break

            if command == "/list":
                rooms = room_manager.list_rooms()
                client_socket.send(("Available rooms: " + ", ".join(rooms)).encode())

            elif command.startswith("/create "):
                room_name = command.replace("/create ", "").strip()

                if room_name not in room_manager.list_rooms():
                    room_manager.create_room(room_name)
                    client_socket.send(f"Room '{room_name}' created".encode())
                    logger.info(f"{username} created room {room_name}")
                else:
                    client_socket.send(f"Room '{room_name}' already exists".encode())

            elif command.startswith("/join "):
                room_name = command.replace("/join ", "").strip()

                if room_name in room_manager.list_rooms():
                    room_manager.leave_room(current_room, username)
                    current_room = room_name
                    room_manager.join_room(current_room, username)
                    client_socket.send(f"Joined room '{current_room}'".encode())
                    logger.info(f"{username} joined room {current_room}")
                else:
                    client_socket.send(f"Room '{room_name}' does not exist".encode())

            elif command.startswith("/invite "):
                parts = command.split()

                if len(parts) != 3:
                    client_socket.send("Usage: /invite username roomname".encode())

                else:
                    receiver = parts[1]
                    room_name = parts[2]

                    if not user_manager.user_exists(receiver):
                        client_socket.send(f"User '{receiver}' is not online".encode())

                    elif room_name not in room_manager.list_rooms():
                        client_socket.send(f"Room '{room_name}' does not exist".encode())

                    else:
                        invitation_manager.create_invitation(username, receiver, room_name)

                        receiver_socket = user_manager.users.get(receiver)

                        if receiver_socket:
                            receiver_socket.send(
                                f"Invitation: {username} invited you to join {room_name}".encode()
                            )

                        client_socket.send(
                            f"Invitation sent to {receiver} for room '{room_name}'".encode()
                        )

                        logger.info(
                            f"{username} invited {receiver} to room {room_name}"
                        )

            elif command == "/quit":
                client_socket.send("Goodbye!".encode())
                logger.info(f"{username} disconnected")
                break

            else:
                broadcast_to_room(current_room, username, command)
                client_socket.send("Message sent".encode())

        except Exception as error:
            logger.error(f"Error with {username}: {error}")
            break

    room_manager.leave_room(current_room, username)
    user_manager.remove_user(username)
    client_socket.close()

    print(f"{username} disconnected")


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()

print(f"Server started on {HOST}:{PORT}")
print("Waiting for connections...")

logger.info(f"Server started on {HOST}:{PORT}")

while True:
    client_socket, address = server.accept()

    thread = threading.Thread(
        target=handle_client,
        args=(client_socket, address)
    )

    thread.start()
