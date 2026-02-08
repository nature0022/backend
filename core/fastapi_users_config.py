from fastapi_users import FastAPIUsers

from core.security import auth_backend
from core.user_manager import get_user_manager
from models.user import User

fastapi_users = FastAPIUsers[User, int](
    get_user_manager=get_user_manager,
    auth_backends=[auth_backend],
)

current_active_user = fastapi_users.current_user(active=True)
