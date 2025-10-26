"""
Agente especialista social - gerencia interações com NPCs, relacionamentos e dinâmicas sociais.
"""

from typing import Optional
from app.agents.specialists.base_agent import BaseSpecialistAgent
from app.agents.graph_state import SpecialistOutput
from app.utils.env import get_env_var


class SocialAgent(BaseSpecialistAgent):
    """Agente especialista responsável por interações sociais e relacionamentos."""
    
    def __init__(self):
        super().__init__("social")
    
    def _get_system_prompt(self) -> str:
        """Retorna o prompt de sistema específico do agente social."""
        return get_env_var("AGENT_SOCIAL_PROMPT")
    
    async def process_request(
        self, 
        user_input: str, 
        instructions: str, 
        context: dict
    ) -> SpecialistOutput:
        """Processa requisições relacionadas a interações sociais."""
        
        try:
            # Identifica NPCs envolvidos
            involved_npcs = self._identify_npcs(user_input, context)
            
            # Analisa tipo de interação social
            interaction_type = self._analyze_interaction_type(user_input)
            
            # Busca relacionamentos existentes
            relationships = await self._get_relationships(context, involved_npcs)
            
            # Calcula modificadores sociais
            social_modifiers = self._calculate_social_modifiers(
                interaction_type, relationships, context
            )
            
            # Prepara contexto social
            social_context = {
                **context,
                "involved_npcs": involved_npcs,
                "interaction_type": interaction_type,
                "relationships": relationships,
                "social_modifiers": social_modifiers
            }
            
            # Chama o LLM para processar a requisição
            response = await self._call_llm(user_input, instructions, social_context)
            
            # Analisa mudanças nos relacionamentos
            relationship_changes = self._analyze_relationship_changes(
                user_input, response, relationships
            )
            
            # Extrai IDs de NPCs referenciados
            referenced_ids = {}
            for i, npc in enumerate(involved_npcs):
                referenced_ids[f"npc_{i}"] = npc.get("id", f"npc_{i}")
            
            metadata = {
                "interaction_type": interaction_type,
                "npcs_involved": len(involved_npcs),
                "relationship_changes": relationship_changes,
                "social_success_probability": social_modifiers.get("success_probability", 0.5),
                "reputation_impact": self._assess_reputation_impact(user_input, response)
            }
            
            return self._create_success_output(
                content=response,
                content_type="social_interaction",
                referenced_ids=referenced_ids,
                metadata=metadata
            )
            
        except Exception as e:
            return self._create_error_output(f"Erro no agente social: {str(e)}")
    
    def _identify_npcs(self, user_input: str, context: dict) -> list[dict]:
        """Identifica NPCs envolvidos na interação."""
        # TODO: Implementar identificação real de NPCs
        # Por enquanto, retorna NPCs mock baseados em palavras-chave
        
        npcs = []
        input_lower = user_input.lower()
        
        # NPCs comuns baseados em contexto
        if any(word in input_lower for word in ["comerciante", "vendedor", "lojista"]):
            npcs.append({
                "id": "merchant_001",
                "name": "Comerciante Local",
                "type": "merchant",
                "disposition": "neutral",
                "relationship_level": 0
            })
        
        if any(word in input_lower for word in ["guarda", "soldado", "patrulha"]):
            npcs.append({
                "id": "guard_001",
                "name": "Guarda da Cidade",
                "type": "authority",
                "disposition": "cautious",
                "relationship_level": 0
            })
        
        if any(word in input_lower for word in ["sábio", "mago", "estudioso"]):
            npcs.append({
                "id": "sage_001",
                "name": "Sábio Eldrin",
                "type": "scholar",
                "disposition": "helpful",
                "relationship_level": 1
            })
        
        if any(word in input_lower for word in ["aldeão", "pessoa", "habitante"]):
            npcs.append({
                "id": "villager_001",
                "name": "Aldeão Local",
                "type": "commoner",
                "disposition": "friendly",
                "relationship_level": 0
            })
        
        return npcs
    
    def _analyze_interaction_type(self, user_input: str) -> str:
        """Analisa o tipo de interação social."""
        input_lower = user_input.lower()
        
        # Tipos de interação baseados em palavras-chave
        if any(word in input_lower for word in ["convencer", "persuadir", "argumentar"]):
            return "persuasion"
        
        elif any(word in input_lower for word in ["intimidar", "ameaçar", "forçar"]):
            return "intimidation"
        
        elif any(word in input_lower for word in ["enganar", "mentir", "blefar"]):
            return "deception"
        
        elif any(word in input_lower for word in ["seduzir", "charme", "encantar"]):
            return "charm"
        
        elif any(word in input_lower for word in ["negociar", "barganhar", "trocar"]):
            return "negotiation"
        
        elif any(word in input_lower for word in ["informação", "perguntar", "questionar"]):
            return "information_gathering"
        
        elif any(word in input_lower for word in ["ajudar", "assistir", "apoiar"]):
            return "assistance"
        
        elif any(word in input_lower for word in ["insultar", "provocar", "ofender"]):
            return "provocation"
        
        else:
            return "casual_conversation"
    
    async def _get_relationships(self, context: dict, npcs: list[dict]) -> dict:
        """Busca relacionamentos existentes com os NPCs."""
        character_id = context.get('character_id')
        
        if not character_id or not npcs:
            return {}
        
        # TODO: Implementar busca real no banco de dados
        # Por enquanto, retorna relacionamentos mock
        relationships = {}
        
        for npc in npcs:
            npc_id = npc.get("id", "")
            relationships[npc_id] = {
                "trust_level": npc.get("relationship_level", 0),
                "reputation": "neutral",
                "history": ["first_meeting"],
                "favors_owed": 0,
                "conflicts": 0
            }
        
        return relationships
    
    def _calculate_social_modifiers(
        self, 
        interaction_type: str, 
        relationships: dict, 
        context: dict
    ) -> dict:
        """Calcula modificadores para a interação social."""
        base_probability = 0.5
        modifiers = {"base": base_probability}
        
        # Modificadores baseados no tipo de interação
        interaction_difficulty = {
            "casual_conversation": 0.8,
            "information_gathering": 0.6,
            "assistance": 0.7,
            "negotiation": 0.5,
            "persuasion": 0.4,
            "charm": 0.4,
            "deception": 0.3,
            "intimidation": 0.3,
            "provocation": 0.2
        }
        
        base_probability = interaction_difficulty.get(interaction_type, 0.5)
        modifiers["interaction_type"] = base_probability
        
        # Modificadores baseados em relacionamentos
        relationship_bonus = 0
        for npc_id, relationship in relationships.items():
            trust_level = relationship.get("trust_level", 0)
            relationship_bonus += trust_level * 0.1
        
        modifiers["relationship_bonus"] = relationship_bonus
        
        # Modificadores baseados no personagem
        character_data = context.get('character_data', {})
        archetypes = character_data.get('archetypes', [])
        
        social_archetypes = ["carismático", "diplomático", "persuasivo", "encantador"]
        archetype_bonus = 0.1 if any(arch.lower() in [sa.lower() for sa in social_archetypes] for arch in archetypes) else 0
        modifiers["archetype_bonus"] = archetype_bonus
        
        # Calcula probabilidade final
        final_probability = min(0.95, max(0.05, 
            base_probability + relationship_bonus + archetype_bonus
        ))
        
        modifiers["success_probability"] = final_probability
        
        return modifiers
    
    def _analyze_relationship_changes(
        self, 
        user_input: str, 
        response: str, 
        relationships: dict
    ) -> dict:
        """Analisa mudanças nos relacionamentos baseadas na interação."""
        changes = {}
        
        input_lower = user_input.lower()
        response_lower = response.lower()
        
        # Ações que melhoram relacionamentos
        positive_actions = ["ajudar", "apoiar", "elogiar", "presente", "favor"]
        # Ações que pioram relacionamentos
        negative_actions = ["insultar", "ameaçar", "enganar", "roubar", "atacar"]
        
        # Indicadores de sucesso na resposta
        success_indicators = ["sucesso", "aceita", "concorda", "satisfeito", "impressionado"]
        failure_indicators = ["falha", "rejeita", "recusa", "irritado", "ofendido"]
        
        for npc_id, relationship in relationships.items():
            change = {"trust_change": 0, "reputation_change": "none", "new_status": "unchanged"}
            
            # Analisa ações do jogador
            if any(action in input_lower for action in positive_actions):
                change["trust_change"] += 1
                change["reputation_change"] = "improved"
            
            if any(action in input_lower for action in negative_actions):
                change["trust_change"] -= 1
                change["reputation_change"] = "worsened"
            
            # Analisa resultado da interação
            if any(indicator in response_lower for indicator in success_indicators):
                change["trust_change"] += 0.5
                change["new_status"] = "positive_interaction"
            elif any(indicator in response_lower for indicator in failure_indicators):
                change["trust_change"] -= 0.5
                change["new_status"] = "negative_interaction"
            
            # Aplica mudanças apenas se houver alteração
            if change["trust_change"] != 0 or change["new_status"] != "unchanged":
                changes[npc_id] = change
        
        return changes
    
    def _assess_reputation_impact(self, user_input: str, response: str) -> dict:
        """Avalia o impacto na reputação geral do personagem."""
        impact = {
            "scope": "local",  # local, regional, widespread
            "type": "neutral",  # positive, negative, neutral
            "magnitude": "minor"  # minor, moderate, major
        }
        
        input_lower = user_input.lower()
        response_lower = response.lower()
        
        # Avalia escopo do impacto
        if any(word in input_lower for word in ["público", "todos", "multidão", "praça"]):
            impact["scope"] = "widespread"
        elif any(word in input_lower for word in ["grupo", "vários", "alguns"]):
            impact["scope"] = "regional"
        
        # Avalia tipo de impacto
        positive_keywords = ["heroico", "nobre", "generoso", "corajoso", "ajudar"]
        negative_keywords = ["criminoso", "desonesto", "cruel", "covarde", "prejudicar"]
        
        if any(keyword in input_lower for keyword in positive_keywords):
            impact["type"] = "positive"
        elif any(keyword in input_lower for keyword in negative_keywords):
            impact["type"] = "negative"
        
        # Avalia magnitude baseada na resposta
        if any(word in response_lower for word in ["impressionante", "extraordinário", "lendário"]):
            impact["magnitude"] = "major"
        elif any(word in response_lower for word in ["notável", "significativo", "importante"]):
            impact["magnitude"] = "moderate"
        
        return impact