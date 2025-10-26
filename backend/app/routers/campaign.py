"""
Rotas para criação e gerenciamento de campanhas.
"""

from fastapi import APIRouter, Depends, HTTPException
from app.models.campaign import CampaignCreationRequest, CampaignCreationResponse
from app.agents.campaign_creation_agent import CampaignCreationAgent
from app.dependencies.auth import AuthenticatedUser

router = APIRouter(prefix="/campaigns", tags=["campaigns"])

# Instância do agente de criação de campanhas
campaign_creation_agent = CampaignCreationAgent()


@router.post("/create", response_model=CampaignCreationResponse)
async def create_campaign(
    request: CampaignCreationRequest,
    user_id: AuthenticatedUser
) -> CampaignCreationResponse:
    """
    Cria uma nova campanha com base nos parâmetros fornecidos.
    
    Esta rota utiliza o agente de criação de campanhas para gerar:
    - Descrição detalhada do mundo
    - NPCs iniciais
    - Locais iniciais
    - Cena de abertura
    - Ficha completa do personagem
    - Tempo inicial da campanha
    - Missão inicial
    """
    try:
        # Converter o modelo Pydantic para dicionário
        campaign_data = request.model_dump()
        
        # Adicionar o ID do usuário atual
        campaign_data["user_id"] = user_id
        
        # Chamar o agente de criação de campanhas
        result = await campaign_creation_agent.create_campaign(campaign_data)
        
        if not result.get("success", True):
            raise HTTPException(
                status_code=500,
                detail=result.get("error", "Erro ao criar campanha")
            )
        
        # Adicionar flag de sucesso se não existir
        if "success" not in result:
            result["success"] = True
            
        # Garantir que error_message existe (mesmo que seja None)
        if "error_message" not in result:
            result["error_message"] = None
            
        return result
        
    except Exception as e:
        # Capturar qualquer exceção não tratada
        raise HTTPException(
            status_code=500,
            detail=f"Erro interno ao criar campanha: {str(e)}"
        )