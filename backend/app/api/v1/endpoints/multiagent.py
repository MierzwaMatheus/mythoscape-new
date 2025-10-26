"""
Endpoints para o sistema multiagente.
"""

from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel, Field
from datetime import datetime

from app.agents import MultiAgentGraph, AgentState
from app.services.multiagent_service import MultiAgentService
from app.core.deps import get_current_user
from app.models.user import User


router = APIRouter()


class ActionRequest(BaseModel):
    """Modelo para requisição de ação do usuário."""
    action: str = Field(..., description="Ação do usuário", min_length=1, max_length=2000)
    world_context: Optional[dict] = Field(default_factory=dict, description="Contexto adicional do mundo")
    character_id: Optional[str] = Field(None, description="ID do personagem (opcional)")
    campaign_id: Optional[str] = Field(None, description="ID da campanha (opcional)")


class ActionResponse(BaseModel):
    """Modelo para resposta de ação processada."""
    narrative: str = Field(..., description="Narrativa final gerada")
    execution_time: float = Field(..., description="Tempo de execução em segundos")
    agents_used: list[str] = Field(..., description="Lista de agentes utilizados")
    success: bool = Field(..., description="Se o processamento foi bem-sucedido")
    metadata: dict = Field(default_factory=dict, description="Metadados da execução")


class GraphVisualizationResponse(BaseModel):
    """Modelo para resposta de visualização do grafo."""
    mermaid_diagram: str = Field(..., description="Diagrama Mermaid do grafo")
    nodes_count: int = Field(..., description="Número de nós no grafo")
    edges_count: int = Field(..., description="Número de arestas no grafo")


class AgentStatusResponse(BaseModel):
    """Modelo para status dos agentes."""
    available_agents: list[str] = Field(..., description="Lista de agentes disponíveis")
    system_status: str = Field(..., description="Status do sistema multiagente")
    last_execution: Optional[datetime] = Field(None, description="Última execução")


@router.post("/process-action", response_model=ActionResponse)
async def process_action(
    request: ActionRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    multiagent_service: MultiAgentService = Depends()
) -> ActionResponse:
    """
    Processa uma ação do usuário através do sistema multiagente.
    
    Este endpoint é o ponto principal de entrada para o processamento de ações
    de RPG, utilizando o sistema multiagente para gerar narrativas coesas.
    """
    
    try:
        # Enriquece contexto com dados do usuário
        enriched_context = await multiagent_service.enrich_world_context(
            request.world_context,
            user_id=current_user.id,
            character_id=request.character_id,
            campaign_id=request.campaign_id
        )
        
        # Processa a ação
        result = await multiagent_service.process_user_action(
            user_input=request.action,
            world_context=enriched_context,
            user_id=current_user.id
        )
        
        # Agenda tarefas em background se necessário
        if result.vector_store_updates:
            background_tasks.add_task(
                multiagent_service.process_vector_store_updates,
                result.vector_store_updates,
                current_user.id
            )
        
        # Agenda salvamento de logs
        background_tasks.add_task(
            multiagent_service.save_execution_log,
            result,
            current_user.id,
            request.action
        )
        
        return ActionResponse(
            narrative=result.final_narrative,
            execution_time=result.execution_duration,
            agents_used=result.selected_agents,
            success=bool(result.final_narrative and result.final_narrative.strip()),
            metadata={
                "execution_metadata": result.execution_metadata,
                "specialists_count": len(result.specialist_outputs),
                "successful_specialists": len([
                    output for output in result.specialist_outputs 
                    if output.success
                ]),
                "vector_updates_count": len(result.vector_store_updates)
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro no processamento da ação: {str(e)}"
        )


@router.get("/status", response_model=AgentStatusResponse)
async def get_agent_status(
    multiagent_service: MultiAgentService = Depends()
) -> AgentStatusResponse:
    """
    Retorna o status atual do sistema multiagente.
    
    Útil para verificar se todos os agentes estão funcionando corretamente
    e obter informações sobre a última execução.
    """
    
    try:
        status_info = await multiagent_service.get_system_status()
        
        return AgentStatusResponse(
            available_agents=status_info["available_agents"],
            system_status=status_info["status"],
            last_execution=status_info.get("last_execution")
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao obter status do sistema: {str(e)}"
        )


@router.get("/graph-visualization", response_model=GraphVisualizationResponse)
async def get_graph_visualization(
    current_user: User = Depends(get_current_user)
) -> GraphVisualizationResponse:
    """
    Retorna a visualização do grafo multiagente em formato Mermaid.
    
    Endpoint útil para debug e compreensão do fluxo do sistema.
    Requer autenticação para evitar exposição desnecessária da arquitetura.
    """
    
    try:
        # Cria instância temporária do grafo para visualização
        graph = MultiAgentGraph()
        mermaid_diagram = graph.get_graph_visualization()
        
        # Conta nós e arestas (estimativa básica)
        nodes_count = mermaid_diagram.count("-->") + 1 if "-->" in mermaid_diagram else 3
        edges_count = mermaid_diagram.count("-->")
        
        return GraphVisualizationResponse(
            mermaid_diagram=mermaid_diagram,
            nodes_count=nodes_count,
            edges_count=edges_count
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao gerar visualização do grafo: {str(e)}"
        )


@router.post("/test-agent/{agent_name}")
async def test_individual_agent(
    agent_name: str,
    request: ActionRequest,
    current_user: User = Depends(get_current_user),
    multiagent_service: MultiAgentService = Depends()
) -> dict:
    """
    Testa um agente especialista individual.
    
    Endpoint de debug para testar agentes específicos isoladamente.
    Útil para desenvolvimento e troubleshooting.
    """
    
    available_agents = [
        "world", "character", "mission", "rules", 
        "time", "items", "plot", "social"
    ]
    
    if agent_name not in available_agents:
        raise HTTPException(
            status_code=400,
            detail=f"Agente '{agent_name}' não encontrado. Disponíveis: {available_agents}"
        )
    
    try:
        result = await multiagent_service.test_individual_agent(
            agent_name=agent_name,
            user_input=request.action,
            world_context=request.world_context or {}
        )
        
        return {
            "agent_name": agent_name,
            "success": result.success,
            "content": result.content,
            "content_type": result.content_type,
            "metadata": result.metadata,
            "error_message": result.error_message if not result.success else None
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao testar agente {agent_name}: {str(e)}"
        )


@router.get("/execution-history")
async def get_execution_history(
    limit: int = 10,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    multiagent_service: MultiAgentService = Depends()
) -> dict:
    """
    Retorna o histórico de execuções do sistema multiagente para o usuário.
    
    Útil para análise de performance e debug de problemas recorrentes.
    """
    
    try:
        history = await multiagent_service.get_execution_history(
            user_id=current_user.id,
            limit=limit,
            offset=offset
        )
        
        return {
            "executions": history,
            "total_count": len(history),
            "limit": limit,
            "offset": offset
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao obter histórico de execuções: {str(e)}"
        )


@router.post("/clear-cache")
async def clear_agent_cache(
    current_user: User = Depends(get_current_user),
    multiagent_service: MultiAgentService = Depends()
) -> dict:
    """
    Limpa o cache do sistema multiagente para o usuário.
    
    Útil quando há mudanças significativas no contexto do mundo
    ou quando se deseja forçar uma re-avaliação completa.
    """
    
    try:
        cleared_items = await multiagent_service.clear_user_cache(current_user.id)
        
        return {
            "success": True,
            "message": "Cache limpo com sucesso",
            "cleared_items": cleared_items
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao limpar cache: {str(e)}"
        )