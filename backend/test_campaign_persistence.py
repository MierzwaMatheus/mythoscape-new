#!/usr/bin/env python3
"""
Script para testar o fluxo completo de criação de campanhas e chat multiagente.
Este script simula as entradas do usuário, ativa os agentes e verifica a persistência dos dados.
"""

import asyncio
import json
import uuid
import os
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple

from app.models.campaign import CampaignCreationRequest
from app.agents.campaign_creation_agent import CampaignCreationAgent
from app.services.supabase import get_supabase_client
from get_auth_token import SupabaseAuthHelper
from app.agents.multiagent_graph import create_rpg_agent_graph
from app.agents.graph_state import GraphState
from app.models.session import ChatMessage, MessageRole
from tests.utils.report_generator import ReportGenerator


async def test_campaign_creation_flow() -> Tuple[Optional[str], Optional[str]]:
    """Testa o fluxo completo de criação de campanha, simulando entrada do usuário."""
    print("\n=== Teste de Fluxo Completo: Criação de Campanha ===")
    
    # Inicializar gerador de relatórios
    report_dir = os.path.join(os.path.dirname(__file__), "tests", "reports")
    report_generator = ReportGenerator(report_dir)
    report_data = {
        "timestamp_inicio": datetime.now().isoformat(),
        "etapas": [],
        "dados_campanha": {},
        "persistencia": {}
    }
    success = True
    details = ""
    
    # 1. Obter token de autenticação e ID do usuário
    auth_helper = SupabaseAuthHelper()
    auth_result = auth_helper.sign_in_user("teste@teste.com", "kipa")
    
    report_data["etapas"].append({
        "etapa": "autenticacao",
        "sucesso": auth_result.get("success", False),
        "timestamp": datetime.now().isoformat()
    })
    
    if not auth_result.get("success"):
        error_msg = f"Falha na autenticação: {auth_result.get('message')}"
        print(f"❌ {error_msg}")
        report_data["erro"] = error_msg
        report_generator.generate("campanha_criacao", report_data, False, error_msg, "json")
        return None, None
    
    user_id = auth_result.get("user_id")
    print(f"✅ Autenticado com sucesso. User ID: {user_id}")
    report_data["user_id"] = user_id
    
    # 2. Simular entrada do usuário para criação de campanha
    print("\n🔄 Simulando entrada do usuário para criação de campanha...")
    campaign_request = CampaignCreationRequest(
        name="Campanha de Teste Completo",
        genre_tags=["fantasy", "medieval", "magic"],
        inspiration="Uma jornada épica em um mundo de magia e mistério",
        master_personality="serious_dark",
        character_concept="Um mago estudioso que busca conhecimentos proibidos",
        character_name="Eldrin",
        character_archetypes=["scholar", "mystic", "survivor"],
        character_approaches=["careful", "clever"]
    )
    
    # Registrar dados da requisição no relatório
    report_data["dados_requisicao"] = campaign_request.model_dump()
    report_data["etapas"].append({
        "etapa": "preparacao_requisicao",
        "sucesso": True,
        "timestamp": datetime.now().isoformat()
    })
    
    # 3. Criar a campanha usando o agente (simulando o endpoint)
    print("\n🔄 Processando criação de campanha via agente...")
    
    # Converter o modelo Pydantic para dicionário
    campaign_data = campaign_request.model_dump()
    campaign_data["user_id"] = user_id
    
    agent = CampaignCreationAgent()
    result = await agent.create_campaign(campaign_data)
    
    report_data["etapas"].append({
        "etapa": "criacao_campanha",
        "sucesso": not result.get("success") is False,
        "timestamp": datetime.now().isoformat()
    })
    
    if not result.get("success", True):
        error_msg = f"Falha ao criar campanha: {result.get('error_message', 'Erro desconhecido')}"
        print(f"❌ {error_msg}")
        report_data["erro"] = error_msg
        success = False
        details = error_msg
        report_generator.generate("campanha_criacao", report_data, success, details, "json")
        return None, None
    
    campaign_id = result.get("id")
    if not campaign_id:
        error_msg = "ID da campanha não retornado pelo agente"
        print(f"❌ {error_msg}")
        report_data["erro"] = error_msg
        success = False
        details = error_msg
        report_generator.generate("campanha_criacao", report_data, success, details, "json")
        return None, None
    
    print(f"✅ Campanha criada com sucesso. ID: {campaign_id}")
    report_data["campaign_id"] = campaign_id
    report_data["dados_campanha"] = result
    
    # 4. Verificar se os dados foram persistidos no Supabase
    print("\n🔄 Verificando persistência no Supabase...")
    supabase = get_supabase_client()
    
    # Verificar tabela campaigns
    db_result = supabase.table("campaigns").select("*").eq("id", campaign_id).execute()
    
    report_data["persistencia"]["campaigns"] = {
        "encontrado": len(db_result.data) > 0,
        "timestamp": datetime.now().isoformat()
    }
    
    if not db_result.data:
        error_msg = "Campanha não encontrada no banco de dados"
        print(f"❌ {error_msg}")
        report_data["erro"] = error_msg
        success = False
        details = error_msg
        report_generator.generate("campanha_criacao", report_data, success, details, "json")
        return None, None
    
    db_campaign = db_result.data[0]
    print(f"✅ Campanha encontrada no banco de dados:")
    print(f"  - ID: {db_campaign.get('id')}")
    print(f"  - Nome: {db_campaign.get('name')}")
    print(f"  - User ID: {db_campaign.get('user_id')}")
    
    report_data["persistencia"]["campaigns"]["dados"] = db_campaign
    
    # Verificar se os dados completos foram salvos
    campaign_data_json = db_campaign.get("campaign_data")
    if not campaign_data_json:
        error_msg = "Dados completos da campanha não encontrados"
        print(f"❌ {error_msg}")
        report_data["erro"] = error_msg
        success = False
        details = error_msg
        report_generator.generate("campanha_criacao", report_data, success, details, "json")
        return None, None
    
    try:
        # Se for string, converter para dict
        if isinstance(campaign_data_json, str):
            campaign_data_full = json.loads(campaign_data_json)
        else:
            campaign_data_full = campaign_data_json
            
        # Verificar campos essenciais
        has_campaign = "campaign" in campaign_data_full
        has_character = "character" in campaign_data_full
        has_world_entities = "world_entities" in campaign_data_full
        
        report_data["persistencia"]["validacao"] = {
            "has_campaign": has_campaign,
            "has_character": has_character,
            "has_world_entities": has_world_entities
        }
        
        if has_campaign and has_character and has_world_entities:
            print("✅ Dados completos da campanha foram persistidos corretamente")
        else:
            print("⚠️ Alguns dados da campanha podem estar faltando:")
            print(f"  - Dados da campanha: {'✅' if has_campaign else '❌'}")
            print(f"  - Dados do personagem: {'✅' if has_character else '❌'}")
            print(f"  - Entidades do mundo: {'✅' if has_world_entities else '❌'}")
            
            if not (has_campaign and has_character and has_world_entities):
                details = "Alguns dados essenciais da campanha estão faltando"
                success = False
    
    except Exception as e:
        error_msg = f"Erro ao analisar dados da campanha: {str(e)}"
        print(f"❌ {error_msg}")
        report_data["erro"] = error_msg
        success = False
        details = error_msg
        report_generator.generate("campanha_criacao", report_data, success, details, "json")
        return None, None
    
    # Verificar tabelas relacionadas (worlds, execution_logs)
    # Verificar se há registros na tabela worlds relacionados à campanha
    worlds_result = supabase.table("worlds").select("*").eq("campaign_id", campaign_id).execute()
    report_data["persistencia"]["worlds"] = {
        "encontrado": len(worlds_result.data) > 0,
        "quantidade": len(worlds_result.data),
        "timestamp": datetime.now().isoformat()
    }
    
    if worlds_result.data:
        print(f"✅ Mundo encontrado no banco de dados: {len(worlds_result.data)} registros")
        report_data["persistencia"]["worlds"]["dados"] = worlds_result.data
    else:
        print("⚠️ Nenhum mundo encontrado para esta campanha")
        # Tentar buscar pelo user_id como fallback
        fallback_worlds = supabase.table("worlds").select("*").eq("user_id", user_id).execute()
        if fallback_worlds.data:
            print(f"  ℹ️ (Encontrados {len(fallback_worlds.data)} mundos para este usuário)")
    
    # Verificar logs de execução
    logs_result = supabase.table("execution_logs").select("*").eq("metadata->>'campaign_id'", campaign_id).execute()
    report_data["persistencia"]["execution_logs"] = {
        "encontrado": len(logs_result.data) > 0,
        "quantidade": len(logs_result.data),
        "timestamp": datetime.now().isoformat()
    }
    
    if logs_result.data:
        print(f"✅ Logs de execução encontrados: {len(logs_result.data)} registros")
        report_data["persistencia"]["execution_logs"]["dados"] = logs_result.data
    else:
        print("⚠️ Nenhum log de execução encontrado para esta campanha")
    
    # Gerar relatório final
    report_data["timestamp_fim"] = datetime.now().isoformat()
    report_data["duracao_segundos"] = (datetime.fromisoformat(report_data["timestamp_fim"]) - 
                                      datetime.fromisoformat(report_data["timestamp_inicio"])).total_seconds()
    
    # Gerar relatório em JSON e TXT
    report_generator.generate("campanha_criacao", report_data, success, details, "json")
    report_generator.generate("campanha_criacao", report_data, success, details, "txt")
    
    print("\n=== Teste de Criação de Campanha Concluído ===")
    print(f"✅ Relatório gerado em: {report_dir}")
    
    return campaign_id, user_id


