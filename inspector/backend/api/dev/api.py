from fastapi import APIRouter

api_router = APIRouter()


@api_router.get("/")
async def read_main():
    return {"msg": "Hello World"}
