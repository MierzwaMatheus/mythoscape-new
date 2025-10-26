"""Ferramentas LangChain para manipulação do contexto do mundo do RPG."""

import json
from typing import Any, Dict
from pydantic import BaseModel, Field
from langchain.tools import BaseTool

from app.services.world_context import WorldContextManager


class GetEntitySchema(BaseModel):
    """Schema para busca de entidades."""
    entity_type: str = Field(description="Tipo da entidade: 'npc', 'location' ou 'knowledge'")
    name: str = Field(description="Nome da entidade a ser buscada")


class CreateEntitySchema(BaseModel):
    """Schema para criação de entidades."""
    entity_type: str = Field(description="Tipo da entidade: 'npc', 'location' ou 'knowledge'")
    data: Dict[str, Any] = Field(description="Dados da entidade em formato JSON")


class UpdateEntitySchema(BaseModel):
    """Schema para atualização de entidades."""
    entity_id: str = Field(description="ID único da entidade a ser atualizada")
    new_data: Dict[str, Any] = Field(description="Novos dados da entidade em formato JSON")


class GetEntityTool(BaseTool):
    """Ferramenta para buscar entidades do contexto do mundo."""
    
    name: str = "get_entity"
    description: str = (
        "Busca uma entidade específica do contexto do mundo por tipo e nome. "
        "Use para consultar informações sobre NPCs, locais ou conhecimentos existentes. "
        "Tipos válidos: 'npc', 'location', 'knowledge'."
    )
    args_schema: type[BaseModel] = GetEntitySchema
    
    def __init__(self) -> None:
        super().__init__()
        # Inicializa o manager como atributo privado para evitar conflitos com Pydantic
        self._manager = WorldContextManager()
    
    def _run(self, entity_type: str, name: str) -> str:
        """
        Executa a busca de entidade.
        
        Args:
            entity_type: Tipo da entidade.
            name: Nome da entidade.
            
        Returns:
            String formatada com os dados da entidade ou mensagem de não encontrada.
        """
        entity = self._manager.get_entity(entity_type, name)
        
        if entity:
            return json.dumps(entity, ensure_ascii=False, indent=2)
        else:
            return f"Entidade do tipo '{entity_type}' com nome '{name}' não foi encontrada."


class CreateEntityTool(BaseTool):
    """Ferramenta para criar novas entidades no contexto do mundo."""
    
    name: str = "create_entity"
    description: str = (
        "Cria uma nova entidade no contexto do mundo. "
        "Use quando descobrir novos NPCs, locais ou conhecimentos durante a aventura. "
        "Tipos válidos: 'npc', 'location', 'knowledge'. "
        "Os dados devem incluir pelo menos um campo 'name'."
    )
    args_schema: type[BaseModel] = CreateEntitySchema
    
    def __init__(self) -> None:
        super().__init__()
        # Inicializa o manager como atributo privado para evitar conflitos com Pydantic
        self._manager = WorldContextManager()
    
    def _run(self, entity_type: str, data: Dict[str, Any]) -> str:
        """
        Executa a criação de entidade.
        
        Args:
            entity_type: Tipo da entidade.
            data: Dados da entidade.
            
        Returns:
            String confirmando a criação ou mensagem de erro.
        """
        entity_id = self._manager.create_entity(entity_type, data)
        
        if entity_id:
            return f"Entidade '{data.get('name', 'sem nome')}' criada com sucesso. ID: {entity_id}"
        else:
            return f"Erro ao criar entidade do tipo '{entity_type}'."


class UpdateEntityTool(BaseTool):
    """Ferramenta para atualizar entidades existentes no contexto do mundo."""
    
    name: str = "update_entity"
    description: str = (
        "Atualiza uma entidade existente no contexto do mundo. "
        "Use quando o estado de um NPC, local ou conhecimento mudar durante a aventura. "
        "Exemplo: NPC morre, local é destruído, jogador aprende nova informação."
    )
    args_schema: type[BaseModel] = UpdateEntitySchema
    
    def __init__(self) -> None:
        super().__init__()
        # Inicializa o manager como atributo privado para evitar conflitos com Pydantic
        self._manager = WorldContextManager()
    
    def _run(self, entity_id: str, new_data: Dict[str, Any]) -> str:
        """
        Executa a atualização de entidade.
        
        Args:
            entity_id: ID da entidade.
            new_data: Novos dados da entidade.
            
        Returns:
            String confirmando a atualização ou mensagem de erro.
        """
        success = self._manager.update_entity(entity_id, new_data)
        
        if success:
            return f"Entidade com ID '{entity_id}' atualizada com sucesso."
        else:
            return f"Erro: Entidade com ID '{entity_id}' não foi encontrada."


# Lista de ferramentas para exportação
world_context_tools = [
    GetEntityTool(),
    CreateEntityTool(),
    UpdateEntityTool()
]