async def test_chat_multiagent_flow(campaign_id: str, user_id: str):
    """Testa o fluxo completo do chat multiagente, simulando mensagens do usuário."""
    print("\n=== Teste de Fluxo Completo: Chat Multiagente ===")
    
    # Inicializar gerador de relatórios
    report_dir = os.path.join(os.path.dirname(__file__), "tests", "reports")
    report_generator = ReportGenerator(report_dir)
    report_data = {
        "timestamp_inicio": datetime.now().isoformat(),
        "etapas": [],
        "campaign_id": campaign_id,
        "user_id": user_id,
        "mensagens": [],
        "persistencia": {}
    }
    success = True
    details = ""
    
    # 1. Inicializar o grafo de agentes
    print("\n🔄 Inicializando grafo de agentes...")
    try:
        graph = create_rpg_agent_graph()
        
        # 2. Criar estado inicial do grafo
        session_id = str(uuid.uuid4())
        state = GraphState(
            session_id=session_id,
            campaign_id=campaign_id,
            user_id=user_id,
            messages=[],
            current_message=None,
            world_context=[],
            execution_log=[]
        )
        
        report_data["session_id"] = session_id
        report_data["etapas"].append({
            "etapa": "inicializacao_grafo",
            "sucesso": True,
            "timestamp": datetime.now().isoformat()
        })
        
        print(f"✅ Grafo de agentes inicializado. Session ID: {session_id}")
        
        # 3. Simular mensagem do usuário
        user_message = "Olá, mestre! Estou pronto para começar minha aventura. O que vejo ao meu redor?"
        print(f"\n🔄 Simulando mensagem do usuário: '{user_message}'")
        
        # Adicionar mensagem ao estado
        message_id = str(uuid.uuid4())
        message = ChatMessage(
            id=message_id,
            role=MessageRole.USER,
            content=user_message,
            timestamp=0
        )
        state.messages.append(message)
        state.current_message = message
        
        report_data["mensagens"].append({
            "id": message_id,
            "role": "user",
            "content": user_message,
            "timestamp": datetime.now().isoformat()
        })
        
        report_data["etapas"].append({
            "etapa": "envio_mensagem_usuario",
            "sucesso": True,
            "timestamp": datetime.now().isoformat()
        })
        
        # 4. Executar o grafo de agentes
        print("\n🔄 Processando mensagem via grafo de agentes...")
        result = await graph.ainvoke(state)
        
        report_data["etapas"].append({
            "etapa": "processamento_grafo",
            "sucesso": bool(result and result.messages and len(result.messages) >= 2),
            "timestamp": datetime.now().isoformat()
        })
        
        # 5. Verificar resposta do agente sintetizador
        if not result or not result.messages or len(result.messages) < 2:
            error_msg = "Nenhuma resposta gerada pelo grafo de agentes"
            print(f"❌ {error_msg}")
            report_data["erro"] = error_msg
            success = False
            details = error_msg
            report_generator.generate("chat_multiagente", report_data, success, details, "json")
            return
        
        assistant_message = result.messages[-1]
        print(f"\n✅ Resposta do agente sintetizador:")
        print(f"  {assistant_message.content[:200]}...")
        
        report_data["mensagens"].append({
            "id": assistant_message.id,
            "role": "assistant",
            "content": assistant_message.content,
            "timestamp": datetime.now().isoformat()
        })
        
        # 6. Verificar logs de execução
        if result.execution_log:
            print(f"\n✅ Logs de execução gerados: {len(result.execution_log)} entradas")
            report_data["logs_execucao"] = {
                "quantidade": len(result.execution_log),
                "logs": result.execution_log
            }
        else:
            print("⚠️ Nenhum log de execução gerado")
            report_data["logs_execucao"] = {
                "quantidade": 0
            }
        
        # 7. Verificar persistência no banco de dados
        print("\n🔄 Verificando persistência dos dados da sessão...")
        supabase = get_supabase_client()
        
        # Verificar se a sessão foi salva
        sessions_result = supabase.table("sessions").select("*").eq("id", session_id).execute()
        report_data["persistencia"]["sessions"] = {
            "encontrado": len(sessions_result.data) > 0,
            "timestamp": datetime.now().isoformat()
        }
        
        if sessions_result.data:
            print("✅ Sessão salva no banco de dados")
            report_data["persistencia"]["sessions"]["dados"] = sessions_result.data
        else:
            print("❌ Sessão não encontrada no banco de dados")
            details += "Sessão não persistida no banco de dados. "
            success = False
        
        # Verificar se as mensagens foram salvas
        messages_result = supabase.table("messages").select("*").eq("session_id", session_id).execute()
        report_data["persistencia"]["messages"] = {
            "encontrado": len(messages_result.data) > 0,
            "quantidade": len(messages_result.data),
            "timestamp": datetime.now().isoformat()
        }
        
        if messages_result.data:
            print(f"✅ Mensagens salvas no banco de dados: {len(messages_result.data)} mensagens")
            report_data["persistencia"]["messages"]["dados"] = messages_result.data
        else:
            print("❌ Mensagens não encontradas no banco de dados")
            details += "Mensagens não persistidas no banco de dados. "
            success = False
        
        # Verificar logs de execução na tabela
        logs_result = supabase.table("execution_logs").select("*").eq("session_id", session_id).execute()
        report_data["persistencia"]["execution_logs"] = {
            "encontrado": len(logs_result.data) > 0,
            "quantidade": len(logs_result.data),
            "timestamp": datetime.now().isoformat()
        }
        
        if logs_result.data:
            print(f"✅ Logs de execução salvos no banco de dados: {len(logs_result.data)} registros")
            report_data["persistencia"]["execution_logs"]["dados"] = logs_result.data
        else:
            print("⚠️ Nenhum log de execução encontrado no banco de dados")
        
    except Exception as e:
        error_msg = f"Erro durante o teste do chat multiagente: {str(e)}"
        print(f"❌ {error_msg}")
        report_data["erro"] = error_msg
        success = False
        details = error_msg
    
    # Gerar relatório final
    report_data["timestamp_fim"] = datetime.now().isoformat()
    report_data["duracao_segundos"] = (datetime.fromisoformat(report_data["timestamp_fim"]) - 
                                      datetime.fromisoformat(report_data["timestamp_inicio"])).total_seconds()
    
    # Gerar relatório em JSON e TXT
    report_generator.generate("chat_multiagente", report_data, success, details, "json")
    report_generator.generate("chat_multiagente", report_data, success, details, "txt")
    
    print("\n=== Teste de Chat Multiagente Concluído ===")
    print(f"✅ Relatório gerado em: {report_dir}")


async def run_all_tests():
    """Executa todos os testes em sequência."""
    try:
        # Teste de criação de campanha
        campaign_id, user_id = await test_campaign_creation_flow()
        
        # Teste de chat multiagente (se o primeiro teste for bem-sucedido)
        if campaign_id and user_id:
            await test_chat_multiagent_flow(campaign_id, user_id)
        
    except Exception as e:
        print(f"\n❌ Erro durante a execução dos testes: {str(e)}")


if __name__ == "__main__":
    asyncio.run(run_all_tests())