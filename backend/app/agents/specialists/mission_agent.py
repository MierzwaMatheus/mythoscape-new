"""
Agente especialista em missões - gerencia missões ativas, plot twists e progressão.
"""

from typing import Optional
from app.agents.specialists.base_agent import BaseSpecialistAgent
from app.agents.graph_state import SpecialistOutput
from app.utils.env import get_env_var


class MissionAgent(BaseSpecialistAgent):
    """Agente especialista responsável pelas missões e plot twists."""
    
    def __init__(self):
        super().__init__("mission")
    
    def _get_system_prompt(self) -> str:
        """Retorna o prompt de sistema específico do agente de missões."""
        return get_env_var("AGENT_MISSIONS_PROMPT")
    
    async def process_request(
        self, 
        user_input: str, 
        instructions: str, 
        context: dict
    ) -> SpecialistOutput:
        """Processa requisições relacionadas às missões."""
        
        try:
            # Busca missões ativas
            active_missions = await self._get_active_missions(context)
            enhanced_context = {**context, "active_missions": active_missions}
            
            # Chama o LLM para processar a requisição
            response = await self._call_llm(user_input, instructions, enhanced_context)
            
            # Analisa progressão das missões
            mission_progress = self._analyze_mission_progress(user_input, active_missions)
            
            # Verifica se deve disparar plot twist
            plot_twist_triggered = self._should_trigger_plot_twist(user_input, context)
            
            # Extrai IDs de missões referenciadas
            referenced_ids = {}
            if active_missions:
                for i, mission in enumerate(active_missions[:3]):
                    referenced_ids[f"mission_{i}"] = mission.get("id", "")
            
            metadata = {
                "mission_progress": mission_progress,
                "plot_twist_triggered": plot_twist_triggered,
                "missions_affected": len(mission_progress)
            }
            
            return self._create_success_output(
                content=response,
                content_type="mission_update",
                referenced_ids=referenced_ids,
                metadata=metadata
            )
            
        except Exception as e:
            return self._create_error_output(f"Erro no agente de missões: {str(e)}")
    
    async def _get_active_missions(self, context: dict) -> list[dict]:
        """Busca missões ativas do personagem."""
        character_id = context.get('character_id')
        world_id = context.get('world_id')
        
        if not character_id or not world_id:
            return []
        
        # TODO: Implementar busca real no banco de dados
        # Por enquanto, retorna dados mock
        return [
            {
                "id": "mission_1",
                "name": "Encontrar o Artefato Perdido",
                "description": "Procure pelo artefato antigo na floresta sombria",
                "status": "active",
                "plot_twist_trigger": "encontrar_artefato"
            },
            {
                "id": "mission_2", 
                "name": "Salvar a Aldeia",
                "description": "Proteja os aldeões dos bandidos",
                "status": "active",
                "plot_twist_trigger": "confronto_bandidos"
            }
        ]
    
    def _analyze_mission_progress(self, user_input: str, missions: list[dict]) -> dict:
        """Analisa o progresso das missões baseado na entrada do usuário."""
        progress = {}
        
        if not missions:
            return progress
        
        input_lower = user_input.lower()
        
        for mission in missions:
            mission_id = mission.get("id", "")
            mission_name = mission.get("name", "").lower()
            
            # Verifica palavras-chave relacionadas à missão
            progress_indicators = [
                "completar", "terminar", "finalizar", "conseguir", "alcançar",
                "encontrar", "descobrir", "resolver", "derrotar", "vencer"
            ]
            
            # Verifica se a ação está relacionada à missão
            mission_related = any(word in mission_name for word in input_lower.split())
            action_indicates_progress = any(indicator in input_lower for indicator in progress_indicators)
            
            if mission_related and action_indicates_progress:
                progress[mission_id] = {
                    "status_change": "progressed",
                    "completion_percentage": 75  # Estimativa
                }
            elif mission_related:
                progress[mission_id] = {
                    "status_change": "updated",
                    "completion_percentage": 50
                }
        
        return progress
    
    def _should_trigger_plot_twist(self, user_input: str, context: dict) -> bool:
        """Determina se um plot twist deve ser disparado."""
        # Verifica se há condições especiais no contexto
        twist_triggers = context.get('plot_twist_conditions', [])
        
        input_lower = user_input.lower()
        
        # Palavras-chave que podem disparar plot twists
        twist_keywords = [
            "descobrir", "revelar", "encontrar", "abrir", "ler", "investigar",
            "confrontar", "atacar", "falar com", "questionar"
        ]
        
        # Verifica se alguma palavra-chave está presente
        keyword_present = any(keyword in input_lower for keyword in twist_keywords)
        
        # Verifica condições específicas do contexto
        condition_met = any(condition in input_lower for condition in twist_triggers)
        
        return keyword_present or condition_met