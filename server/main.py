from endpoints.user import router as user_router
from fastapi import FastAPI

app = FastAPI()

app.include_router(user_router, prefix="/api/user", tags=["User"])
