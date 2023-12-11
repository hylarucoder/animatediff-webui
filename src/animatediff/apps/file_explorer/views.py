from fastapi import APIRouter

bp = APIRouter(prefix="/api/file_explorer")


@bp.get("/users/", tags=["users"])
async def read_users():
    return [{"username": "Rick"}, {"username": "Morty"}]


@bp.get("/users/me", tags=["users"])
async def read_user_me():
    return {"username": "fakecurrentuser"}


@bp.get("/users/{username}", tags=["users"])
async def read_user(username: str):
    return {"username": username}
