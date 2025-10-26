"""
Agente especialista em plot - gerencia narrativa, plot twists e desenvolvimento da história.
"""

from typing import Optional
from app.agents.specialists.base_agent import BaseSpecialistAgent
from app.agents.graph_state import SpecialistOutput
from app.utils.env import get_env_var


class PlotAgent(BaseSpecialistAgent):
    """Agente especialista responsável pela narrativa e desenvolvimento do plot."""
    
    def __init__(self):
        super().__init__("plot")
    
    def _get_system_prompt(self) -> str:
        """Retorna o prompt de sistema específico do agente de plot."""
        return get_env_var("AGENT_PLOT_PROMPT")
    
    async def process_request(
        self, 
        user_input: str, 
        instructions: str, 
        context: dict
    ) -> SpecialistOutput:
        """Processa requisições relacionadas ao desenvolvimento narrativo."""
        
        try:
            # Analisa o contexto narrativo atual
            narrative_context = await self._analyze_narrative_context(context)
            
            # Verifica oportunidades de plot twist
            plot_opportunities = self._identify_plot_opportunities(user_input, context)
            
            # Avalia tensão dramática
            dramatic_tension = self._assess_dramatic_tension(user_input, narrative_context)
            
            # Prepara contexto narrativo
            plot_context = {
                **context,
                "narrative_context": narrative_context,
                "plot_opportunities": plot_opportunities,
                "dramatic_tension": dramatic_tension
            }
            
            # Chama o LLM para processar a requisição
            response = await self._call_llm(user_input, instructions, plot_context)
            
            # Analisa impacto narrativo
            narrative_impact = self._analyze_narrative_impact(user_input, response)
            
            # Gera hooks para futuros desenvolvimentos
            future_hooks = self._generate_future_hooks(response, context)
            
            metadata = {
                "narrative_impact": narrative_impact,
                "plot_twist_potential": len(plot_opportunities),
                "dramatic_tension_level": dramatic_tension["level"],
                "future_hooks": future_hooks,
                "story_arc_progression": self._assess_story_progression(context)
            }
            
            return self._create_success_output(
                content=response,
                content_type="narrative_development",
                referenced_ids={},
                metadata=metadata
            )
            
        except Exception as e:
            return self._create_error_output(f"Erro no agente de plot: {str(e)}")
    
    async def _analyze_narrative_context(self, context: dict) -> dict:
        """Analisa o contexto narrativo atual."""
        # TODO: Implementar análise real do histórico narrativo
        # Por enquanto, retorna contexto mock
        return {
            "current_arc": "A Busca pelo Artefato",
            "act": 2,
            "tension_level": "rising",
            "key_npcs": ["Sábio Eldrin", "Mercador Suspicious"],
            "unresolved_mysteries": ["Origem do artefato", "Identidade do antagonista"],
            "recent_events": ["Encontro com o sábio", "Descoberta da pista"],
            "character_development_stage": "growth"
        }
    
    def _identify_plot_opportunities(self, user_input: str, context: dict) -> list[dict]:
        """Identifica oportunidades para desenvolvimento do plot."""
        opportunities = []
        input_lower = user_input.lower()
        
        # Oportunidades baseadas em ações do jogador
        if any(word in input_lower for word in ["investigar", "procurar", "descobrir"]):
            opportunities.append({
                "type": "revelation",
                "description": "Oportunidade para revelar informação importante",
                "impact": "medium",
                "timing": "immediate"
            })
        
        if any(word in input_lower for word in ["confrontar", "enfrentar", "desafiar"]):
            opportunities.append({
                "type": "conflict_escalation",
                "description": "Momento para escalar o conflito",
                "impact": "high",
                "timing": "immediate"
            })
        
        if any(word in input_lower for word in ["conversar", "questionar", "perguntar"]):
            opportunities.append({
                "type": "character_development",
                "description": "Chance de desenvolver personagens",
                "impact": "medium",
                "timing": "gradual"
            })
        
        # Oportunidades baseadas no contexto
        narrative_context = context.get('narrative_context', {})
        if narrative_context.get('tension_level') == 'rising':
            opportunities.append({
                "type": "climax_preparation",
                "description": "Preparação para o clímax do arco",
                "impact": "high",
                "timing": "delayed"
            })
        
        return opportunities
    
    def _assess_dramatic_tension(self, user_input: str, narrative_context: dict) -> dict:
        """Avalia o nível de tensão dramática."""
        base_tension = narrative_context.get('tension_level', 'low')
        
        # Fatores que aumentam a tensão
        tension_increasers = [
            "perigo", "ameaça", "urgente", "rápido", "escapar", "fugir",
            "atacar", "lutar", "confrontar", "desafiar"
        ]
        
        # Fatores que diminuem a tensão
        tension_decreasers = [
            "descansar", "relaxar", "conversar", "explorar", "investigar",
            "estudar", "planejar", "preparar"
        ]
        
        input_lower = user_input.lower()
        
        # Calcula modificador de tensão
        tension_modifier = 0
        for word in tension_increasers:
            if word in input_lower:
                tension_modifier += 1
        
        for word in tension_decreasers:
            if word in input_lower:
                tension_modifier -= 1
        
        # Mapeia níveis de tensão
        tension_levels = ["low", "building", "rising", "high", "climactic"]
        current_index = tension_levels.index(base_tension) if base_tension in tension_levels else 1
        
        new_index = max(0, min(len(tension_levels) - 1, current_index + tension_modifier))
        new_level = tension_levels[new_index]
        
        return {
            "level": new_level,
            "modifier": tension_modifier,
            "description": self._get_tension_description(new_level)
        }
    
    def _get_tension_description(self, level: str) -> str:
        """Retorna descrição do nível de tensão."""
        descriptions = {
            "low": "Momento calmo, propício para exploração e desenvolvimento",
            "building": "Tensão começando a se formar, sinais de conflito",
            "rising": "Tensão crescente, obstáculos se apresentando",
            "high": "Alta tensão, conflito iminente ou em andamento",
            "climactic": "Momento climático, resolução de conflitos principais"
        }
        return descriptions.get(level, "Tensão indefinida")
    
    def _analyze_narrative_impact(self, user_input: str, response: str) -> dict:
        """Analisa o impacto narrativo da ação e resposta."""
        impact = {
            "scope": "local",  # local, regional, global
            "permanence": "temporary",  # temporary, lasting, permanent
            "character_growth": False,
            "world_change": False,
            "relationship_change": False
        }
        
        input_lower = user_input.lower()
        response_lower = response.lower()
        
        # Analisa escopo do impacto
        if any(word in input_lower for word in ["mundo", "reino", "todos", "guerra"]):
            impact["scope"] = "global"
        elif any(word in input_lower for word in ["cidade", "região", "área", "local"]):
            impact["scope"] = "regional"
        
        # Analisa permanência
        if any(word in input_lower for word in ["destruir", "matar", "criar", "construir"]):
            impact["permanence"] = "permanent"
        elif any(word in input_lower for word in ["mudar", "alterar", "modificar"]):
            impact["permanence"] = "lasting"
        
        # Verifica crescimento do personagem
        growth_indicators = ["aprender", "descobrir", "compreender", "realizar"]
        impact["character_growth"] = any(word in response_lower for word in growth_indicators)
        
        # Verifica mudanças no mundo
        world_change_indicators = ["transformar", "alterar", "modificar", "afetar"]
        impact["world_change"] = any(word in response_lower for word in world_change_indicators)
        
        # Verifica mudanças em relacionamentos
        relationship_indicators = ["confiança", "amizade", "inimizade", "aliança"]
        impact["relationship_change"] = any(word in response_lower for word in relationship_indicators)
        
        return impact
    
    def _generate_future_hooks(self, response: str, context: dict) -> list[str]:
        """Gera ganchos para desenvolvimentos futuros da narrativa."""
        hooks = []
        
        # Hooks baseados na resposta
        response_lower = response.lower()
        
        if "mistério" in response_lower or "segredo" in response_lower:
            hooks.append("Um mistério foi mencionado que pode ser explorado")
        
        if "npc" in response_lower or "personagem" in response_lower:
            hooks.append("Novo personagem introduzido com potencial para desenvolvimento")
        
        if "local" in response_lower or "lugar" in response_lower:
            hooks.append("Novo local mencionado que pode ser visitado")
        
        if "conflito" in response_lower or "problema" in response_lower:
            hooks.append("Conflito estabelecido que precisa de resolução")
        
        # Hooks baseados no contexto narrativo
        narrative_context = context.get('narrative_context', {})
        unresolved_mysteries = narrative_context.get('unresolved_mysteries', [])
        
        for mystery in unresolved_mysteries[:2]:  # Limita a 2 mistérios
            hooks.append(f"Mistério não resolvido: {mystery}")
        
        return hooks[:5]  # Limita a 5 hooks
    
    def _assess_story_progression(self, context: dict) -> str:
        """Avalia a progressão do arco narrativo."""
        narrative_context = context.get('narrative_context', {})
        current_act = narrative_context.get('act', 1)
        tension_level = narrative_context.get('tension_level', 'low')
        
        if current_act == 1:
            if tension_level in ['low', 'building']:
                return "setup_phase"
            else:
                return "inciting_incident"
        elif current_act == 2:
            if tension_level in ['building', 'rising']:
                return "rising_action"
            else:
                return "midpoint_crisis"
        else:  # act 3
            if tension_level == 'climactic':
                return "climax"
            elif tension_level == 'high':
                return "falling_action"
            else:
                return "resolution"