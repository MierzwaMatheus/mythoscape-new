"""
Configurações globais para testes do projeto Mythoscape.
"""

import os
import sys
import pytest
from fastapi.testclient import TestClient
from datetime import datetime
from unittest.mock import AsyncMock, patch

# Adiciona o diretório raiz ao path para importação dos módulos
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.main import app
from app.dependencies.auth import get_authenticated_user
from get_auth_token import SupabaseAuthHelper


@pytest.fixture
def auth_token():
    """Fixture que fornece um token de autenticação válido para testes."""
    auth_helper = SupabaseAuthHelper()
    result = auth_helper.sign_in_user("teste@teste.com", "kipa")
    if not result.get("success"):
        pytest.fail(f"Falha ao obter token de autenticação: {result.get('message')}")
    return result["access_token"]


@pytest.fixture
def client(auth_token):
    """Fixture que fornece um cliente de teste para a API FastAPI."""
    # Configura o cliente com o token de autenticação
    client = TestClient(app)
    client.headers.update({"Authorization": f"Bearer {auth_token}"})
    return client


@pytest.fixture
def test_report_dir():
    """Fixture que fornece o diretório para relatórios de teste."""
    report_dir = os.path.join(os.path.dirname(__file__), "reports")
    os.makedirs(report_dir, exist_ok=True)
    return report_dir


@pytest.fixture
def generate_report():
    """Fixture que fornece uma função para gerar relatórios de teste."""
    def _generate_report(test_name, test_data, report_dir):
        """
        Gera um relatório de teste em formato de texto.
        
        Args:
            test_name: Nome do teste
            test_data: Dados do teste para incluir no relatório
            report_dir: Diretório onde o relatório será salvo
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{test_name}_{timestamp}.txt"
        filepath = os.path.join(report_dir, filename)
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(f"=== Relatório de Teste: {test_name} ===\n")
            f.write(f"Data/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 50 + "\n\n")
            
            # Escreve os dados do teste
            if isinstance(test_data, dict):
                for key, value in test_data.items():
                    f.write(f"{key}:\n")
                    f.write(f"{value}\n\n")
            else:
                f.write(str(test_data) + "\n")
                
        return filepath
    
    return _generate_report


@pytest.fixture
def mock_campaign_creation_agent(monkeypatch):
    """Fixture que fornece um mock para o agente de criação de campanhas."""
    
    async def mock_create_campaign(self, campaign_data):
        """Mock para o método create_campaign do agente."""
        return {
            "success": True,
            "campaign": {
                "id": "mock-campaign-id",
                "name": campaign_data.get("name", "Campanha de Teste"),
                "description": "Uma campanha de teste gerada para fins de teste unitário."
            },
            "character": {
                "id": "mock-character-id",
                "name": "Personagem de Teste",
                "concept": campaign_data.get("character_concept", "Conceito de teste")
            },
            "world_entities": {
                "npcs": [
                    {"id": "npc-1", "name": "NPC de Teste 1", "description": "Um NPC para testes."},
                    {"id": "npc-2", "name": "NPC de Teste 2", "description": "Outro NPC para testes."}
                ],
                "locations": [
                    {"id": "loc-1", "name": "Local de Teste", "description": "Um local para testes."}
                ]
            },
            "campaign_time": {
                "year": 1000,
                "month": 1,
                "day": 1,
                "hour": 12,
                "minute": 0
            },
            "initial_mission": {
                "title": "Missão de Teste",
                "description": "Uma missão para testar o sistema."
            }
        }
    
    # Aplica o patch
    from app.agents.campaign_creation_agent import CampaignCreationAgent
    monkeypatch.setattr(CampaignCreationAgent, "create_campaign", mock_create_campaign)