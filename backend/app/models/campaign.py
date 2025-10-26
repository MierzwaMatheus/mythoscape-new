"""
Modelos para criação e gerenciamento de campanhas.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class CampaignCreationRequest(BaseModel):
    """Modelo para requisição de criação de campanha."""
    
    # Cenário
    name: str = Field(..., description="Nome da campanha")
    genre_tags: List[str] = Field(..., description="Tags de gênero/tema")
    inspiration: Optional[str] = Field(None, description="Inspiração opcional")
    
    # Mestre
    master_personality: str = Field(
        ..., 
        description="Personalidade do mestre", 
        examples=["serious_dark", "epic_heroic", "comic_light", "mysterious_occult"]
    )
    
    # Protagonista
    character_concept: str = Field(..., description="Conceito principal do personagem")
    character_name: Optional[str] = Field(None, description="Nome do personagem (opcional)")
    character_archetypes: List[str] = Field(..., description="2-3 arquétipos selecionados")
    character_approaches: List[str] = Field(..., description="2 abordagens selecionadas")


class CampaignCreationResponse(BaseModel):
    """Modelo para resposta de criação de campanha."""
    
    campaign: Dict[str, Any] = Field(..., description="Dados da campanha")
    character: Dict[str, Any] = Field(..., description="Dados do personagem")
    world_entities: Dict[str, List[Dict[str, Any]]] = Field(..., description="Entidades do mundo")
    campaign_time: Dict[str, Any] = Field(..., description="Tempo inicial da campanha")
    initial_mission: Optional[Dict[str, Any]] = Field(None, description="Missão inicial opcional")
    success: bool = Field(..., description="Indica se a criação foi bem-sucedida")
    error_message: Optional[str] = Field(None, description="Mensagem de erro, se houver")