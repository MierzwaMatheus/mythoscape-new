"""
Agente especialista em regras - gerencia mecânicas de jogo, testes de dados e sistema SAA.
"""

from typing import Optional
from app.agents.specialists.base_agent import BaseSpecialistAgent
from app.agents.graph_state import SpecialistOutput
from app.utils.env import get_env_var
import random


class RulesAgent(BaseSpecialistAgent):
    """Agente especialista responsável pelas regras e mecânicas do jogo."""
    
    def __init__(self):
        super().__init__("rules")
    
    def _get_system_prompt(self) -> str:
        """Retorna o prompt de sistema específico do agente de regras."""
        return get_env_var("AGENT_RULES_PROMPT")
    
    async def process_request(
        self, 
        user_input: str, 
        instructions: str, 
        context: dict
    ) -> SpecialistOutput:
        """Processa requisições relacionadas às regras do jogo."""
        
        try:
            # Analisa se precisa de teste de dados
            dice_test_needed = self._needs_dice_test(user_input)
            
            # Busca dados do personagem para SAA
            character_data = context.get('character_data', {})
            
            # Processa teste de dados se necessário
            dice_result = None
            if dice_test_needed:
                dice_result = self._perform_dice_test(user_input, character_data)
            
            # Prepara contexto com regras
            rules_context = {
                **context,
                "dice_result": dice_result,
                "saa_system": self._get_saa_context(character_data)
            }
            
            # Chama o LLM para processar a requisição
            response = await self._call_llm(user_input, instructions, rules_context)
            
            # Analisa consequências das regras
            rule_consequences = self._analyze_rule_consequences(user_input, dice_result)
            
            metadata = {
                "dice_test_performed": dice_test_needed,
                "dice_result": dice_result,
                "rule_consequences": rule_consequences,
                "difficulty_level": self._assess_difficulty(user_input)
            }
            
            return self._create_success_output(
                content=response,
                content_type="rules_application",
                referenced_ids={},
                metadata=metadata
            )
            
        except Exception as e:
            return self._create_error_output(f"Erro no agente de regras: {str(e)}")
    
    def _needs_dice_test(self, user_input: str) -> bool:
        """Determina se a ação requer um teste de dados."""
        test_keywords = [
            "tentar", "atacar", "saltar", "escalar", "convencer", "enganar",
            "investigar", "procurar", "forçar", "quebrar", "abrir", "hackear",
            "persuadir", "intimidar", "esconder", "fugir", "correr", "lutar"
        ]
        
        input_lower = user_input.lower()
        return any(keyword in input_lower for keyword in test_keywords)
    
    def _perform_dice_test(self, user_input: str, character_data: dict) -> dict:
        """Executa um teste de dados usando o sistema SAA."""
        # Determina a dificuldade base
        difficulty = self._determine_difficulty(user_input)
        
        # Seleciona arquétipo e abordagem relevantes
        relevant_archetype = self._select_relevant_archetype(user_input, character_data)
        relevant_approach = self._select_relevant_approach(user_input, character_data)
        
        # Rola os dados (4dF - Fate Dice)
        dice_roll = sum(random.choice([-1, -1, 0, 0, 1, 1]) for _ in range(4))
        
        # Calcula modificadores
        archetype_bonus = 2 if relevant_archetype else 0
        approach_bonus = 2 if relevant_approach else 0
        
        # Resultado final
        total_result = dice_roll + archetype_bonus + approach_bonus
        success = total_result >= difficulty
        
        return {
            "dice_roll": dice_roll,
            "archetype_used": relevant_archetype,
            "approach_used": relevant_approach,
            "archetype_bonus": archetype_bonus,
            "approach_bonus": approach_bonus,
            "total_result": total_result,
            "difficulty": difficulty,
            "success": success,
            "margin": total_result - difficulty
        }
    
    def _determine_difficulty(self, user_input: str) -> int:
        """Determina a dificuldade da ação baseada na entrada."""
        input_lower = user_input.lower()
        
        # Ações muito difíceis
        if any(word in input_lower for word in ["impossível", "épico", "lendário"]):
            return 4
        
        # Ações difíceis
        elif any(word in input_lower for word in ["difícil", "complicado", "perigoso"]):
            return 3
        
        # Ações moderadas
        elif any(word in input_lower for word in ["moderado", "normal", "padrão"]):
            return 2
        
        # Ações fáceis
        elif any(word in input_lower for word in ["fácil", "simples", "básico"]):
            return 1
        
        # Dificuldade padrão
        return 2
    
    def _select_relevant_archetype(self, user_input: str, character_data: dict) -> Optional[str]:
        """Seleciona o arquétipo mais relevante para a ação."""
        archetypes = character_data.get('archetypes', [])
        if not archetypes:
            return None
        
        input_lower = user_input.lower()
        
        # Mapeamento de palavras-chave para arquétipos comuns
        archetype_keywords = {
            "atlético": ["correr", "saltar", "escalar", "nadar", "força"],
            "corajoso": ["atacar", "enfrentar", "proteger", "lutar"],
            "inteligente": ["investigar", "analisar", "resolver", "estudar"],
            "carismático": ["convencer", "persuadir", "liderar", "negociar"],
            "furtivo": ["esconder", "esgueirar", "roubar", "espionar"]
        }
        
        # Verifica qual arquétipo é mais relevante
        for archetype in archetypes:
            archetype_lower = archetype.lower()
            if archetype_lower in archetype_keywords:
                keywords = archetype_keywords[archetype_lower]
                if any(keyword in input_lower for keyword in keywords):
                    return archetype
        
        # Retorna o primeiro arquétipo se nenhum for específico
        return archetypes[0] if archetypes else None
    
    def _select_relevant_approach(self, user_input: str, character_data: dict) -> Optional[str]:
        """Seleciona a abordagem mais relevante para a ação."""
        approaches = character_data.get('approaches', [])
        if not approaches:
            return None
        
        input_lower = user_input.lower()
        
        # Mapeamento de palavras-chave para abordagens comuns
        approach_keywords = {
            "força": ["forçar", "quebrar", "empurrar", "destruir"],
            "agilidade": ["esquivar", "correr", "saltar", "rápido"],
            "intelecto": ["pensar", "analisar", "calcular", "estudar"],
            "percepção": ["observar", "notar", "procurar", "ver"],
            "vontade": ["resistir", "concentrar", "focar", "determinar"],
            "presença": ["impressionar", "liderar", "comandar", "inspirar"]
        }
        
        # Verifica qual abordagem é mais relevante
        for approach in approaches:
            approach_lower = approach.lower()
            if approach_lower in approach_keywords:
                keywords = approach_keywords[approach_lower]
                if any(keyword in input_lower for keyword in keywords):
                    return approach
        
        # Retorna a primeira abordagem se nenhuma for específica
        return approaches[0] if approaches else None
    
    def _get_saa_context(self, character_data: dict) -> dict:
        """Prepara contexto do sistema SAA."""
        return {
            "archetypes": character_data.get('archetypes', []),
            "approaches": character_data.get('approaches', []),
            "vitality": character_data.get('vitality', 3)
        }
    
    def _analyze_rule_consequences(self, user_input: str, dice_result: Optional[dict]) -> dict:
        """Analisa as consequências da aplicação das regras."""
        consequences = {
            "success_level": "none",
            "narrative_impact": "low",
            "mechanical_effects": []
        }
        
        if dice_result:
            margin = dice_result.get('margin', 0)
            
            if margin >= 3:
                consequences["success_level"] = "critical_success"
                consequences["narrative_impact"] = "high"
                consequences["mechanical_effects"].append("bonus_outcome")
            elif margin >= 0:
                consequences["success_level"] = "success"
                consequences["narrative_impact"] = "medium"
            elif margin >= -2:
                consequences["success_level"] = "partial_success"
                consequences["narrative_impact"] = "medium"
                consequences["mechanical_effects"].append("complication")
            else:
                consequences["success_level"] = "failure"
                consequences["narrative_impact"] = "high"
                consequences["mechanical_effects"].append("consequence")
        
        return consequences
    
    def _assess_difficulty(self, user_input: str) -> str:
        """Avalia o nível de dificuldade da ação."""
        input_lower = user_input.lower()
        
        if any(word in input_lower for word in ["impossível", "épico", "lendário"]):
            return "legendary"
        elif any(word in input_lower for word in ["muito difícil", "extremo"]):
            return "epic"
        elif any(word in input_lower for word in ["difícil", "complicado"]):
            return "hard"
        elif any(word in input_lower for word in ["moderado", "normal"]):
            return "moderate"
        elif any(word in input_lower for word in ["fácil", "simples"]):
            return "easy"
        else:
            return "moderate"