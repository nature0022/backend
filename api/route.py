from fastapi import APIRouter

from .endpoints import chats, contents, directories, flash_cards, health, notebooks, quizzes, sources, users

api_router = APIRouter()

api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(users.router)
api_router.include_router(notebooks.router, prefix="/notebooks", tags=["notebooks"])
api_router.include_router(chats.router, prefix="/chats", tags=["chats"])
api_router.include_router(contents.router, prefix="/contents", tags=["contents"])
api_router.include_router(directories.router, prefix="/directories", tags=["directories"])
api_router.include_router(sources.router, prefix="/sources", tags=["sources"])
api_router.include_router(quizzes.router, prefix="/quizzes", tags=["quizzes"])
api_router.include_router(flash_cards.router, prefix="/flash-cards", tags=["flash-cards"])
