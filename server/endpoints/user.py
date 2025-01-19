from authentication import UserSession
from database import DbSession
from fastapi import APIRouter, HTTPException
from models.user import CreateUser, CreateUserResponse, User

router = APIRouter()


@router.post("/", response_model=CreateUserResponse)
def create_user(body: CreateUser, db_session: DbSession, user_session: UserSession):
    if User.get_user_by_username(db_session, body.username):
        raise HTTPException(400, "This user already exists")

    password = User.generate_password()
    password_hash = User.hash_password(password)
    db_user = User.model_validate({**body.model_dump(), "password_hash": password_hash, "is_admin": False, "first_login": True})

    db_session.add(db_user)
    db_session.commit()

    return {"password": password}
