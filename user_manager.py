class UserManager:
    def __init__(self):
        self.users = {}

    def add_user(self, username, client_socket):
        if username in self.users:
            return False

        self.users[username] = client_socket
        return True

    def remove_user(self, username):
        if username in self.users:
            del self.users[username]

    def user_exists(self, username):
        return username in self.users

    def get_all_users(self):
        return list(self.users.keys())
