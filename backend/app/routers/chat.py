"""Roteador para funcionalidades de chat do Mestre de RPG."""

from fastapi import APIRouter, HTTPException
from app.dependencies.auth import OptionalUser
from app.models.errors import ErrorDetail, InternalServerError

router = APIRouter(prefix="/chat", tags=["chat"])


@router.get(
    "/",
    responses={
        500: {"model": InternalServerError, "description": "Erro interno do servidor"}
    }
)
async def chat_status(user_id: OptionalUser = None) -> dict[str, str | bool]:
    """
    Endpoint de status do chat.
    Permite acesso público mas identifica usuários autenticados.
    
    Args:
        user_id: ID do usuário se autenticado, None caso contrário.
    
    Returns:
        Status do serviço de chat com informação do usuário.
        
    Raises:
        HTTPException: Em caso de erro na verificação
    """
    try:
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
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=ErrorDetail(
                message="Erro na verificação do status do chat",
                error_code="CHAT_STATUS_ERROR",
                details={"original_error": str(e)}
            ).model_dump()
        )