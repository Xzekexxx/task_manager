from app.errors.base import CustomExeption

class InvalidCredentials(CustomExeption):
    def __init__(self, detail=None):
        super().__init__(status_code=401, detail=detail)

class TaskNotFound(CustomExeption):
    def __init__(self, detail):
        super().__init__(status_code=404, detail=detail)