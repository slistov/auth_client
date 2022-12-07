from datetime import datetime


class User:
    def __init__(self, email: str, username: str):
        self.email = email
        self.username = username
        self.created = datetime.utcnow()
        self.is_active = True