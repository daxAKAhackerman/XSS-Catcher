from database import DbSession
from fastapi import APIRouter, HTTPException
from models.user import User, UserCreate, UserCreateResponse

router = APIRouter()


@router.post("/", response_model=UserCreateResponse)
def create_user(user: UserCreate, db_session: DbSession):
    if User.get_user_by_username(db_session, user.username):
        raise HTTPException(400, "This user already exists")

    password = User.generate_password()
    password_hash = User.hash_password(password)
    db_user = User.model_validate({**user.model_dump(), "password_hash": password_hash, "is_admin": False, "first_login": True})

    db_session.add(db_user)
    db_session.commit()

    return UserCreateResponse(password=password)
