"""Modelos Pydantic para o contexto do mundo do RPG."""

from enum import Enum
from uuid import UUID, uuid4
from pydantic import BaseModel, Field
from typing import Any


class EntityType(str, Enum):
    """Tipos de entidades do mundo."""
    NPC = "npc"
    LOCATION = "location"
    KNOWLEDGE = "knowledge"


class BaseEntity(BaseModel):
    """Modelo base para entidades do mundo."""
    id: UUID = Field(default_factory=uuid4)
    type: EntityType
    name: str = Field(..., min_length=1, max_length=100)
    data: dict[str, Any] = Field(default_factory=dict)


class NPCData(BaseModel):
    """Dados específicos para NPCs."""
    status: str = Field(default="Vivo", description="Status atual do NPC")
    location_id: UUID | None = Field(None, description="ID do local onde o NPC está")
    personality: str | None = Field(None, max_length=500, description="Personalidade do NPC")
    history: str | None = Field(None, max_length=1000, description="História do NPC")
    relationships: dict[str, str] = Field(default_factory=dict, description="Relacionamentos com outros NPCs")


class LocationData(BaseModel):
    """Dados específicos para Locais."""
    description: str = Field(..., max_length=1000, description="Descrição do local")
    is_discovered: bool = Field(default=False, description="Se o local foi descoberto pelo jogador")
    npcs_present: list[UUID] = Field(default_factory=list, description="NPCs presentes no local")
    connections: list[UUID] = Field(default_factory=list, description="Locais conectados")
    items: list[str] = Field(default_factory=list, description="Itens disponíveis no local")


class KnowledgeData(BaseModel):
    """Dados específicos para Conhecimento."""
    topic: str = Field(..., max_length=200, description="Tópico do conhecimento")
    known_by_player: bool = Field(default=False, description="Se o jogador conhece esta informação")
    details: str = Field(..., max_length=2000, description="Detalhes do conhecimento")
    source: str | None = Field(None, max_length=200, description="Fonte do conhecimento")
    importance_level: int = Field(default=1, ge=1, le=5, description="Nível de importância (1-5)")


class CreateEntityRequest(BaseModel):
    """Modelo para criação de nova entidade no contexto do mundo."""
    type: EntityType = Field(..., description="Tipo da entidade")
    world_id: UUID = Field(..., description="ID do mundo onde a entidade será criada")
    data: NPCData | LocationData | KnowledgeData = Field(..., description="Dados da entidade")


class UpdateEntityRequest(BaseModel):
    """Modelo para atualização de entidade existente."""
    name: str | None = Field(None, min_length=1, max_length=100)
    data: NPCData | LocationData | KnowledgeData = Field(..., description="Novos dados da entidade")


class EntityResponse(BaseModel):
    """Modelo de resposta para uma entidade do contexto do mundo."""
    id: UUID
    type: EntityType
    world_id: UUID
    user_id: UUID
    data: NPCData | LocationData | KnowledgeData
    created_at: datetime
    updated_at: datetime


class EntitiesListResponse(BaseModel):
    """Resposta com lista de entidades."""
    entities: list[EntityResponse]
    total: int
    page: int = 1
    page_size: int = 50