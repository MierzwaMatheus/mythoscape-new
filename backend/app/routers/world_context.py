"""Router para gerenciamento do contexto do mundo do RPG."""

from uuid import UUID
from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.responses import JSONResponse

from app.dependencies.auth import AuthenticatedUser
from app.models.world_context import (
    EntityType, CreateEntityRequest, UpdateEntityRequest, 
    EntityResponse, EntitiesListResponse
)
from app.models.errors import (
    ErrorDetail, NotFoundError, ValidationError, 
    InternalServerError, AuthenticationError
)
from app.services.world_context import WorldContextService

router = APIRouter(prefix="/world", tags=["world-context"])


@router.post(
    "/entities",
    response_model=EntityResponse,
    responses={
        401: {"model": AuthenticationError, "description": "Não autenticado"},
        422: {"model": ValidationError, "description": "Dados inválidos"},
        500: {"model": InternalServerError, "description": "Erro interno do servidor"}
    }
)
async def create_entity(
    request: CreateEntityRequest,
    user_id: AuthenticatedUser
) -> EntityResponse:
    """Cria uma nova entidade no contexto do mundo."""
    try:
        service = WorldContextService()
        entity_data = await service.create_entity(
            entity_type=request.type.value,
            data=request.data.model_dump(),
            user_id=str(user_id),
            world_id=str(request.world_id)
        )
        return EntityResponse(**entity_data)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=ErrorDetail(
                error="internal_server_error",
                message="Erro ao criar entidade",
                details=str(e)
            ).model_dump()
        )


@router.get(
    "/entities",
    response_model=EntitiesListResponse,
    responses={
        401: {"model": AuthenticationError, "description": "Não autenticado"},
        500: {"model": InternalServerError, "description": "Erro interno do servidor"}
    }
)
async def list_entities(
    user_id: AuthenticatedUser,
    world_id: UUID = Query(..., description="ID do mundo"),
    entity_type: EntityType | None = Query(None, description="Filtrar por tipo de entidade"),
    page: int = Query(1, ge=1, description="Número da página"),
    per_page: int = Query(10, ge=1, le=100, description="Itens por página")
) -> EntitiesListResponse:
    """Lista entidades do mundo com paginação e filtros."""
    try:
        service = WorldContextService()
        entities_data = await service.list_entities(
            entity_type=entity_type.value if entity_type else None,
            user_id=str(user_id),
            world_id=str(world_id),
            page=page,
            per_page=per_page
        )
        return EntitiesListResponse(**entities_data)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=ErrorDetail(
                error="internal_server_error",
                message="Erro ao listar entidades",
                details=str(e)
            ).model_dump()
        )


@router.get(
    "/entities/{entity_id}",
    response_model=EntityResponse,
    responses={
        401: {"model": AuthenticationError, "description": "Não autenticado"},
        404: {"model": NotFoundError, "description": "Entidade não encontrada"},
        500: {"model": InternalServerError, "description": "Erro interno do servidor"}
    }
)
async def get_entity(
    entity_id: UUID,
    user_id: AuthenticatedUser,
    world_service: WorldContextService = Depends()
) -> EntityResponse:
    """
    Obtém uma entidade específica por ID.
    
    Args:
        entity_id: ID da entidade
        user_id: ID do usuário autenticado
        world_service: Serviço de contexto do mundo
        
    Returns:
        Dados da entidade
        
    Raises:
        HTTPException: Se a entidade não for encontrada
    """
    try:
        entity = await world_service.get_entity(entity_id, user_id)
        if not entity:
            raise HTTPException(
                status_code=404,
                detail=ErrorDetail(
                    message="Entidade não encontrada",
                    error_code="ENTITY_NOT_FOUND",
                    details={"entity_id": str(entity_id)}
                ).model_dump()
            )
        return entity
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=ErrorDetail(
                message="Erro interno ao buscar entidade",
                error_code="INTERNAL_ERROR",
                details={"original_error": str(e)}
            ).model_dump()
        )


@router.put(
    "/entities/{entity_id}",
    response_model=EntityResponse,
    responses={
        401: {"model": AuthenticationError, "description": "Não autenticado"},
        404: {"model": NotFoundError, "description": "Entidade não encontrada"},
        422: {"model": ValidationError, "description": "Dados inválidos"},
        500: {"model": InternalServerError, "description": "Erro interno do servidor"}
    }
)
async def update_entity(
    entity_id: UUID,
    request: UpdateEntityRequest,
    user_id: AuthenticatedUser,
    world_service: WorldContextService = Depends()
) -> EntityResponse:
    """
    Atualiza uma entidade existente.
    
    Args:
        entity_id: ID da entidade
        request: Dados para atualização
        user_id: ID do usuário autenticado
        world_service: Serviço de contexto do mundo
        
    Returns:
        Dados da entidade atualizada
        
    Raises:
        HTTPException: Em caso de erro na atualização
    """
    try:
        entity = await world_service.update_entity(entity_id, request, user_id)
        if not entity:
            raise HTTPException(
                status_code=404,
                detail=ErrorDetail(
                    message="Entidade não encontrada",
                    error_code="ENTITY_NOT_FOUND",
                    details={"entity_id": str(entity_id)}
                ).model_dump()
            )
        return entity
    except ValueError as e:
        raise HTTPException(
            status_code=422,
            detail=ErrorDetail(
                message=str(e),
                error_code="VALIDATION_ERROR"
            ).model_dump()
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=ErrorDetail(
                message="Erro interno ao atualizar entidade",
                error_code="INTERNAL_ERROR",
                details={"original_error": str(e)}
            ).model_dump()
        )


@router.delete(
    "/entities/{entity_id}",
    status_code=204,
    responses={
        401: {"model": AuthenticationError, "description": "Não autenticado"},
        404: {"model": NotFoundError, "description": "Entidade não encontrada"},
        500: {"model": InternalServerError, "description": "Erro interno do servidor"}
    }
)
async def delete_entity(
    entity_id: UUID,
    user_id: AuthenticatedUser,
    world_service: WorldContextService = Depends()
) -> None:
    """
    Remove uma entidade do mundo.
    
    Args:
        entity_id: ID da entidade
        user_id: ID do usuário autenticado
        world_service: Serviço de contexto do mundo
        
    Raises:
        HTTPException: Se a entidade não for encontrada
    """
    try:
        success = await world_service.delete_entity(entity_id, user_id)
        if not success:
            raise HTTPException(
                status_code=404,
                detail=ErrorDetail(
                    message="Entidade não encontrada",
                    error_code="ENTITY_NOT_FOUND",
                    details={"entity_id": str(entity_id)}
                ).model_dump()
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=ErrorDetail(
                message="Erro interno ao deletar entidade",
                error_code="INTERNAL_ERROR",
                details={"original_error": str(e)}
            ).model_dump()
        )