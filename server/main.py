from endpoints.auth import router as auth_router
from endpoints.user import router as user_router
from fastapi import FastAPI

app = FastAPI()

app.include_router(user_router, prefix="/api/user", tags=["User"])
app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])
