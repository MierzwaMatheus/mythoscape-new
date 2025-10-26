"""
Agente especialista em tempo - gerencia o sistema de tempo da campanha e eventos temporais.
"""

from typing import Optional
from datetime import datetime, timedelta
from app.agents.specialists.base_agent import BaseSpecialistAgent
from app.agents.graph_state import SpecialistOutput
from app.utils.env import get_env_var


class TimeAgent(BaseSpecialistAgent):
    """Agente especialista responsável pelo sistema de tempo da campanha."""
    
    def __init__(self):
        super().__init__("time")
    
    def _get_system_prompt(self) -> str:
        """Retorna o prompt de sistema específico do agente de tempo."""
        return get_env_var("AGENT_TIME_PROMPT")
    
    async def process_request(
        self, 
        user_input: str, 
        instructions: str, 
        context: dict
    ) -> SpecialistOutput:
        """Processa requisições relacionadas ao tempo da campanha."""
        
        try:
            # Busca tempo atual da campanha
            current_time = await self._get_campaign_time(context)
            
            # Calcula passagem de tempo baseada na ação
            time_passage = self._calculate_time_passage(user_input)
            
            # Atualiza tempo da campanha
            new_time = self._update_campaign_time(current_time, time_passage)
            
            # Verifica eventos temporais
            temporal_events = self._check_temporal_events(current_time, new_time, context)
            
            # Prepara contexto temporal
            temporal_context = {
                **context,
                "current_time": current_time,
                "new_time": new_time,
                "time_passage": time_passage,
                "temporal_events": temporal_events
            }
            
            # Chama o LLM para processar a requisição
            response = await self._call_llm(user_input, instructions, temporal_context)
            
            metadata = {
                "time_passage": time_passage,
                "new_campaign_time": new_time,
                "temporal_events_triggered": len(temporal_events),
                "time_sensitive": self._is_time_sensitive_action(user_input)
            }
            
            return self._create_success_output(
                content=response,
                content_type="temporal_update",
                referenced_ids={},
                metadata=metadata
            )
            
        except Exception as e:
            return self._create_error_output(f"Erro no agente de tempo: {str(e)}")
    
    async def _get_campaign_time(self, context: dict) -> dict:
        """Busca o tempo atual da campanha."""
        world_id = context.get('world_id')
        
        # TODO: Implementar busca real no banco de dados
        # Por enquanto, retorna tempo mock
        return {
            "year": 1423,
            "month": 7,
            "day": 15,
            "hour": 14,
            "minute": 30,
            "season": "summer",
            "moon_phase": "waxing_gibbous",
            "weather": "clear"
        }
    
    def _calculate_time_passage(self, user_input: str) -> dict:
        """Calcula quanto tempo passa baseado na ação do usuário."""
        input_lower = user_input.lower()
        
        # Ações que consomem muito tempo
        if any(word in input_lower for word in ["viajar", "jornada", "caminhar longe", "explorar região"]):
            return {"hours": 8, "description": "viagem longa"}
        
        # Ações que consomem tempo moderado
        elif any(word in input_lower for word in ["descansar", "dormir", "acampar"]):
            return {"hours": 8, "description": "descanso completo"}
        
        elif any(word in input_lower for word in ["investigar", "procurar detalhadamente", "estudar"]):
            return {"hours": 2, "description": "investigação detalhada"}
        
        # Ações que consomem pouco tempo
        elif any(word in input_lower for word in ["conversar", "negociar", "discutir"]):
            return {"minutes": 30, "description": "conversa"}
        
        elif any(word in input_lower for word in ["lutar", "combate", "batalha"]):
            return {"minutes": 10, "description": "combate"}
        
        # Ações instantâneas ou muito rápidas
        elif any(word in input_lower for word in ["olhar", "observar", "falar", "gritar"]):
            return {"minutes": 1, "description": "ação rápida"}
        
        # Tempo padrão para ações não especificadas
        return {"minutes": 15, "description": "ação padrão"}
    
    def _update_campaign_time(self, current_time: dict, time_passage: dict) -> dict:
        """Atualiza o tempo da campanha."""
        new_time = current_time.copy()
        
        # Adiciona minutos
        if "minutes" in time_passage:
            new_time["minute"] += time_passage["minutes"]
            
            # Converte minutos em horas se necessário
            if new_time["minute"] >= 60:
                hours_to_add = new_time["minute"] // 60
                new_time["minute"] = new_time["minute"] % 60
                new_time["hour"] += hours_to_add
        
        # Adiciona horas
        if "hours" in time_passage:
            new_time["hour"] += time_passage["hours"]
        
        # Converte horas em dias se necessário
        if new_time["hour"] >= 24:
            days_to_add = new_time["hour"] // 24
            new_time["hour"] = new_time["hour"] % 24
            new_time["day"] += days_to_add
        
        # Converte dias em meses se necessário (simplificado - 30 dias por mês)
        if new_time["day"] > 30:
            months_to_add = (new_time["day"] - 1) // 30
            new_time["day"] = ((new_time["day"] - 1) % 30) + 1
            new_time["month"] += months_to_add
        
        # Converte meses em anos se necessário
        if new_time["month"] > 12:
            years_to_add = (new_time["month"] - 1) // 12
            new_time["month"] = ((new_time["month"] - 1) % 12) + 1
            new_time["year"] += years_to_add
        
        # Atualiza informações derivadas
        new_time["season"] = self._calculate_season(new_time["month"])
        new_time["moon_phase"] = self._calculate_moon_phase(new_time["day"])
        
        return new_time
    
    def _calculate_season(self, month: int) -> str:
        """Calcula a estação baseada no mês."""
        if month in [12, 1, 2]:
            return "winter"
        elif month in [3, 4, 5]:
            return "spring"
        elif month in [6, 7, 8]:
            return "summer"
        else:
            return "autumn"
    
    def _calculate_moon_phase(self, day: int) -> str:
        """Calcula a fase da lua baseada no dia (ciclo de 28 dias)."""
        lunar_day = day % 28
        
        if lunar_day < 7:
            return "new_moon"
        elif lunar_day < 14:
            return "waxing_gibbous"
        elif lunar_day < 21:
            return "full_moon"
        else:
            return "waning_gibbous"
    
    def _check_temporal_events(self, current_time: dict, new_time: dict, context: dict) -> list[dict]:
        """Verifica eventos que podem ser disparados pela passagem do tempo."""
        events = []
        
        # Verifica mudança de dia
        if current_time["day"] != new_time["day"]:
            events.append({
                "type": "day_change",
                "description": "Um novo dia começou",
                "effects": ["reset_daily_abilities", "check_mission_deadlines"]
            })
        
        # Verifica mudança de estação
        if current_time["season"] != new_time["season"]:
            events.append({
                "type": "season_change",
                "description": f"A estação mudou para {new_time['season']}",
                "effects": ["weather_change", "seasonal_events"]
            })
        
        # Verifica mudança de fase da lua
        if current_time["moon_phase"] != new_time["moon_phase"]:
            events.append({
                "type": "moon_phase_change",
                "description": f"A lua entrou na fase {new_time['moon_phase']}",
                "effects": ["magical_effects", "creature_behavior"]
            })
        
        # Verifica horários específicos
        if new_time["hour"] == 0 and current_time["hour"] != 0:
            events.append({
                "type": "midnight",
                "description": "Meia-noite chegou",
                "effects": ["supernatural_activity"]
            })
        elif new_time["hour"] == 12 and current_time["hour"] != 12:
            events.append({
                "type": "noon",
                "description": "Meio-dia chegou",
                "effects": ["peak_sunlight"]
            })
        
        return events
    
    def _is_time_sensitive_action(self, user_input: str) -> bool:
        """Verifica se a ação é sensível ao tempo."""
        time_sensitive_keywords = [
            "rapidamente", "urgente", "pressa", "imediatamente", "agora",
            "antes que", "tempo limite", "prazo", "expirar", "acabar"
        ]
        
        input_lower = user_input.lower()
        return any(keyword in input_lower for keyword in time_sensitive_keywords)