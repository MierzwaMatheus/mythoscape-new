"""
Agente sintetizador - combina saídas dos agentes especialistas em uma narrativa coesa.
"""

from typing import Optional
from langchain_openai import ChatOpenAI
from app.agents.graph_state import AgentState, SpecialistOutput
from app.utils.env import get_env_var


class SynthesizerAgent:
    """Agente responsável por sintetizar as saídas dos especialistas em uma narrativa final."""
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.3,  # Baixa criatividade para manter coerência
            max_tokens=2000
        )
    
    async def synthesize_outputs(self, state: AgentState) -> str:
        """Sintetiza as saídas dos agentes especialistas em uma narrativa coesa."""
        
        try:
            # Prepara contexto para síntese
            synthesis_context = self._prepare_synthesis_context(state)
            
            # Constrói prompt de síntese
            synthesis_prompt = self._build_synthesis_prompt(
                state.user_input,
                state.specialist_outputs,
                synthesis_context
            )
            
            # Chama o LLM para sintetizar
            response = await self.llm.ainvoke([
                {"role": "system", "content": self._get_system_prompt()},
                {"role": "user", "content": synthesis_prompt}
            ])
            
            # Extrai e processa a resposta
            synthesized_narrative = response.content.strip()
            
            # Adiciona elementos de coerência se necessário
            final_narrative = self._enhance_narrative_coherence(
                synthesized_narrative, 
                state.specialist_outputs
            )
            
            return final_narrative
            
        except Exception as e:
            # Fallback para síntese básica em caso de erro
            return self._create_fallback_synthesis(state.specialist_outputs)
    
    def _get_system_prompt(self) -> str:
        """Retorna o prompt de sistema do sintetizador."""
        return get_env_var("AGENT_SYNTHESIZER_PROMPT")
    
    def _prepare_synthesis_context(self, state: AgentState) -> dict:
        """Prepara contexto adicional para a síntese."""
        context = {
            "world_context": state.world_context,
            "execution_metadata": {
                "total_specialists": len(state.specialist_outputs),
                "execution_duration": state.execution_duration,
                "has_errors": any(
                    output.success is False for output in state.specialist_outputs
                )
            }
        }
        
        # Agrupa saídas por tipo de conteúdo
        content_types = {}
        for output in state.specialist_outputs:
            content_type = output.content_type
            if content_type not in content_types:
                content_types[content_type] = []
            content_types[content_type].append(output)
        
        context["content_types"] = content_types
        
        # Extrai metadados importantes
        important_metadata = self._extract_important_metadata(state.specialist_outputs)
        context["important_metadata"] = important_metadata
        
        return context
    
    def _build_synthesis_prompt(
        self, 
        user_input: str, 
        specialist_outputs: list[SpecialistOutput],
        context: dict
    ) -> str:
        """Constrói o prompt para síntese das saídas."""
        
        prompt_parts = [
            f"ENTRADA DO USUÁRIO: {user_input}",
            "",
            "SAÍDAS DOS AGENTES ESPECIALISTAS:",
        ]
        
        # Adiciona cada saída de especialista
        for i, output in enumerate(specialist_outputs, 1):
            if output.success:
                prompt_parts.extend([
                    f"{i}. AGENTE {output.agent_type.upper()}:",
                    f"   Conteúdo: {output.content}",
                    f"   Tipo: {output.content_type}",
                ])
                
                # Adiciona metadados importantes se existirem
                if output.metadata:
                    important_meta = self._filter_important_metadata(output.metadata)
                    if important_meta:
                        prompt_parts.append(f"   Metadados: {important_meta}")
                
                prompt_parts.append("")
            else:
                prompt_parts.extend([
                    f"{i}. AGENTE {output.agent_type.upper()}: [ERRO - {output.error_message}]",
                    ""
                ])
        
        # Adiciona contexto adicional
        if context.get("important_metadata"):
            prompt_parts.extend([
                "INFORMAÇÕES IMPORTANTES:",
                str(context["important_metadata"]),
                ""
            ])
        
        prompt_parts.extend([
            "INSTRUÇÕES:",
            "1. Combine todas as saídas em uma narrativa coesa e envolvente",
            "2. Mantenha a coerência com o mundo e personagem",
            "3. Integre naturalmente as informações de regras, tempo e itens",
            "4. Preserve elementos importantes como mudanças de estado",
            "5. Use um tom narrativo apropriado para RPG",
            "6. Se houver conflitos entre agentes, priorize a coerência narrativa",
            "",
            "NARRATIVA FINAL:"
        ])
        
        return "\n".join(prompt_parts)
    
    def _extract_important_metadata(self, outputs: list[SpecialistOutput]) -> dict:
        """Extrai metadados importantes das saídas dos especialistas."""
        important_data = {
            "character_changes": {},
            "world_updates": {},
            "time_progression": {},
            "mission_updates": {},
            "social_changes": {}
        }
        
        for output in outputs:
            if not output.success or not output.metadata:
                continue
            
            agent_type = output.agent_type
            metadata = output.metadata
            
            # Extrai dados específicos por tipo de agente
            if agent_type == "character":
                if metadata.get("character_changes"):
                    important_data["character_changes"] = metadata["character_changes"]
                if metadata.get("vitality_affected"):
                    important_data["character_changes"]["vitality_affected"] = True
            
            elif agent_type == "world":
                if metadata.get("needs_context_update"):
                    important_data["world_updates"]["context_updated"] = True
            
            elif agent_type == "time":
                if metadata.get("time_passage"):
                    important_data["time_progression"] = metadata["time_passage"]
                if metadata.get("new_campaign_time"):
                    important_data["time_progression"]["new_time"] = metadata["new_campaign_time"]
            
            elif agent_type == "mission":
                if metadata.get("mission_progress"):
                    important_data["mission_updates"] = metadata["mission_progress"]
                if metadata.get("plot_twist_triggered"):
                    important_data["mission_updates"]["plot_twist"] = True
            
            elif agent_type == "social":
                if metadata.get("relationship_changes"):
                    important_data["social_changes"] = metadata["relationship_changes"]
        
        # Remove seções vazias
        return {k: v for k, v in important_data.items() if v}
    
    def _filter_important_metadata(self, metadata: dict) -> dict:
        """Filtra apenas metadados importantes para a síntese."""
        important_keys = [
            "success_level", "narrative_impact", "character_changes",
            "time_passage", "plot_twist_triggered", "relationship_changes",
            "dice_result", "inventory_changes"
        ]
        
        return {k: v for k, v in metadata.items() if k in important_keys}
    
    def _enhance_narrative_coherence(
        self, 
        narrative: str, 
        outputs: list[SpecialistOutput]
    ) -> str:
        """Melhora a coerência narrativa adicionando elementos conectivos."""
        
        # Verifica se há elementos importantes não mencionados
        missing_elements = self._identify_missing_elements(narrative, outputs)
        
        if missing_elements:
            # Adiciona elementos faltantes de forma sutil
            enhanced_narrative = self._integrate_missing_elements(narrative, missing_elements)
            return enhanced_narrative
        
        return narrative
    
    def _identify_missing_elements(
        self, 
        narrative: str, 
        outputs: list[SpecialistOutput]
    ) -> list[str]:
        """Identifica elementos importantes que podem estar faltando na narrativa."""
        missing = []
        narrative_lower = narrative.lower()
        
        for output in outputs:
            if not output.success:
                continue
            
            # Verifica elementos específicos por tipo de agente
            if output.agent_type == "rules" and output.metadata.get("dice_result"):
                if "teste" not in narrative_lower and "dado" not in narrative_lower:
                    missing.append("resultado_teste")
            
            elif output.agent_type == "time" and output.metadata.get("time_passage"):
                if "tempo" not in narrative_lower and "hora" not in narrative_lower:
                    missing.append("passagem_tempo")
            
            elif output.agent_type == "character" and output.metadata.get("vitality_affected"):
                if "vitalidade" not in narrative_lower and "ferimento" not in narrative_lower:
                    missing.append("mudanca_vitalidade")
        
        return missing
    
    def _integrate_missing_elements(self, narrative: str, missing_elements: list[str]) -> str:
        """Integra elementos faltantes na narrativa."""
        additions = []
        
        for element in missing_elements:
            if element == "resultado_teste":
                additions.append("O resultado da ação foi determinado pelas circunstâncias.")
            elif element == "passagem_tempo":
                additions.append("O tempo passou durante essa ação.")
            elif element == "mudanca_vitalidade":
                additions.append("Isso afetou o estado físico do personagem.")
        
        if additions:
            return narrative + " " + " ".join(additions)
        
        return narrative
    
    def _create_fallback_synthesis(self, outputs: list[SpecialistOutput]) -> str:
        """Cria uma síntese básica em caso de falha do LLM."""
        successful_outputs = [output for output in outputs if output.success]
        
        if not successful_outputs:
            return "Algo inesperado aconteceu e não foi possível processar completamente sua ação."
        
        # Combina as saídas de forma simples
        combined_content = []
        for output in successful_outputs:
            if output.content:
                combined_content.append(output.content)
        
        if combined_content:
            return " ".join(combined_content)
        else:
            return "Sua ação foi processada, mas os detalhes não estão claros no momento."