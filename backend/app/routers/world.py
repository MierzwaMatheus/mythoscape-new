"""Router para gerenciamento de mundos/campanhas do RPG."""

from uuid import UUID
from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.responses import JSONResponse

from app.dependencies.auth import AuthenticatedUser
from app.models.world import (
    CreateWorldRequest, UpdateWorldRequest, 
    WorldResponse, WorldsListResponse, WorldStatsResponse
)
from app.models.errors import (
    ErrorDetail, NotFoundError, ValidationError, 
    InternalServerError, AuthenticationError
)

router = APIRouter(prefix="/worlds", tags=["worlds"])


@router.post(
    "/",
    response_model=WorldResponse,
    responses={
        401: {"model": AuthenticationError, "description": "Não autenticado"},
        422: {"model": ValidationError, "description": "Dados inválidos"},
        500: {"model": InternalServerError, "description": "Erro interno do servidor"}
    }
)
async def create_world(
    request: CreateWorldRequest,
    user_id: AuthenticatedUser
) -> WorldResponse:
    """Cria um novo mundo/campanha para o usuário."""
    try:
        # TODO: Implementar criação no banco de dados
        from datetime import datetime
        world_data = {
            "id": UUID("550e8400-e29b-41d4-a716-446655440001"),
            "name": request.name,
            "description": request.description,
            "theme": request.theme,
            "is_active": request.is_active,
            "user_id": user_id,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "entities_count": 0
        }
        return WorldResponse(**world_data)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=ErrorDetail(
                error="internal_server_error",
                message="Erro ao criar mundo",
                details=str(e)
            ).model_dump()
        )


@router.get(
    "/",
    response_model=WorldsListResponse,
    responses={
        401: {"model": AuthenticationError, "description": "Não autenticado"},
        500: {"model": InternalServerError, "description": "Erro interno do servidor"}
    }
)
async def list_worlds(
    user_id: AuthenticatedUser,
    page: int = Query(1, ge=1, description="Número da página"),
    per_page: int = Query(10, ge=1, le=100, description="Itens por página"),
    active_only: bool = Query(False, description="Listar apenas mundos ativos")
) -> WorldsListResponse:
    """Lista mundos do usuário com paginação."""
    try:
        # TODO: Implementar busca no banco com filtros
        from datetime import datetime
        mock_world = WorldResponse(
            id=UUID("550e8400-e29b-41d4-a716-446655440001"),
            name="Mundo de Exemplo",
            description="Um mundo de teste",
            theme="medieval",
            is_active=True,
            user_id=user_id,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            entities_count=5
        )
        
        return WorldsListResponse(
            worlds=[mock_world],
            total=1,
            page=page,
            per_page=per_page
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=ErrorDetail(
                error="internal_server_error",
                message="Erro ao listar mundos",
                details=str(e)
            ).model_dump()
        )


@router.get(
    "/{world_id}",
    response_model=WorldResponse,
    responses={
        401: {"model": AuthenticationError, "description": "Não autenticado"},
        404: {"model": NotFoundError, "description": "Mundo não encontrado"},
        500: {"model": InternalServerError, "description": "Erro interno do servidor"}
    }
)
async def get_world(
    world_id: UUID,
    user_id: AuthenticatedUser
) -> WorldResponse:
    """Obtém detalhes de um mundo específico."""
    try:
        # TODO: Implementar busca no banco com verificação de propriedade
        from datetime import datetime
        return WorldResponse(
            id=world_id,
            name="Mundo de Exemplo",
            description="Um mundo de teste",
            theme="medieval",
            is_active=True,
            user_id=user_id,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            entities_count=5
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=ErrorDetail(
                error="internal_server_error",
                message="Erro ao obter mundo",
                details=str(e)
            ).model_dump()
        )


@router.put(
    "/{world_id}",
    response_model=WorldResponse,
    responses={
        401: {"model": AuthenticationError, "description": "Não autenticado"},
        404: {"model": NotFoundError, "description": "Mundo não encontrado"},
        422: {"model": ValidationError, "description": "Dados inválidos"},
        500: {"model": InternalServerError, "description": "Erro interno do servidor"}
    }
)
async def update_world(
    world_id: UUID,
    request: UpdateWorldRequest,
    user_id: AuthenticatedUser
) -> WorldResponse:
    """Atualiza um mundo existente."""
    try:
        # TODO: Implementar atualização no banco com verificação de propriedade
        from datetime import datetime
        return WorldResponse(
            id=world_id,
            name=request.name or "Mundo Atualizado",
            description=request.description,
            theme=request.theme,
            is_active=request.is_active if request.is_active is not None else True,
            user_id=user_id,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            entities_count=5
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=ErrorDetail(
                error="internal_server_error",
                message="Erro ao atualizar mundo",
                details=str(e)
            ).model_dump()
        )


@router.delete(
    "/{world_id}",
    responses={
        401: {"model": AuthenticationError, "description": "Não autenticado"},
        404: {"model": NotFoundError, "description": "Mundo não encontrado"},
        500: {"model": InternalServerError, "description": "Erro interno do servidor"}
    }
)
async def delete_world(
    world_id: UUID,
    user_id: AuthenticatedUser
) -> JSONResponse:
    """Remove um mundo e todas suas entidades."""
    try:
        # TODO: Implementar remoção no banco com verificação de propriedade
        # Deve remover também todas as entidades associadas
        return JSONResponse(
            status_code=200,
            content={"message": "Mundo removido com sucesso"}
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=ErrorDetail(
                error="internal_server_error",
                message="Erro ao remover mundo",
                details=str(e)
            ).model_dump()
        )


@router.get(
    "/{world_id}/stats",
    response_model=WorldStatsResponse,
    responses={
        401: {"model": AuthenticationError, "description": "Não autenticado"},
        404: {"model": NotFoundError, "description": "Mundo não encontrado"},
        500: {"model": InternalServerError, "description": "Erro interno do servidor"}
    }
)
async def get_world_stats(
    world_id: UUID,
    user_id: AuthenticatedUser
) -> WorldStatsResponse:
    """Obtém estatísticas específicas de um mundo."""
    try:
        # TODO: Implementar consulta de estatísticas no banco
        from datetime import datetime
        return WorldStatsResponse(
            world_id=world_id,
            world_name="Mundo de Exemplo",
            total_entities=15,
            entities_by_type={
                "npc": 6,
                "location": 4,
                "knowledge": 5
            },
            total_sessions=3,
            active_sessions=1,
            last_activity=datetime.now(),
            created_at=datetime.now()
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