from app.errors.base import CustomExeption

class UserNotFound(CustomExeption):
    def __init__(self, detail = None):
        super().__init__(status_code=404, detail=detail)

class UserAlreadyExists(CustomExeption):
    def __init__(self, detail=None):
        super().__init__(status_code=409, detail=detail)

class InvalidCredentials(CustomExeption):
    def __init__(self, detail):
        super().__init__(status_code=401, detail=detail)