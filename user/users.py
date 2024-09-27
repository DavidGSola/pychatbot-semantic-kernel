from typing import List

class User:
    id: str
    avatar: str
    
    def __init__(self, id: str):
        self.id = id
        self.avatar = f'https://api.dicebear.com/9.x/avataaars-neutral/svg?seed={id}'
        
users: List[User] = []

def add(id: str):
    users.append(User(id))
    
def find(id: str) -> User:
    return next(user for user in users if user.id == id)