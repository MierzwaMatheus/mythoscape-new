"""
Agente especialista em personagem - gerencia dados do personagem, vitalidade e inventário.
"""

from typing import Optional
from app.agents.specialists.base_agent import BaseSpecialistAgent
from app.agents.graph_state import SpecialistOutput
from app.utils.env import get_env_var


class CharacterAgent(BaseSpecialistAgent):
    """Agente especialista responsável pelos dados do personagem."""
    
    def __init__(self):
        super().__init__("character")
    
    def _get_system_prompt(self) -> str:
        """Retorna o prompt de sistema específico do agente de personagem."""
        return get_env_var("AGENT_CHARACTER_PROMPT")
    
    async def process_request(
        self, 
        user_input: str, 
        instructions: str, 
        context: dict
    ) -> SpecialistOutput:
        """Processa requisições relacionadas ao personagem."""
        
        try:
            # Busca dados do personagem
            character_data = await self._get_character_data(context)
            enhanced_context = {**context, "character_data": character_data}
            
            # Chama o LLM para processar a requisição
            response = await self._call_llm(user_input, instructions, enhanced_context)
            
            # Analisa se houve mudanças no personagem
            character_changes = self._analyze_character_changes(user_input, response)
            
            # Extrai IDs relevantes
            referenced_ids = {}
            if character_data:
                referenced_ids["character"] = character_data.get("id", "")
            
            metadata = {
                "character_changes": character_changes,
                "vitality_affected": self._is_vitality_affected(user_input),
                "inventory_affected": self._is_inventory_affected(user_input)
            }
            
            return self._create_success_output(
                content=response,
                content_type="character_action",
                referenced_ids=referenced_ids,
                metadata=metadata
            )
            
        except Exception as e:
            return self._create_error_output(f"Erro no agente de personagem: {str(e)}")
    
    async def _get_character_data(self, context: dict) -> Optional[dict]:
        """Busca dados do personagem."""
        character_id = context.get('character_id')
        if not character_id:
            return None
        
        # TODO: Implementar busca real no banco de dados
        # Por enquanto, retorna dados mock
        return {
            "id": character_id,
            "name": "Personagem Exemplo",
            "concept": "Guerreiro Corajoso",
            "vitality": 3,
            "archetypes": ["Atlético", "Corajoso"],
            "approaches": ["Força", "Determinação"],
            "inventory": ["Espada", "Escudo", "Poção de Cura"]
        }
    
    def _analyze_character_changes(self, user_input: str, response: str) -> dict:
        """Analisa mudanças no personagem baseadas na entrada e resposta."""
        changes = {
            "vitality_change": 0,
            "inventory_changes": [],
            "status_effects": []
        }
        
        input_lower = user_input.lower()
        
        # Detecta possíveis mudanças na vitalidade
        if any(word in input_lower for word in ["atacar", "lutar", "ferimento", "dano"]):
            changes["vitality_change"] = -1
        elif any(word in input_lower for word in ["curar", "descansar", "recuperar"]):
            changes["vitality_change"] = 1
        
        # Detecta mudanças no inventário
        if any(word in input_lower for word in ["pegar", "coletar", "encontrar"]):
            changes["inventory_changes"].append("item_added")
        elif any(word in input_lower for word in ["usar", "consumir", "gastar"]):
            changes["inventory_changes"].append("item_used")
        
        return changes
    
    def _is_vitality_affected(self, user_input: str) -> bool:
        """Verifica se a vitalidade pode ser afetada."""
        vitality_keywords = [
            "atacar", "lutar", "ferimento", "dano", "curar", "descansar", 
            "recuperar", "machucado", "ferido", "cansado"
        ]
        return any(keyword in user_input.lower() for keyword in vitality_keywords)
    
    def _is_inventory_affected(self, user_input: str) -> bool:
        """Verifica se o inventário pode ser afetado."""
        inventory_keywords = [
            "pegar", "coletar", "encontrar", "usar", "consumir", "gastar",
            "equipar", "guardar", "dropar", "vender", "comprar"
        ]
        return any(keyword in user_input.lower() for keyword in inventory_keywords)