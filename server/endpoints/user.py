from authentication import AdminSession, UserSession
from database import DbSession
from fastapi import APIRouter, HTTPException
from models.user import (
    ChangePasswordRequest,
    CreateUserRequest,
    CreateUserResponse,
    GetAllUsersResponse,
    GetCurrentUserResponse,
    ResetPasswordResponse,
    UpdateUserRequest,
    User,
)
from response import DetailResponse

router = APIRouter()


@router.post("/", response_model=CreateUserResponse)
def create_user(body: CreateUserRequest, db_session: DbSession, admin_session: AdminSession):
    if User.get_user_by_username(db_session, body.username):
        raise HTTPException(400, "This user already exists")

    password = User.generate_password()
    password_hash = User.hash_password(password)
    db_user = User.model_validate({**body.model_dump(), "password_hash": password_hash, "is_admin": False, "first_login": True})

    db_session.add(db_user)
    db_session.commit()

    return {"password": password}


@router.post("/password")
def change_password(body: ChangePasswordRequest, db_session: DbSession, user_session: UserSession):
    user, token_payload = user_session

    if not user.check_password(body.old_password):
        raise HTTPException(400, "Old password is incorrect")

    user.password_hash = User.hash_password(body.password1)
    user.first_login = False

    db_session.add(user)
    db_session.commit()

    return DetailResponse("Password changed successfully")


@router.post("/{user_id}/password", response_model=ResetPasswordResponse)
def reset_password(user_id: int, db_session: DbSession, admin_session: AdminSession):
    user = User.get_user_by_id(db_session, user_id)
    if not user:
        raise HTTPException(404)

    password = User.generate_password()
    user.password_hash = User.hash_password(password)
    user.first_login = True

    db_session.add(user)
    db_session.commit()

    return {"password": password}


@router.get("/current", response_model=GetCurrentUserResponse)
def get_current_user(db_session: DbSession, user_session: UserSession):
    user, token_payload = user_session

    return {**user.model_dump(), "mfa": bool(user.mfa_secret)}


@router.delete("/{user_id}")
def delete_user(user_id: int, db_session: DbSession, admin_session: AdminSession):
    user, token_payload = admin_session

    if User.get_user_count(db_session) <= 1:
        raise HTTPException(400, "Can't delete the only user")

    if user.id == user_id:
        raise HTTPException(400, "Can't delete yourself")

    user_to_delete = User.get_user_by_id(db_session, user_id)
    if not user_to_delete:
        raise HTTPException(404)

    db_session.delete(user_to_delete)
    db_session.commit()

    return DetailResponse(f"User {user.username} deleted successfully")


@router.patch("/{user_id}")
def update_user(body: UpdateUserRequest, user_id: int, db_session: DbSession, admin_session: AdminSession):
    user, token_payload = admin_session

    if user.id == user_id:
        raise HTTPException(400, "Can't demote yourself")

    user_to_update = User.get_user_by_id(db_session, user_id)
    if not user_to_update:
        raise HTTPException(404)

    user_to_update.is_admin = body.is_admin
    db_session.add(user)
    db_session.commit()

    return DetailResponse(f"User {user_to_update.username} modified successfully")


@router.get("/", response_model=list[GetAllUsersResponse])
def get_all_users(db_session: DbSession, user_session: UserSession):
    users = User.get_all_users(db_session)

    return [{**user.model_dump(), "mfa": bool(user.mfa_secret)} for user in users]
