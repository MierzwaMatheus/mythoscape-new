"""Roteador para funcionalidades de chat do Mestre de RPG."""

from fastapi import APIRouter

router = APIRouter(prefix="/chat", tags=["chat"])


@router.get("/")
async def chat_status() -> dict[str, str]:
    """
    Endpoint de status do chat.
    
    Returns:
        Status do serviço de chat.
    """
    return {"status": "Chat service is running"}