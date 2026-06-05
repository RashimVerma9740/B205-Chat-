class ChatRoomManager:
    def __init__(self):
        self.rooms = {}

    def create_room(self, room_name):
        if room_name not in self.rooms:
            self.rooms[room_name] = []

    def join_room(self, room_name, username):
        if room_name in self.rooms and username not in self.rooms[room_name]:
            self.rooms[room_name].append(username)

    def leave_room(self, room_name, username):
        if room_name in self.rooms and username in self.rooms[room_name]:
            self.rooms[room_name].remove(username)

    def list_rooms(self):
        return list(self.rooms.keys())

    def get_users_in_room(self, room_name):
        return self.rooms.get(room_name, [])
