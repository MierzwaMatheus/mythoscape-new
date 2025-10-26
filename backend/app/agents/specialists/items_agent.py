"""
Agente especialista em itens - gerencia inventário, equipamentos e objetos do mundo.
"""

from typing import Optional
from app.agents.specialists.base_agent import BaseSpecialistAgent
from app.agents.graph_state import SpecialistOutput
from app.utils.env import get_env_var


class ItemsAgent(BaseSpecialistAgent):
    """Agente especialista responsável por itens, inventário e equipamentos."""
    
    def __init__(self):
        super().__init__("items")
    
    def _get_system_prompt(self) -> str:
        """Retorna o prompt de sistema específico do agente de itens."""
        return get_env_var("AGENT_ITEMS_PROMPT")
    
    async def process_request(
        self, 
        user_input: str, 
        instructions: str, 
        context: dict
    ) -> SpecialistOutput:
        """Processa requisições relacionadas a itens e inventário."""
        
        try:
            # Busca inventário atual
            current_inventory = await self._get_character_inventory(context)
            
            # Analisa interações com itens
            item_interactions = self._analyze_item_interactions(user_input, current_inventory)
            
            # Busca itens disponíveis no ambiente
            available_items = self._get_available_items(user_input, context)
            
            # Prepara contexto de itens
            items_context = {
                **context,
                "current_inventory": current_inventory,
                "item_interactions": item_interactions,
                "available_items": available_items
            }
            
            # Chama o LLM para processar a requisição
            response = await self._call_llm(user_input, instructions, items_context)
            
            # Calcula mudanças no inventário
            inventory_changes = self._calculate_inventory_changes(item_interactions)
            
            # Extrai IDs de itens referenciados
            referenced_ids = {}
            for i, item in enumerate(current_inventory[:3]):
                referenced_ids[f"item_{i}"] = item.get("id", f"item_{i}")
            
            metadata = {
                "inventory_changes": inventory_changes,
                "items_used": len([i for i in item_interactions if i["action"] == "use"]),
                "items_acquired": len([i for i in item_interactions if i["action"] == "acquire"]),
                "inventory_full": len(current_inventory) >= 10  # Limite exemplo
            }
            
            return self._create_success_output(
                content=response,
                content_type="item_interaction",
                referenced_ids=referenced_ids,
                metadata=metadata
            )
            
        except Exception as e:
            return self._create_error_output(f"Erro no agente de itens: {str(e)}")
    
    async def _get_character_inventory(self, context: dict) -> list[dict]:
        """Busca o inventário atual do personagem."""
        character_id = context.get('character_id')
        
        if not character_id:
            return []
        
        # TODO: Implementar busca real no banco de dados
        # Por enquanto, retorna inventário mock
        return [
            {
                "id": "sword_001",
                "name": "Espada de Ferro",
                "type": "weapon",
                "description": "Uma espada bem forjada",
                "properties": {"damage": "+2", "durability": 85},
                "equipped": True
            },
            {
                "id": "shield_001",
                "name": "Escudo de Madeira",
                "type": "armor",
                "description": "Um escudo resistente",
                "properties": {"defense": "+1", "durability": 70},
                "equipped": True
            },
            {
                "id": "potion_001",
                "name": "Poção de Cura",
                "type": "consumable",
                "description": "Restaura vitalidade",
                "properties": {"healing": "+2", "uses": 1},
                "equipped": False
            },
            {
                "id": "rope_001",
                "name": "Corda",
                "type": "tool",
                "description": "10 metros de corda resistente",
                "properties": {"length": "10m", "durability": 90},
                "equipped": False
            }
        ]
    
    def _analyze_item_interactions(self, user_input: str, inventory: list[dict]) -> list[dict]:
        """Analisa interações com itens baseadas na entrada do usuário."""
        interactions = []
        input_lower = user_input.lower()
        
        # Verifica ações de uso de itens
        use_keywords = ["usar", "consumir", "beber", "comer", "ativar", "equipar"]
        if any(keyword in input_lower for keyword in use_keywords):
            # Tenta identificar qual item está sendo usado
            for item in inventory:
                item_name_lower = item["name"].lower()
                if any(word in item_name_lower for word in input_lower.split()):
                    interactions.append({
                        "action": "use",
                        "item": item,
                        "success_probability": 0.9
                    })
                    break
        
        # Verifica ações de aquisição
        acquire_keywords = ["pegar", "coletar", "encontrar", "comprar", "receber"]
        if any(keyword in input_lower for keyword in acquire_keywords):
            interactions.append({
                "action": "acquire",
                "item": {"name": "Item Encontrado", "type": "unknown"},
                "success_probability": 0.7
            })
        
        # Verifica ações de descarte
        drop_keywords = ["dropar", "descartar", "jogar fora", "deixar"]
        if any(keyword in input_lower for keyword in drop_keywords):
            interactions.append({
                "action": "drop",
                "item": {"name": "Item Descartado", "type": "unknown"},
                "success_probability": 1.0
            })
        
        return interactions
    
    def _get_available_items(self, user_input: str, context: dict) -> list[dict]:
        """Busca itens disponíveis no ambiente atual."""
        input_lower = user_input.lower()
        
        # Lista de itens que podem estar disponíveis baseado no contexto
        potential_items = []
        
        # Itens em locais específicos
        if any(word in input_lower for word in ["floresta", "árvore", "natureza"]):
            potential_items.extend([
                {"name": "Galho Resistente", "type": "material", "rarity": "common"},
                {"name": "Ervas Medicinais", "type": "consumable", "rarity": "uncommon"}
            ])
        
        elif any(word in input_lower for word in ["caverna", "mina", "subterrâneo"]):
            potential_items.extend([
                {"name": "Cristal Brilhante", "type": "material", "rarity": "rare"},
                {"name": "Pedra Preciosa", "type": "treasure", "rarity": "uncommon"}
            ])
        
        elif any(word in input_lower for word in ["cidade", "loja", "mercado"]):
            potential_items.extend([
                {"name": "Equipamento Básico", "type": "equipment", "rarity": "common"},
                {"name": "Suprimentos", "type": "consumable", "rarity": "common"}
            ])
        
        # Itens baseados em ações
        if any(word in input_lower for word in ["procurar", "investigar", "explorar"]):
            potential_items.append({
                "name": "Item Oculto", "type": "treasure", "rarity": "rare"
            })
        
        return potential_items[:3]  # Limita a 3 itens
    
    def _calculate_inventory_changes(self, interactions: list[dict]) -> dict:
        """Calcula mudanças no inventário baseadas nas interações."""
        changes = {
            "items_added": [],
            "items_removed": [],
            "items_modified": [],
            "durability_changes": {}
        }
        
        for interaction in interactions:
            action = interaction["action"]
            item = interaction["item"]
            
            if action == "use":
                # Itens consumíveis são removidos
                if item.get("type") == "consumable":
                    changes["items_removed"].append(item["name"])
                else:
                    # Outros itens perdem durabilidade
                    item_name = item["name"]
                    current_durability = item.get("properties", {}).get("durability", 100)
                    new_durability = max(0, current_durability - 5)
                    changes["durability_changes"][item_name] = new_durability
                    
                    if new_durability <= 0:
                        changes["items_removed"].append(item_name)
            
            elif action == "acquire":
                changes["items_added"].append(item["name"])
            
            elif action == "drop":
                changes["items_removed"].append(item["name"])
        
        return changes
    
    def _assess_item_value(self, item: dict) -> int:
        """Avalia o valor de um item."""
        base_values = {
            "weapon": 100,
            "armor": 80,
            "tool": 50,
            "consumable": 20,
            "material": 10,
            "treasure": 200
        }
        
        item_type = item.get("type", "unknown")
        base_value = base_values.get(item_type, 25)
        
        # Modifica valor baseado na raridade
        rarity_multipliers = {
            "common": 1.0,
            "uncommon": 2.0,
            "rare": 5.0,
            "epic": 10.0,
            "legendary": 25.0
        }
        
        rarity = item.get("rarity", "common")
        multiplier = rarity_multipliers.get(rarity, 1.0)
        
        return int(base_value * multiplier)
    
    def _check_item_compatibility(self, item: dict, character_data: dict) -> bool:
        """Verifica se o item é compatível com o personagem."""
        # Verifica restrições básicas
        item_requirements = item.get("requirements", {})
        
        # Verifica arquétipos necessários
        required_archetypes = item_requirements.get("archetypes", [])
        character_archetypes = character_data.get("archetypes", [])
        
        if required_archetypes:
            has_required_archetype = any(
                arch in character_archetypes for arch in required_archetypes
            )
            if not has_required_archetype:
                return False
        
        # Verifica nível de vitalidade mínimo
        min_vitality = item_requirements.get("min_vitality", 0)
        character_vitality = character_data.get("vitality", 3)
        
        if character_vitality < min_vitality:
            return False
        
        return True