"""
Roteamento principal da API v1.
"""

from fastapi import APIRouter

from app.api.v1.endpoints import multiagent
from app.routers import chat, world, world_context, admin


api_router = APIRouter()

# Inclui rotas existentes
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(world.router, prefix="/world", tags=["world"])
api_router.include_router(world_context.router, prefix="/world-context", tags=["world-context"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])

# Inclui novas rotas do sistema multiagente
api_router.include_router(multiagent.router, prefix="/multiagent", tags=["multiagent"])