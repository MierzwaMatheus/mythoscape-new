"""Modelos Pydantic para gerenciamento de mundos/campanhas do RPG."""

from datetime import datetime
from uuid import UUID
from typing import Optional
from pydantic import BaseModel, Field


class CreateWorldRequest(BaseModel):
    """Modelo para criação de novo mundo/campanha."""
    name: str = Field(..., min_length=1, max_length=100, description="Nome do mundo/campanha")
    description: Optional[str] = Field(None, max_length=1000, description="Descrição do mundo")
    theme: Optional[str] = Field(None, max_length=50, description="Tema do mundo (medieval, sci-fi, etc.)")
    is_active: bool = Field(True, description="Se o mundo está ativo")


class UpdateWorldRequest(BaseModel):
    """Modelo para atualização de mundo existente."""
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="Nome do mundo")
    description: Optional[str] = Field(None, max_length=1000, description="Descrição do mundo")
    theme: Optional[str] = Field(None, max_length=50, description="Tema do mundo")
    is_active: Optional[bool] = Field(None, description="Se o mundo está ativo")


class WorldResponse(BaseModel):
    """Modelo de resposta para um mundo."""
    id: UUID
    name: str
    description: Optional[str]
    theme: Optional[str]
    is_active: bool
    user_id: UUID
    created_at: datetime
    updated_at: datetime
    entities_count: int = Field(0, description="Número total de entidades no mundo")


class WorldsListResponse(BaseModel):
    """Modelo de resposta para lista de mundos."""
    worlds: list[WorldResponse]
    total: int
    page: int
    per_page: int


class WorldStatsResponse(BaseModel):
    """Modelo de resposta para estatísticas específicas de um mundo."""
    world_id: UUID
    world_name: str
    total_entities: int
    entities_by_type: dict[str, int]
    total_sessions: int
    active_sessions: int
    last_activity: Optional[datetime]
    created_at: datetime