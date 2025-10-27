"""
Testes unitários para verificar a integração com agentes.
"""

import pytest
from unittest.mock import AsyncMock, patch
from app.agents.router import RouterAgent


@pytest.mark.asyncio
async def test_router_agent_routing(test_report_dir, generate_report):
    """Testa o roteamento de mensagens para agentes especialistas."""
    
    # Mock para o LLM
    with patch('app.agents.router.ChatOpenAI') as mock_llm:
        # Configura o mock para retornar uma resposta específica
        mock_instance = mock_llm.return_value
        mock_with_structured = mock_instance.with_structured_output.return_value
        
        # Simula o retorno de um agente específico
        mock_result = [{
            "agent": "world",
            "instructions": "Processar entrada do usuário com contexto do mundo",
            "tool_class": "WorldExpertTool"
        }]
        mock_with_structured.ainvoke.return_value = mock_result
        
        # Instancia o agente roteador
        router_agent = RouterAgent()
        
        # Testa o roteamento
        user_input = "Descreva o mundo da minha campanha"
        context = {"campaign_id": "test-campaign-id"}
        
        result = await router_agent.route(user_input, context)
        
        # Verifica se o resultado é o esperado
        assert isinstance(result, list)
        assert len(result) > 0
        assert "agent" in result[0]
        assert "instructions" in result[0]
        
        # Gera relatório do teste
        report_data = {
            "Entrada do usuário": user_input,
            "Contexto": str(context),
            "Agentes roteados": str(result),
            "Resultado": "Sucesso - Roteamento funcionando corretamente"
        }
        
        generate_report("router_agent_routing", report_data, test_report_dir)

@pytest.mark.asyncio
async def test_campaign_creation_agent_integration(mock_campaign_creation_agent, test_report_dir, generate_report):
    """Testa a integração do agente de criação de campanhas."""
    
    # Importa o agente após o mock ser aplicado
    from app.agents.campaign_creation_agent import CampaignCreationAgent
    
    # Instancia o agente
    agent = CampaignCreationAgent()
    
    # Dados de teste
    campaign_data = {
        "name": "Crônicas do Reino Perdido",
        "genre_tags": ["fantasia", "aventura"],
        "master_personality": "epic_heroic",
        "character_concept": "Guerreiro exilado em busca de redenção",
        "character_archetypes": ["guerreiro", "exilado"],
        "character_approaches": ["força", "determinação"],
        "user_id": "test-user-id"
    }
    
    # Executa o método de criação de campanha
    result = await agent.create_campaign(campaign_data)
    
    # Verifica o resultado
    assert result["success"] is True
    assert "campaign" in result
    assert "character" in result
    assert "world_entities" in result
    assert "campaign_time" in result
    assert "initial_mission" in result
    
    # Gera relatório do teste
    report_data = {
        "Dados da campanha": str(campaign_data),
        "Resultado da criação": str(result),
        "Resultado": "Sucesso - Agente de criação de campanha funcionando corretamente"
    }
    
    generate_report("campaign_creation_agent_integration", report_data, test_report_dir)