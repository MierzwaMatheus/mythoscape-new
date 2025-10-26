"""
Roteamento principal da API v1.
"""

from fastapi import APIRouter

from app.api.v1.endpoints import multiagent
from app.routers import chat, world, world_context, admin


api_router = APIRouter()

# Inclui rotas existentes sem duplicar prefixos
api_router.include_router(chat.router, tags=["chat"])
api_router.include_router(world.router, tags=["world"])
api_router.include_router(world_context.router, tags=["world-context"])
api_router.include_router(admin.router, tags=["admin"])

# Inclui novas rotas do sistema multiagente
api_router.include_router(multiagent.router, prefix="/multiagent", tags=["multiagent"])