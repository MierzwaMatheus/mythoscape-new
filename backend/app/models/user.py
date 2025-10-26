"""
Modelo de usuário.
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import Column, String, Boolean, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
from pydantic import BaseModel, Field
import uuid

from app.core.database import Base


class UserTable(Base):
    """Tabela de usuários no banco de dados."""
    
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    avatar_url = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    preferences = Column(Text, nullable=True)  # JSON serializado
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_login = Column(DateTime, nullable=True)


class User(BaseModel):
    """Modelo Pydantic para usuário."""
    
    id: str = Field(..., description="ID único do usuário")
    email: str = Field(..., description="Email do usuário")
    name: str = Field(..., description="Nome do usuário")
    avatar_url: Optional[str] = Field(None, description="URL do avatar do usuário")
    is_active: bool = Field(True, description="Se o usuário está ativo")
    preferences: Optional[dict] = Field(default_factory=dict, description="Preferências do usuário")
    created_at: Optional[datetime] = Field(None, description="Data de criação")
    updated_at: Optional[datetime] = Field(None, description="Data de última atualização")
    last_login: Optional[datetime] = Field(None, description="Data do último login")
    
    class Config:
        from_attributes = True


class UserCreate(BaseModel):
    """Modelo para criação de usuário."""
    
    email: str = Field(..., description="Email do usuário", max_length=255)
    name: str = Field(..., description="Nome do usuário", max_length=255)
    avatar_url: Optional[str] = Field(None, description="URL do avatar", max_length=500)
    preferences: Optional[dict] = Field(default_factory=dict, description="Preferências iniciais")


class UserUpdate(BaseModel):
    """Modelo para atualização de usuário."""
    
    name: Optional[str] = Field(None, description="Nome do usuário", max_length=255)
    avatar_url: Optional[str] = Field(None, description="URL do avatar", max_length=500)
    is_active: Optional[bool] = Field(None, description="Status ativo do usuário")
    preferences: Optional[dict] = Field(None, description="Preferências do usuário")


class UserResponse(BaseModel):
    """Modelo de resposta para usuário."""
    
    id: str = Field(..., description="ID único do usuário")
    email: str = Field(..., description="Email do usuário")
    name: str = Field(..., description="Nome do usuário")
    avatar_url: Optional[str] = Field(None, description="URL do avatar do usuário")
    is_active: bool = Field(..., description="Se o usuário está ativo")
    created_at: datetime = Field(..., description="Data de criação")
    updated_at: datetime = Field(..., description="Data de última atualização")
    last_login: Optional[datetime] = Field(None, description="Data do último login")
    
    class Config:
        from_attributes = True