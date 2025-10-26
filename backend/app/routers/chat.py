"""Roteador para funcionalidades de chat do Mestre de RPG."""

from fastapi import APIRouter
from app.dependencies.auth import OptionalUser

router = APIRouter(prefix="/chat", tags=["chat"])


@router.get("/")
async def chat_status(user_id: OptionalUser = None) -> dict[str, str]:
    """
    Endpoint de status do chat.
    Permite acesso público mas identifica usuários autenticados.
    
    Args:
        user_id: ID do usuário se autenticado, None caso contrário.
    
    Returns:
        Status do serviço de chat com informação do usuário.
    """
    if user_id:
        return {
            "status": "Chat service is running", 
            "user": user_id,
            "authenticated": True
        }
    else:
        return {
            "status": "Chat service is running", 
            "authenticated": False
        }