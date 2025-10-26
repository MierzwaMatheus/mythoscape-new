"""
Agente Roteador do sistema multiagente.
Analisa a entrada do usuário e determina quais agentes especialistas devem ser acionados.
"""

import os
from typing import Union
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from app.agents.routing_tools import ROUTING_TOOLS
from app.utils.env import get_env_var


class RouterAgent:
    """Agente responsável por rotear requisições para agentes especialistas."""
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.1,  # Baixa temperatura para decisões mais consistentes
            api_key=get_env_var("OPENAI_API_KEY")
        )
        self.router_prompt = get_env_var("AGENT_ROUTER_PROMPT")
        
        # Configura o LLM com structured output para as ferramentas de roteamento
        self.router_agent = self.llm.with_structured_output(
            Union[tuple(ROUTING_TOOLS)]
        )
    
    async def route_request(self, user_input: str, world_context: dict = None) -> list[dict]:
        """
        Analisa a entrada do usuário e retorna lista de agentes especialistas necessários.
        
        Args:
            user_input: Entrada do usuário
            world_context: Contexto do mundo atual (opcional)
            
        Returns:
            Lista de dicionários com agente e instruções específicas
        """
        
        # Prepara o contexto adicional se disponível
        context_info = ""
        if world_context:
            context_info = f"""
            
CONTEXTO DO MUNDO ATUAL:
- ID do Mundo: {world_context.get('world_id', 'N/A')}
- Nome: {world_context.get('name', 'N/A')}
- Gênero: {world_context.get('genre_tags', [])}
- Personalidade do Mestre: {world_context.get('master_personality', 'N/A')}
"""
        
        # Monta o prompt completo
        full_prompt = f"""
{self.router_prompt}

{context_info}

ENTRADA DO USUÁRIO: "{user_input}"

Analise cuidadosamente a entrada e determine quais agentes especialistas são necessários.
Retorne APENAS os agentes que são realmente relevantes para processar esta entrada específica.
"""
        
        try:
            # Chama o LLM para classificar
            messages = [
                SystemMessage(content=full_prompt),
                HumanMessage(content=user_input)
            ]
            
            result = await self.router_agent.ainvoke(messages)
            
            # Converte o resultado para formato padronizado
            if not isinstance(result, list):
                result = [result]
            
            routed_agents = []
            for agent_tool in result:
                agent_name = agent_tool.__class__.__name__.replace("ExpertTool", "").lower()
                routed_agents.append({
                    "agent": agent_name,
                    "instructions": agent_tool.instructions,
                    "tool_class": agent_tool.__class__.__name__
                })
            
            return routed_agents
            
        except Exception as e:
            # Fallback: se houver erro, roteia para agentes básicos
            print(f"Erro no roteamento: {e}")
            return [
                {
                    "agent": "world",
                    "instructions": "Processar entrada do usuário com contexto do mundo",
                    "tool_class": "WorldExpertTool"
                }
            ]
    
    def get_available_agents(self) -> list[str]:
        """Retorna lista de agentes especialistas disponíveis."""
        return [tool.__name__.replace("ExpertTool", "").lower() for tool in ROUTING_TOOLS]