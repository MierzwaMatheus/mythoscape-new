"""
Agente especialista em mundo - gerencia contexto, NPCs e locais.
"""

from typing import Optional
from app.agents.specialists.base_agent import BaseSpecialistAgent
from app.agents.graph_state import SpecialistOutput
from app.utils.env import get_env_var
from app.services.world_context import WorldContextService


class WorldAgent(BaseSpecialistAgent):
    """Agente especialista responsável pelo contexto do mundo, NPCs e locais."""
    
    def __init__(self):
        super().__init__("world")
        self.world_service = WorldContextService()
    
    def _get_system_prompt(self) -> str:
        """Retorna o prompt de sistema específico do agente de mundo."""
        return get_env_var("AGENT_WORLD_PROMPT")
    
    async def process_request(
        self, 
        user_input: str, 
        instructions: str, 
        context: dict
    ) -> SpecialistOutput:
        """Processa requisições relacionadas ao mundo."""
        
        try:
            # Busca contexto adicional do mundo se necessário
            world_context = await self._get_world_context(context)
            enhanced_context = {**context, "world_context": world_context}
            
            # Chama o LLM para processar a requisição
            response = await self._call_llm(user_input, instructions, enhanced_context)
            
            # Extrai IDs de entidades mencionadas
            referenced_ids = self._extract_entity_ids(response, context)
            
            # Determina se precisa atualizar o contexto do mundo
            needs_update = self._should_update_world_context(user_input, response)
            
            metadata = {
                "needs_context_update": needs_update,
                "world_entities_mentioned": len(referenced_ids)
            }
            
            return self._create_success_output(
                content=response,
                content_type="world_description",
                referenced_ids=referenced_ids,
                metadata=metadata
            )
            
        except Exception as e:
            return self._create_error_output(f"Erro no agente de mundo: {str(e)}")
    
    async def _get_world_context(self, context: dict) -> Optional[dict]:
        """Busca contexto adicional do mundo."""
        world_id = context.get('world_id')
        if not world_id:
            return None
        
        try:
            # Busca entidades relevantes do mundo
            entities = await self.world_service.search_entities(
                world_id=world_id,
                query=context.get('user_input', ''),
                limit=5
            )
            return {"entities": entities}
        except Exception:
            return None
    
    def _extract_entity_ids(self, response: str, context: dict) -> dict:
        """Extrai IDs de entidades mencionadas na resposta."""
        # Implementação básica - pode ser melhorada com NER
        referenced_ids = {}
        
        # Se há contexto de mundo, assume que as entidades foram referenciadas
        if context.get('world_context', {}).get('entities'):
            entities = context['world_context']['entities']
            for i, entity in enumerate(entities[:3]):  # Limita a 3 entidades
                entity_type = entity.get('entity_type', 'unknown')
                entity_id = entity.get('id', f"entity_{i}")
                referenced_ids[f"{entity_type}_{i}"] = entity_id
        
        return referenced_ids
    
    def _should_update_world_context(self, user_input: str, response: str) -> bool:
        """Determina se o contexto do mundo deve ser atualizado."""
        # Palavras-chave que indicam mudanças no mundo
        update_keywords = [
            "matar", "destruir", "criar", "construir", "mover", "alterar",
            "modificar", "adicionar", "remover", "mudar", "transformar"
        ]
        
        input_lower = user_input.lower()
        return any(keyword in input_lower for keyword in update_keywords)