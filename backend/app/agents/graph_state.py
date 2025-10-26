"""
Estado do grafo para o sistema multiagente LangGraph.
Define a estrutura de dados compartilhada entre todos os nós do grafo.
"""

from typing import TypedDict, Optional, Any
from datetime import datetime


class AgentState(TypedDict):
    """Estado compartilhado entre todos os nós do grafo multiagente."""
    
    # Entrada original do usuário
    user_input: str
    
    # Contexto do mundo/campanha
    world_id: str
    user_id: str
    character_id: Optional[str]
    world_context: Optional[dict]
    
    # Roteamento
    selected_agents: list[dict]  # Lista de agentes selecionados pelo roteador
    
    # Saídas dos agentes especialistas
    specialist_outputs: list[dict]  # Resultados de cada agente especialista
    
    # Resultado final
    final_narrative: Optional[str]  # Narrativa final do sintetizador
    duration_minutes: Optional[int]  # Duração das ações em minutos
    vector_store_updates: Optional[list[dict]]  # Atualizações para o vector store
    
    # Metadados de execução
    execution_start: Optional[datetime]
    execution_end: Optional[datetime]
    errors: list[str]  # Lista de erros ocorridos durante a execução
    
    # Dados adicionais que podem ser necessários
    additional_data: dict[str, Any]


class SpecialistOutput(TypedDict):
    """Estrutura padronizada para saída de agentes especialistas."""
    
    source_agent: str  # Nome do agente que gerou a saída
    content_type: str  # Tipo de conteúdo (description, action_result, etc.)
    data: str  # Conteúdo principal da resposta
    referenced_ids: dict[str, str]  # IDs de entidades referenciadas
    metadata: Optional[dict]  # Metadados adicionais
    success: bool  # Se a operação foi bem-sucedida
    error_message: Optional[str]  # Mensagem de erro se houver


class VectorStoreUpdate(TypedDict):
    """Estrutura para atualizações do vector store."""
    
    entity_id: str  # ID da entidade
    entity_type: str  # Tipo da entidade (npc, location, etc.)
    text_chunk: str  # Texto a ser armazenado
    metadata: dict  # Metadados para o chunk
    world_id: str  # ID do mundo
    user_id: str  # ID do usuário