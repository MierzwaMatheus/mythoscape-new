"""Router para endpoints administrativos do sistema."""

from datetime import datetime
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, HTTPException, Query, Depends
from fastapi.responses import JSONResponse

from app.dependencies.auth import AuthenticatedUser
from app.models.errors import (
    ErrorDetail, 
    AuthenticationError, 
    NotFoundError, 
    ValidationError, 
    InternalServerError
)
from app.models.session import (
    CreateSessionRequest,
    UpdateSessionRequest, 
    SessionResponse,
    SessionsListResponse,
    WorldStatsResponse,
    SystemStatsResponse
)

router = APIRouter(prefix="/admin", tags=["Administração"])


@router.post(
    "/sessions",
    response_model=SessionResponse,
    responses={
        401: {"model": AuthenticationError, "description": "Não autenticado"},
        422: {"model": ValidationError, "description": "Dados inválidos"},
        500: {"model": InternalServerError, "description": "Erro interno do servidor"}
    }
)
async def create_session(
    request: CreateSessionRequest,
    user_id: AuthenticatedUser
) -> SessionResponse:
    """Cria uma nova sessão de jogo."""
    try:
        # TODO: Implementar lógica de criação de sessão no banco
        session_data = {
            "id": UUID("550e8400-e29b-41d4-a716-446655440000"),  # Mock UUID
            "name": request.name,
            "description": request.description,
            "status": "active",
            "world_id": request.world_id,
            "user_id": user_id,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "last_activity": datetime.now()
        }
        return SessionResponse(**session_data)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=ErrorDetail(
                error="internal_server_error",
                message="Erro ao criar sessão",
                details=str(e)
            ).model_dump()
        )


@router.get(
    "/sessions",
    response_model=SessionsListResponse,
    responses={
        401: {"model": AuthenticationError, "description": "Não autenticado"},
        500: {"model": InternalServerError, "description": "Erro interno do servidor"}
    }
)
async def list_sessions(
    user_id: AuthenticatedUser,
    page: int = Query(1, ge=1, description="Número da página"),
    per_page: int = Query(10, ge=1, le=100, description="Itens por página"),
    status: Optional[str] = Query(None, description="Filtrar por status")
) -> SessionsListResponse:
    """Lista sessões do usuário com paginação."""
    try:
        # TODO: Implementar busca no banco com filtros
        mock_session = SessionResponse(
            id=UUID("550e8400-e29b-41d4-a716-446655440000"),
            name="Sessão de Exemplo",
            description="Uma sessão de teste",
            status="active",
            world_id=None,
            user_id=user_id,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            last_activity=datetime.now()
        )
        
        return SessionsListResponse(
            sessions=[mock_session],
            total=1,
            page=page,
            per_page=per_page
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=ErrorDetail(
                error="internal_server_error",
                message="Erro ao listar sessões",
                details=str(e)
            ).model_dump()
        )


@router.get(
    "/sessions/{session_id}",
    response_model=SessionResponse,
    responses={
        401: {"model": AuthenticationError, "description": "Não autenticado"},
        404: {"model": NotFoundError, "description": "Sessão não encontrada"},
        500: {"model": InternalServerError, "description": "Erro interno do servidor"}
    }
)
async def get_session(
    session_id: UUID,
    user_id: AuthenticatedUser
) -> SessionResponse:
    """Obtém detalhes de uma sessão específica."""
    try:
        # TODO: Implementar busca no banco
        if str(session_id) != "550e8400-e29b-41d4-a716-446655440000":
            raise HTTPException(
                status_code=404,
                detail=ErrorDetail(
                    error="not_found",
                    message="Sessão não encontrada",
                    details=f"Sessão com ID {session_id} não existe"
                ).model_dump()
            )
        
        return SessionResponse(
            id=session_id,
            name="Sessão de Exemplo",
            description="Uma sessão de teste",
            status="active",
            world_id=None,
            user_id=user_id,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            last_activity=datetime.now()
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=ErrorDetail(
                error="internal_server_error",
                message="Erro ao obter sessão",
                details=str(e)
            ).model_dump()
        )


