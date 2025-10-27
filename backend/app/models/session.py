"""Modelos Pydantic para gerenciamento de sessões de jogo."""

from datetime import datetime
from typing import Optional, Literal
from uuid import UUID, uuid4
from enum import Enum
from pydantic import BaseModel, Field


class SessionStatus(str):
    """Status possíveis para uma sessão de jogo."""
    ACTIVE = "active"
    PAUSED = "paused" 
    COMPLETED = "completed"
    ARCHIVED = "archived"


class MessageRole(str, Enum):
    """Papéis possíveis para mensagens de chat."""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    FUNCTION = "function"


class ChatMessage(BaseModel):
    """Modelo para mensagens de chat em uma sessão."""
    id: str = Field(default_factory=lambda: str(uuid4()))
    role: MessageRole
    content: str
    timestamp: int = Field(default_factory=lambda: int(datetime.now().timestamp()))
    metadata: Optional[dict] = Field(default_factory=dict)
    
    class Config:
        use_enum_values = True


class CreateSessionRequest(BaseModel):
    """Modelo para criação de nova sessão."""
    name: str = Field(..., min_length=1, max_length=100, description="Nome da sessão")
    description: Optional[str] = Field(None, max_length=500, description="Descrição da sessão")
    world_id: Optional[UUID] = Field(None, description="ID do mundo associado")


class UpdateSessionRequest(BaseModel):
    """Modelo para atualização de sessão existente."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    status: Optional[str] = Field(None, description="Status da sessão")


class SessionResponse(BaseModel):
    """Modelo de resposta para uma sessão."""
    id: UUID
    name: str
    description: Optional[str]
    status: str
    world_id: Optional[UUID]
    user_id: UUID
    created_at: datetime
    updated_at: datetime
    last_activity: Optional[datetime]


class SessionsListResponse(BaseModel):
    """Modelo de resposta para lista de sessões."""
    sessions: list[SessionResponse]
    total: int
    page: int
    per_page: int


class WorldStatsResponse(BaseModel):
    """Modelo de resposta para estatísticas do mundo."""
    total_entities: int
    entities_by_type: dict[str, int]
    total_sessions: int
    active_sessions: int
    last_updated: datetime


class SystemStatsResponse(BaseModel):
    """Modelo de resposta para estatísticas do sistema."""
    total_users: int
    total_worlds: int
    total_entities: int
    total_sessions: int
    active_sessions: int
    system_uptime: str
    last_updated: datetime