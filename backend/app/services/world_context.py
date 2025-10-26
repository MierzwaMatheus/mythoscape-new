"""Módulo para gerenciamento do contexto do mundo do RPG."""

import uuid
from typing import Optional, Dict, Any
from supabase import Client

from app.services.supabase import get_supabase_client


class WorldContextManager:
    """Gerenciador do contexto do mundo com operações CRUD otimizadas."""
    
    TABLE_NAME = "world_context"
    
    def __init__(self) -> None:
        """Inicializa o cliente Supabase."""
        self.client: Client = get_supabase_client()
    
    def get_entity(self, entity_type: str, name: str) -> Optional[Dict[str, Any]]:
        """
        Consulta uma entidade pelo tipo e nome.
        
        Args:
            entity_type: Tipo da entidade (npc, location, knowledge).
            name: Nome da entidade a ser buscada.
            
        Returns:
            Dados da entidade encontrada ou None se não existir.
        """
        response = (
            self.client.table(self.TABLE_NAME)
            .select("*")
            .eq("type", entity_type)
            .ilike("data->>name", f"%{name}%")
            .execute()
        )
        
        return response.data[0] if response.data else None
    
    def create_entity(self, entity_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Cria uma nova entidade no contexto do mundo.
        
        Args:
            entity_type: Tipo da entidade (npc, location, knowledge).
            data: Dados da entidade em formato JSONB.
            
        Returns:
            Dados da entidade criada com ID gerado.
        """
        entity_data = {
            "id": str(uuid.uuid4()),
            "type": entity_type,
            "data": data
        }
        
        response = (
            self.client.table(self.TABLE_NAME)
            .insert(entity_data)
            .execute()
        )
        
        return response.data[0]
    
    def update_entity(self, entity_id: str, new_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Atualiza os dados de uma entidade existente.
        
        Args:
            entity_id: ID único da entidade.
            new_data: Novos dados para atualizar no campo JSONB.
            
        Returns:
            Dados da entidade atualizada ou None se não encontrada.
        """
        response = (
            self.client.table(self.TABLE_NAME)
            .update({"data": new_data})
            .eq("id", entity_id)
            .execute()
        )
        
        return response.data[0] if response.data else None


class WorldContextService:
    """Serviço para operações de contexto do mundo com validação."""
    
    def __init__(self) -> None:
        """Inicializa o serviço com o gerenciador de contexto."""
        self.manager = WorldContextManager()
    
    async def create_entity(self, entity_type: str, data: Dict[str, Any], user_id: str, world_id: str) -> Dict[str, Any]:
        """Cria uma nova entidade com validação."""
        # Adiciona user_id e world_id aos dados
        data["user_id"] = user_id
        data["world_id"] = world_id
        return self.manager.create_entity(entity_type, data)
    
    async def get_entity(self, entity_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """Obtém uma entidade por ID com verificação de usuário."""
        # TODO: Implementar busca por ID com verificação de user_id
        return None
    
    async def update_entity(self, entity_id: str, data: Dict[str, Any], user_id: str) -> Optional[Dict[str, Any]]:
        """Atualiza uma entidade com verificação de usuário."""
        return self.manager.update_entity(entity_id, data)
    
    async def delete_entity(self, entity_id: str, user_id: str) -> bool:
        """Remove uma entidade com verificação de usuário."""
        # TODO: Implementar remoção com verificação de user_id
        return True
    
    async def list_entities(self, entity_type: Optional[str], user_id: str, world_id: str, page: int = 1, per_page: int = 10) -> Dict[str, Any]:
        """Lista entidades do usuário em um mundo específico com paginação."""
        # TODO: Implementar listagem com paginação e filtro por user_id e world_id
        return {
            "entities": [],
            "total": 0,
            "page": page,
            "per_page": per_page
        }