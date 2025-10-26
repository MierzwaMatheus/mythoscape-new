"""
Classe base para agentes especialistas do sistema multiagente.
"""

from abc import ABC, abstractmethod
from typing import Optional
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from app.agents.graph_state import SpecialistOutput
from app.utils.env import get_env_var


class BaseSpecialistAgent(ABC):
    """Classe base para todos os agentes especialistas."""
    
    def __init__(self, agent_type: str):
        self.agent_type = agent_type
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.7,  # Temperatura moderada para criatividade controlada
            api_key=get_env_var("OPENAI_API_KEY")
        )
        self.system_prompt = self._get_system_prompt()
    
    @abstractmethod
    def _get_system_prompt(self) -> str:
        """Retorna o prompt de sistema específico do agente."""
        pass
    
    @abstractmethod
    async def process_request(
        self, 
        user_input: str, 
        instructions: str, 
        context: dict
    ) -> SpecialistOutput:
        """Processa uma requisição específica do agente."""
        pass
    
    async def _call_llm(
        self, 
        user_input: str, 
        instructions: str, 
        context: dict
    ) -> str:
        """Chama o LLM com o contexto apropriado."""
        
        # Prepara o contexto
        context_str = self._format_context(context)
        
        # Monta o prompt completo
        full_prompt = f"""
{self.system_prompt}

INSTRUÇÕES ESPECÍFICAS: {instructions}

CONTEXTO ATUAL:
{context_str}

ENTRADA DO USUÁRIO: "{user_input}"

Processe esta entrada de acordo com sua especialidade e as instruções fornecidas.
"""
        
        try:
            messages = [
                SystemMessage(content=full_prompt),
                HumanMessage(content=user_input)
            ]
            
            response = await self.llm.ainvoke(messages)
            return response.content
            
        except Exception as e:
            raise Exception(f"Erro ao chamar LLM para {self.agent_type}: {str(e)}")
    
    def _format_context(self, context: dict) -> str:
        """Formata o contexto para o prompt."""
        formatted_lines = []
        
        if context.get('world_context'):
            world = context['world_context']
            formatted_lines.append(f"MUNDO: {world.get('name', 'N/A')}")
            formatted_lines.append(f"GÊNERO: {', '.join(world.get('genre_tags', []))}")
            formatted_lines.append(f"PERSONALIDADE DO MESTRE: {world.get('master_personality', 'N/A')}")
        
        if context.get('character_data'):
            char = context['character_data']
            formatted_lines.append(f"PERSONAGEM: {char.get('name', 'N/A')}")
            formatted_lines.append(f"CONCEITO: {char.get('concept', 'N/A')}")
            formatted_lines.append(f"VITALIDADE: {char.get('vitality', 'N/A')}")
        
        if context.get('world_id'):
            formatted_lines.append(f"WORLD_ID: {context['world_id']}")
        
        if context.get('user_id'):
            formatted_lines.append(f"USER_ID: {context['user_id']}")
        
        return "\n".join(formatted_lines) if formatted_lines else "Nenhum contexto adicional disponível."
    
    def _create_success_output(
        self, 
        content: str, 
        content_type: str = "response",
        referenced_ids: Optional[dict] = None,
        metadata: Optional[dict] = None
    ) -> SpecialistOutput:
        """Cria uma saída de sucesso padronizada."""
        return SpecialistOutput(
            source_agent=self.agent_type,
            content_type=content_type,
            data=content,
            referenced_ids=referenced_ids or {},
            metadata=metadata,
            success=True,
            error_message=None
        )
    
    def _create_error_output(self, error_message: str) -> SpecialistOutput:
        """Cria uma saída de erro padronizada."""
        return SpecialistOutput(
            source_agent=self.agent_type,
            content_type="error",
            data="",
            referenced_ids={},
            metadata=None,
            success=False,
            error_message=error_message
        )