from database import SessionDep
from fastapi import APIRouter, HTTPException
from models.user import User, UserChangePassword, UserCreate, UserCreateResponse

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


# @router.post("password")
# def change_user_password(user: UserChangePassword, session: SessionDep):


# @bp.route("/user/password", methods=["POST"])
# @authorization_required()
# @validate()
# def change_password(body: ChangePasswordModel):
#     current_user: User = get_current_user()

#     if not current_user.check_password(body.old_password):
#         return {"msg": "Old password is incorrect"}, 400

#     current_user.set_password(body.password1)
#     current_user.first_login = False

#     db.session.commit()
#     return {"msg": "Password changed successfully"}
