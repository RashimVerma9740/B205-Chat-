class InvitationManager:
    def __init__(self):
        self.invitations = []

    def create_invitation(self, sender, receiver, room):
        invitation = {
            "sender": sender,
            "receiver": receiver,
            "room": room
        }

        self.invitations.append(invitation)

        return invitation
