"""
Grafo principal do sistema multiagente usando LangGraph.
"""

import asyncio
from typing import Optional
from datetime import datetime
from langgraph.graph import StateGraph, END
from langchain_core.runnables import RunnableConfig

from app.agents.graph_state import AgentState, SpecialistOutput, VectorStoreUpdate
from app.agents.router import RouterAgent
from app.agents.synthesizer import SynthesizerAgent
from app.agents.specialists import (
    WorldAgent, CharacterAgent, MissionAgent, RulesAgent,
    TimeAgent, ItemsAgent, PlotAgent, SocialAgent
)


class MultiAgentGraph:
    """Grafo principal que orquestra o sistema multiagente."""
    
    def __init__(self):
        self.router = RouterAgent()
        self.synthesizer = SynthesizerAgent()
        
        # Inicializa agentes especialistas
        self.specialists = {
            "world": WorldAgent(),
            "character": CharacterAgent(),
            "mission": MissionAgent(),
            "rules": RulesAgent(),
            "time": TimeAgent(),
            "items": ItemsAgent(),
            "plot": PlotAgent(),
            "social": SocialAgent()
        }
        
        # Constrói o grafo
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Constrói o grafo de estados do sistema multiagente."""
        
        # Define o grafo com o estado
        workflow = StateGraph(AgentState)
        
        # Adiciona nós
        workflow.add_node("router", self._router_node)
        workflow.add_node("specialists", self._specialists_node)
        workflow.add_node("synthesizer", self._synthesizer_node)
        
        # Define o fluxo
        workflow.set_entry_point("router")
        workflow.add_edge("router", "specialists")
        workflow.add_edge("specialists", "synthesizer")
        workflow.add_edge("synthesizer", END)
        
        return workflow.compile()
    
    async def _router_node(self, state: AgentState) -> dict:
        """Nó do roteador - classifica e seleciona agentes."""
        start_time = datetime.now()
        
        try:
            # Executa roteamento
            selected_agents = await self.router.route_request(
                state.user_input, 
                state.world_context
            )
            
            # Atualiza estado
            execution_time = (datetime.now() - start_time).total_seconds()
            
            return {
                "selected_agents": selected_agents,
                "execution_metadata": {
                    **state.execution_metadata,
                    "router_execution_time": execution_time,
                    "router_success": True
                }
            }
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            
            # Fallback para agente world em caso de erro
            return {
                "selected_agents": ["world"],
                "execution_metadata": {
                    **state.execution_metadata,
                    "router_execution_time": execution_time,
                    "router_success": False,
                    "router_error": str(e)
                }
            }
    
    async def _specialists_node(self, state: AgentState) -> dict:
        """Nó dos especialistas - executa agentes selecionados em paralelo."""
        start_time = datetime.now()
        
        try:
            # Executa agentes especialistas em paralelo
            specialist_tasks = []
            
            for agent_name in state.selected_agents:
                if agent_name in self.specialists:
                    task = self._execute_specialist(
                        agent_name, 
                        state.user_input, 
                        state.world_context
                    )
                    specialist_tasks.append(task)
            
            # Aguarda todas as execuções
            specialist_results = await asyncio.gather(*specialist_tasks, return_exceptions=True)
            
            # Processa resultados
            specialist_outputs = []
            vector_store_updates = []
            
            for i, result in enumerate(specialist_results):
                agent_name = state.selected_agents[i] if i < len(state.selected_agents) else "unknown"
                
                if isinstance(result, Exception):
                    # Cria saída de erro
                    error_output = SpecialistOutput(
                        agent_type=agent_name,
                        content="",
                        content_type="error",
                        success=False,
                        error_message=str(result),
                        metadata={}
                    )
                    specialist_outputs.append(error_output)
                else:
                    specialist_outputs.append(result)
                    
                    # Extrai atualizações do vector store se existirem
                    if result.metadata and result.metadata.get("vector_store_updates"):
                        updates = result.metadata["vector_store_updates"]
                        if isinstance(updates, list):
                            vector_store_updates.extend(updates)
                        else:
                            vector_store_updates.append(updates)
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            return {
                "specialist_outputs": specialist_outputs,
                "vector_store_updates": vector_store_updates,
                "execution_metadata": {
                    **state.execution_metadata,
                    "specialists_execution_time": execution_time,
                    "specialists_success": True,
                    "total_specialists_executed": len(specialist_outputs)
                }
            }
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            
            # Cria saída de erro genérica
            error_output = SpecialistOutput(
                agent_type="system",
                content="Erro interno no processamento dos agentes especialistas.",
                content_type="error",
                success=False,
                error_message=str(e),
                metadata={}
            )
            
            return {
                "specialist_outputs": [error_output],
                "vector_store_updates": [],
                "execution_metadata": {
                    **state.execution_metadata,
                    "specialists_execution_time": execution_time,
                    "specialists_success": False,
                    "specialists_error": str(e)
                }
            }
    
    async def _synthesizer_node(self, state: AgentState) -> dict:
        """Nó do sintetizador - combina saídas em narrativa final."""
        start_time = datetime.now()
        
        try:
            # Sintetiza as saídas
            final_narrative = await self.synthesizer.synthesize_outputs(state)
            
            execution_time = (datetime.now() - start_time).total_seconds()
            total_execution_time = (datetime.now() - state.execution_metadata.get("start_time", start_time)).total_seconds()
            
            return {
                "final_narrative": final_narrative,
                "execution_duration": total_execution_time,
                "execution_metadata": {
                    **state.execution_metadata,
                    "synthesizer_execution_time": execution_time,
                    "synthesizer_success": True,
                    "total_execution_time": total_execution_time,
                    "end_time": datetime.now()
                }
            }
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            total_execution_time = (datetime.now() - state.execution_metadata.get("start_time", start_time)).total_seconds()
            
            # Fallback para narrativa básica
            fallback_narrative = self._create_fallback_narrative(state.specialist_outputs)
            
            return {
                "final_narrative": fallback_narrative,
                "execution_duration": total_execution_time,
                "execution_metadata": {
                    **state.execution_metadata,
                    "synthesizer_execution_time": execution_time,
                    "synthesizer_success": False,
                    "synthesizer_error": str(e),
                    "total_execution_time": total_execution_time,
                    "end_time": datetime.now()
                }
            }
    
    async def _execute_specialist(
        self, 
        agent_name: str, 
        user_input: str, 
        world_context: dict
    ) -> SpecialistOutput:
        """Executa um agente especialista específico."""
        
        try:
            specialist = self.specialists[agent_name]
            return await specialist.process_request(user_input, world_context)
            
        except Exception as e:
            return SpecialistOutput(
                agent_type=agent_name,
                content="",
                content_type="error",
                success=False,
                error_message=f"Erro na execução do agente {agent_name}: {str(e)}",
                metadata={}
            )
    
    def _create_fallback_narrative(self, specialist_outputs: list[SpecialistOutput]) -> str:
        """Cria uma narrativa de fallback quando o sintetizador falha."""
        
        successful_outputs = [output for output in specialist_outputs if output.success]
        
        if not successful_outputs:
            return "Algo inesperado aconteceu durante o processamento de sua ação."
        
        # Combina conteúdos de forma simples
        contents = []
        for output in successful_outputs:
            if output.content and output.content.strip():
                contents.append(output.content.strip())
        
        if contents:
            return " ".join(contents)
        else:
            return "Sua ação foi processada com sucesso."
    
    async def process_user_input(
        self, 
        user_input: str, 
        world_context: dict,
        config: Optional[RunnableConfig] = None
    ) -> AgentState:
        """Processa entrada do usuário através do sistema multiagente."""
        
        # Cria estado inicial
        initial_state = AgentState(
            user_input=user_input,
            world_context=world_context,
            selected_agents=[],
            specialist_outputs=[],
            final_narrative="",
            execution_duration=0.0,
            vector_store_updates=[],
            execution_metadata={
                "start_time": datetime.now(),
                "user_input_length": len(user_input),
                "world_context_size": len(str(world_context))
            }
        )
        
        # Executa o grafo
        try:
            final_state = await self.graph.ainvoke(initial_state, config=config)
            return final_state
            
        except Exception as e:
            # Estado de erro
            error_state = initial_state.copy()
            error_state.final_narrative = f"Erro no processamento: {str(e)}"
            error_state.execution_duration = (datetime.now() - initial_state.execution_metadata["start_time"]).total_seconds()
            error_state.execution_metadata["system_error"] = str(e)
            
            return error_state
    
    def get_graph_visualization(self) -> str:
        """Retorna uma representação visual do grafo para debug."""
        try:
            return self.graph.get_graph().draw_mermaid()
        except Exception:
            return "Visualização do grafo não disponível"