@router.put(
    "/sessions/{session_id}",
    response_model=SessionResponse,
    responses={
        401: {"model": AuthenticationError, "description": "Não autenticado"},
        404: {"model": NotFoundError, "description": "Sessão não encontrada"},
        422: {"model": ValidationError, "description": "Dados inválidos"},
        500: {"model": InternalServerError, "description": "Erro interno do servidor"}
    }
)
async def update_session(
    session_id: UUID,
    request: UpdateSessionRequest,
    user_id: AuthenticatedUser
) -> SessionResponse:
    """Atualiza uma sessão existente."""
    try:
        # TODO: Implementar atualização no banco
        if str(session_id) != "550e8400-e29b-41d4-a716-446655440000":
            raise HTTPException(
                status_code=404,
                detail=ErrorDetail(
                    error="not_found",
                    message="Sessão não encontrada",
                    details=f"Sessão com ID {session_id} não existe"
                ).model_dump()
            )
        
        return SessionResponse(
            id=session_id,
            name=request.name or "Sessão Atualizada",
            description=request.description,
            status=request.status or "active",
            world_id=None,
            user_id=user_id,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            last_activity=datetime.now()
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=ErrorDetail(
                error="internal_server_error",
                message="Erro ao atualizar sessão",
                details=str(e)
            ).model_dump()
        )


@router.get(
    "/stats/world",
    response_model=WorldStatsResponse,
    responses={
        401: {"model": AuthenticationError, "description": "Não autenticado"},
        500: {"model": InternalServerError, "description": "Erro interno do servidor"}
    }
)
async def get_world_stats(user_id: AuthenticatedUser) -> WorldStatsResponse:
    """Obtém estatísticas do mundo do usuário."""
    try:
        # TODO: Implementar consulta de estatísticas no banco
        return WorldStatsResponse(
            total_entities=42,
            entities_by_type={
                "npc": 15,
                "location": 12,
                "knowledge": 15
            },
            total_sessions=5,
            active_sessions=2,
            last_updated=datetime.now()
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=ErrorDetail(
                error="internal_server_error",
                message="Erro ao obter estatísticas do mundo",
                details=str(e)
            ).model_dump()
        )


@router.get(
    "/stats/system",
    response_model=SystemStatsResponse,
    responses={
        401: {"model": AuthenticationError, "description": "Não autenticado"},
        500: {"model": InternalServerError, "description": "Erro interno do servidor"}
    }
)
async def get_system_stats(user_id: AuthenticatedUser) -> SystemStatsResponse:
    """Obtém estatísticas gerais do sistema."""
    try:
        # TODO: Implementar consulta de estatísticas do sistema
        return SystemStatsResponse(
            total_users=150,
            total_worlds=75,
            total_entities=1250,
            total_sessions=300,
            active_sessions=25,
            system_uptime="5 days, 12 hours",
            last_updated=datetime.now()
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=ErrorDetail(
                error="internal_server_error",
                message="Erro ao obter estatísticas do sistema",
                details=str(e)
            ).model_dump()
        )


@router.post(
    "/world/reset",
    responses={
        401: {"model": AuthenticationError, "description": "Não autenticado"},
        500: {"model": InternalServerError, "description": "Erro interno do servidor"}
    }
)
async def reset_world(user_id: AuthenticatedUser) -> JSONResponse:
    """Reseta o mundo do usuário, removendo todas as entidades."""
    try:
        # TODO: Implementar reset do mundo no banco
        return JSONResponse(
            content={
                "message": "Mundo resetado com sucesso",
                "timestamp": datetime.now().isoformat()
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=ErrorDetail(
                error="internal_server_error",
                message="Erro ao resetar mundo",
                details=str(e)
            ).model_dump()
        )