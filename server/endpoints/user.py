from database import SessionDep
from fastapi import APIRouter, HTTPException
from models import User, UserCreate, UserCreateResponse

router = APIRouter()


@router.post("", response_model=UserCreateResponse)
def create_user(user: UserCreate, session: SessionDep):
    if User.get_user_by_username(session, user.username):
        raise HTTPException(400, "This user already exists")

    db_user = User.model_validate(user)
    password = User.generate_password()
    db_user.set_password(password)

    session.add(db_user)
    session.commit()

    return UserCreateResponse(password=password)
