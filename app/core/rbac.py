from fastapi import status, HTTPException
from functools import wraps

class PremissionChecker:
    def __init__(self, roles: list[str]):
        self.roles = roles

    def __call__(self, func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            user = kwargs.get("current_user")

            if not user:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="требуется аунтификация")
            
            if "admin" in user.roles:
                return await func(*args, **kwargs)
            
            if not any(role in user.roles for role in self.roles):
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Недостаточно прав")
            return await func(*args, **kwargs)
        return wrapper