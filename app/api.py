from fastapi import APIRouter
from .endpoints import home,caption_generator

api_router = APIRouter()

api_router.include_router(home.router, prefix="/home", tags=["home"])
api_router.include_router(caption_generator.router, prefix="/caption_generator_api", tags=["caption_generator"])