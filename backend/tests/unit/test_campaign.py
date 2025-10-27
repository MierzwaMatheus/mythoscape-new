"""
Testes unitários para o módulo de campanhas.
"""

import pytest
import json
from fastapi import HTTPException
from app.models.campaign import CampaignCreationRequest


@pytest.mark.asyncio
async def test_create_campaign_success(client, mock_campaign_creation_agent, test_report_dir, generate_report):
    """Testa a criação bem-sucedida de uma campanha."""
    
    # Dados de teste
    test_data = {
        "name": "Aventuras nas Terras Místicas",
        "genre_tags": ["fantasia", "medieval", "magia"],
        "inspiration": "Senhor dos Anéis",
        "master_personality": "epic_heroic",
        "character_concept": "Mago errante em busca de conhecimento perdido",
        "character_name": "Elindor",
        "character_archetypes": ["sábio", "místico"],
        "character_approaches": ["astúcia", "conhecimento"]
    }
    
    # Executa a requisição
    response = client.post("/campaigns/create", json=test_data)
    
    # Verifica o status code
    assert response.status_code == 200
    
    # Verifica a estrutura da resposta
    result = response.json()
    assert result["success"] is True
    assert "campaign" in result
    assert "character" in result
    assert "world_entities" in result
    assert "campaign_time" in result
    assert "initial_mission" in result
    
    # Gera relatório do teste
    report_data = {
        "Requisição": json.dumps(test_data, indent=2, ensure_ascii=False),
        "Resposta": json.dumps(result, indent=2, ensure_ascii=False),
        "Status Code": response.status_code,
        "Resultado": "Sucesso - Campanha criada corretamente"
    }
    
    report_path = generate_report("create_campaign_success", report_data, test_report_dir)


@pytest.mark.asyncio
async def test_create_campaign_validation(client, test_report_dir, generate_report):
    """Testa a validação dos dados na criação de campanha."""
    
    # Dados de teste incompletos (faltando campos obrigatórios)
    test_data = {
        "name": "Campanha Incompleta",
        # Faltando genre_tags
        "master_personality": "serious_dark",
        # Faltando character_concept
        "character_archetypes": ["guerreiro"]
        # Faltando character_approaches
    }
    
    # Executa a requisição
    response = client.post("/campaigns/create", json=test_data)
    
    # Verifica o status code (deve ser 422 - Unprocessable Entity)
    assert response.status_code == 422
    
    # Verifica a estrutura da resposta de erro
    result = response.json()
    assert "detail" in result
    
    # Gera relatório do teste
    report_data = {
        "Requisição": json.dumps(test_data, indent=2, ensure_ascii=False),
        "Resposta": json.dumps(result, indent=2, ensure_ascii=False),
        "Status Code": response.status_code,
        "Resultado": "Sucesso - Validação funcionando corretamente"
    }
    
    report_path = generate_report("create_campaign_validation", report_data, test_report_dir)


@pytest.mark.asyncio
async def test_campaign_model_validation():
    """Testa a validação do modelo Pydantic de campanha."""
    
    # Teste com dados válidos
    valid_data = {
        "name": "Campanha Válida",
        "genre_tags": ["horror", "investigação"],
        "master_personality": "mysterious_occult",
        "character_concept": "Detetive paranormal",
        "character_archetypes": ["investigador", "sensitivo"],
        "character_approaches": ["percepção", "conhecimento"]
    }
    
    # Cria o modelo a partir dos dados válidos
    campaign_request = CampaignCreationRequest(**valid_data)
    
    # Verifica se os campos foram corretamente atribuídos
    assert campaign_request.name == valid_data["name"]
    assert campaign_request.genre_tags == valid_data["genre_tags"]
    assert campaign_request.master_personality == valid_data["master_personality"]
    assert campaign_request.character_concept == valid_data["character_concept"]
    assert campaign_request.character_archetypes == valid_data["character_archetypes"]
    assert campaign_request.character_approaches == valid_data["character_approaches"]
    
    # Verifica se campos opcionais são None quando não fornecidos
    assert campaign_request.inspiration is None
    assert campaign_request.character_name is None