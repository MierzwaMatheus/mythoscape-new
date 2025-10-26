"""
Serviço de integração do sistema multiagente.
"""

from typing import Dict, List, Optional, Any
import asyncio
import json
from datetime import datetime, timedelta
import logging

from fastapi import Depends
from app.agents.multiagent_graph import MultiAgentGraph
from app.agents.specialists.social_agent import SocialAgent
from app.agents.specialists.plot_agent import PlotAgent
from app.agents.specialists.items_agent import ItemsAgent
from app.agents.specialists.mission_agent import MissionAgent
from app.agents.specialists.world_agent import WorldAgent
from app.agents.specialists.character_agent import CharacterAgent
from app.agents.specialists.rules_agent import RulesAgent
from app.agents.specialists.time_agent import TimeAgent
from app.agents.graph_state import AgentState, SpecialistOutput, VectorStoreUpdate
from app.utils.cache import CacheManager
from app.services.world_context import WorldContextService
from app.services.vector_store_service import VectorStoreService
from app.models.execution_log import ExecutionLog
from app.models.user import User
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db


class MultiAgentService:
    """Serviço principal para integração do sistema multiagente."""
    
    def __init__(
        self,
        db: AsyncSession = Depends(get_db),
        world_context_service: WorldContextService = Depends(),
        vector_store_service: VectorStoreService = Depends(),
        cache_manager: CacheManager = Depends()
    ):
        self.db = db
        self.world_context_service = world_context_service
        self.vector_store_service = vector_store_service
        self.cache_manager = cache_manager
        
        # Inicializa o grafo multiagente
        self.multiagent_graph = MultiAgentGraph()
        
        # Cache de agentes individuais para testes
        self._individual_agents = {
            "world": WorldAgent(),
            "character": CharacterAgent(),
            "mission": MissionAgent(),
            "rules": RulesAgent(),
            "time": TimeAgent(),
            "items": ItemsAgent(),
            "plot": PlotAgent(),
            "social": SocialAgent()
        }
    
    async def process_user_action(
        self,
        user_input: str,
        world_context: dict,
        user_id: str
    ) -> AgentState:
        """Processa uma ação do usuário através do sistema multiagente."""
        
        # Verifica cache primeiro
        cache_key = self._generate_cache_key(user_input, world_context, user_id)
        cached_result = await self.cache_manager.get(cache_key)
        
        if cached_result:
            return AgentState(**cached_result)
        
        try:
            # Processa através do grafo multiagente
            result = await self.multiagent_graph.process_user_input(
                user_input=user_input,
                world_context=world_context
            )
            
            # Salva no cache (expira em 1 hora)
            await self.cache_manager.set(
                cache_key, 
                result.dict(), 
                expire_seconds=3600
            )
            
            return result
            
        except Exception as e:
            # Log do erro
            await self._log_error(user_id, user_input, str(e))
            
            # Retorna estado de erro
            error_state = AgentState(
                user_input=user_input,
                world_context=world_context,
                selected_agents=[],
                specialist_outputs=[],
                final_narrative=f"Desculpe, ocorreu um erro ao processar sua ação: {str(e)}",
                execution_duration=0.0,
                vector_store_updates=[],
                execution_metadata={"error": str(e), "timestamp": datetime.now()}
            )
            
            return error_state
    
    async def enrich_world_context(
        self,
        base_context: dict,
        user_id: str,
        character_id: Optional[str] = None,
        campaign_id: Optional[str] = None
    ) -> dict:
        """Enriquece o contexto do mundo com dados adicionais."""
        
        enriched_context = base_context.copy()
        
        try:
            # Adiciona contexto do mundo se disponível
            if campaign_id:
                world_data = await self.world_context_service.get_world_context(campaign_id)
                enriched_context.update(world_data)
            
            # Adiciona dados do personagem se disponível
            if character_id:
                character_data = await self._get_character_context(character_id, user_id)
                enriched_context["character"] = character_data
            
            # Adiciona dados do usuário
            user_data = await self._get_user_context(user_id)
            enriched_context["user"] = user_data
            
            # Adiciona timestamp
            enriched_context["timestamp"] = datetime.now().isoformat()
            
            return enriched_context
            
        except Exception as e:
            # Em caso de erro, retorna contexto base
            enriched_context["enrichment_error"] = str(e)
            return enriched_context
    
    async def test_individual_agent(
        self,
        agent_name: str,
        user_input: str,
        world_context: dict
    ) -> SpecialistOutput:
        """Testa um agente especialista individual."""
        
        if agent_name not in self._individual_agents:
            return SpecialistOutput(
                agent_type=agent_name,
                content="",
                content_type="error",
                success=False,
                error_message=f"Agente '{agent_name}' não encontrado",
                metadata={}
            )
        
        try:
            agent = self._individual_agents[agent_name]
            return await agent.process_request(user_input, world_context)
            
        except Exception as e:
            return SpecialistOutput(
                agent_type=agent_name,
                content="",
                content_type="error",
                success=False,
                error_message=str(e),
                metadata={}
            )
    
    async def get_system_status(self) -> dict:
        """Retorna o status atual do sistema multiagente."""
        
        try:
            # Testa conectividade básica de cada agente
            agent_status = {}
            
            for agent_name, agent in self._individual_agents.items():
                try:
                    # Teste básico com entrada mínima
                    test_result = await agent.process_request("teste", {})
                    agent_status[agent_name] = "online" if test_result else "error"
                except Exception:
                    agent_status[agent_name] = "offline"
            
            # Verifica última execução
            last_execution = await self._get_last_execution_time()
            
            # Determina status geral
            online_agents = sum(1 for status in agent_status.values() if status == "online")
            total_agents = len(agent_status)
            
            if online_agents == total_agents:
                system_status = "healthy"
            elif online_agents > total_agents // 2:
                system_status = "degraded"
            else:
                system_status = "critical"
            
            return {
                "status": system_status,
                "available_agents": list(self._individual_agents.keys()),
                "agent_status": agent_status,
                "online_agents": online_agents,
                "total_agents": total_agents,
                "last_execution": last_execution
            }
            
        except Exception as e:
            return {
                "status": "error",
                "available_agents": [],
                "error": str(e),
                "last_execution": None
            }
    
    async def process_vector_store_updates(
        self,
        updates: list[VectorStoreUpdate],
        user_id: str
    ) -> None:
        """Processa atualizações do vector store em background."""
        
        try:
            for update in updates:
                if update.operation == "add":
                    await self.vector_store_service.add_document(
                        content=update.content,
                        metadata=update.metadata,
                        user_id=user_id
                    )
                elif update.operation == "update":
                    await self.vector_store_service.update_document(
                        document_id=update.document_id,
                        content=update.content,
                        metadata=update.metadata
                    )
                elif update.operation == "delete":
                    await self.vector_store_service.delete_document(
                        document_id=update.document_id
                    )
                    
        except Exception as e:
            # Log do erro mas não falha o processo principal
            await self._log_error(user_id, "vector_store_update", str(e))
    
    async def save_execution_log(
        self,
        result: AgentState,
        user_id: str,
        original_input: str
    ) -> None:
        """Salva log da execução no banco de dados."""
        
        try:
            log_data = {
                "user_id": user_id,
                "input_text": original_input,
                "output_narrative": result.final_narrative,
                "execution_time": result.execution_duration,
                "agents_used": result.selected_agents,
                "success": bool(result.final_narrative and result.final_narrative.strip()),
                "execution_metadata": result.execution_metadata,
                "created_at": datetime.now()
            }
            
            # Insere no banco
            stmt = insert(ExecutionLog).values(**log_data)
            await self.db.execute(stmt)
            await self.db.commit()
            
        except Exception as e:
            # Log do erro mas não falha o processo principal
            await self._log_error(user_id, "save_execution_log", str(e))
    
    async def get_execution_history(
        self,
        user_id: str,
        limit: int = 10,
        offset: int = 0
    ) -> list[dict]:
        """Retorna o histórico de execuções do usuário."""
        
        try:
            stmt = (
                select(ExecutionLog)
                .where(ExecutionLog.user_id == user_id)
                .order_by(ExecutionLog.created_at.desc())
                .limit(limit)
                .offset(offset)
            )
            
            result = await self.db.execute(stmt)
            logs = result.scalars().all()
            
            return [
                {
                    "id": log.id,
                    "input_text": log.input_text,
                    "output_narrative": log.output_narrative,
                    "execution_time": log.execution_time,
                    "agents_used": log.agents_used,
                    "success": log.success,
                    "created_at": log.created_at,
                    "metadata": log.execution_metadata
                }
                for log in logs
            ]
            
        except Exception as e:
            await self._log_error(user_id, "get_execution_history", str(e))
            return []
    
    async def clear_user_cache(self, user_id: str) -> int:
        """Limpa o cache relacionado ao usuário."""
        
        try:
            # Padrão de chave de cache para o usuário
            pattern = f"multiagent:*:user:{user_id}:*"
            return await self.cache_manager.delete_pattern(pattern)
            
        except Exception as e:
            await self._log_error(user_id, "clear_user_cache", str(e))
            return 0
    
    def _generate_cache_key(self, user_input: str, world_context: dict, user_id: str) -> str:
        """Gera chave de cache para a requisição."""
        
        # Cria hash do contexto para chave mais compacta
        context_hash = hash(json.dumps(world_context, sort_keys=True))
        input_hash = hash(user_input)
        
        return f"multiagent:{input_hash}:user:{user_id}:context:{context_hash}"
    
    async def _get_character_context(self, character_id: str, user_id: str) -> dict:
        """Busca contexto do personagem."""
        
        try:
            # TODO: Implementar busca real do personagem
            return {
                "id": character_id,
                "name": "Personagem Teste",
                "level": 1,
                "vitality": {"current": 100, "max": 100},
                "inventory": []
            }
            
        except Exception:
            return {"id": character_id, "error": "Dados não encontrados"}
    
    async def _get_user_context(self, user_id: str) -> dict:
        """Busca contexto do usuário."""
        
        try:
            # Buscar usuário no banco de dados
            from app.models.user import UserTable
            stmt = select(UserTable).where(UserTable.id == user_id)
            result = await self.db.execute(stmt)
            user = result.scalar_one_or_none()
            
            if user:
                return {
                    "id": user.id,
                    "name": user.name,
                    "email": user.email,
                    "preferences": user.preferences or {},
                    "last_login": user.last_login.isoformat() if user.last_login else None,
                    "is_active": user.is_active
                }
            else:
                return {"id": user_id, "error": "Usuário não encontrado"}
            
        except Exception as e:
            logging.error(f"Erro ao buscar contexto do usuário {user_id}: {e}")
            return {"id": user_id, "error": "Dados não encontrados"}
    
    async def _get_last_execution_time(self) -> Optional[datetime]:
        """Busca o timestamp da última execução."""
        
        try:
            stmt = (
                select(ExecutionLog.created_at)
                .order_by(ExecutionLog.created_at.desc())
                .limit(1)
            )
            
            result = await self.db.execute(stmt)
            last_time = result.scalar_one_or_none()
            
            return last_time
            
        except Exception:
            return None
    
    async def _log_error(self, user_id: str, operation: str, error_message: str) -> None:
        """Log de erros internos."""
        
        try:
            # TODO: Implementar sistema de log mais robusto
            print(f"ERROR [{datetime.now()}] User: {user_id}, Op: {operation}, Error: {error_message}")
            
        except Exception:
            # Falha silenciosa para evitar loops de erro
            pass