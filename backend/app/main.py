"""Aplicação principal FastAPI para o Mestre de RPG com IA."""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from app.utils.env import load_env

# Carrega variáveis de ambiente ANTES de qualquer importação que dependa delas
load_env()

# Agora importa o RPGAgent após carregar as variáveis de ambiente
from app.agents.rpg_agent import RPGAgent
from app.routers.chat import router as chat_router
from app.routers.world_context import router as world_context_router
from app.routers.admin import router as admin_router
from app.routers.world import router as world_router
from app.dependencies.auth import AuthenticatedUser
from app.models.errors import ErrorDetail, InternalServerError, AuthenticationError, ValidationError

# Inicializa o agente RPG globalmente para eficiência
rpg_agent = RPGAgent()

# Modelos Pydantic para requisição e resposta de chat
class ChatRequest(BaseModel):
    """Modelo para requisição de chat."""
    prompt: str = Field(..., min_length=1, max_length=2000)

class ChatResponse(BaseModel):
    """Modelo para resposta de chat."""
    response: str

# Inicializa a aplicação FastAPI
app = FastAPI(
    title="Mestre de RPG com IA",
    description="API para sistema de RPG assistido por Inteligência Artificial",
    version="1.0.0"
)

# Configuração do CORS - restritivo para produção, permissivo para desenvolvimento
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8080",      # Frontend em desenvolvimento
        "http://127.0.0.1:8080",     # Frontend em desenvolvimento (IP)
        "https://yourdomain.com",    # Substitua pelo seu domínio em produção
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST"],   # Apenas métodos necessários
    allow_headers=["Authorization", "Content-Type"],  # Headers específicos
)

# Endpoint POST /chat (protegido por autenticação)
@app.post(
    "/chat", 
    response_model=ChatResponse,
    responses={
        401: {"model": AuthenticationError, "description": "Não autenticado"},
        422: {"model": ValidationError, "description": "Prompt inválido"},
        500: {"model": InternalServerError, "description": "Erro interno do servidor"}
    }
)
async def chat_endpoint(request: ChatRequest, user_id: AuthenticatedUser) -> ChatResponse:
    """
    Endpoint principal de chat com o Mestre de RPG.
    Requer autenticação válida (exceto para localhost em desenvolvimento).
    
    Args:
        request: Requisição contendo o prompt do jogador.
        user_id: ID do usuário autenticado (injetado pela dependência).
        
    Returns:
        Resposta do agente RPG formatada.
        
    Raises:
        HTTPException: Em caso de erro na geração da resposta
    """
    try:
        # Adiciona contexto do usuário ao prompt se necessário
        enhanced_prompt = f"[Usuário: {user_id}] {request.prompt}"
        response = await rpg_agent.run(enhanced_prompt)
        return ChatResponse(response=response)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=ErrorDetail(
                message="Erro interno ao processar chat",
                error_code="CHAT_ERROR",
                details={"original_error": str(e)}
            ).model_dump()
        )

# Incluir routers
app.include_router(chat_router)
app.include_router(world_context_router)
app.include_router(admin_router)
app.include_router(world_router)


@app.get(
    "/health",
    responses={
        500: {"model": InternalServerError, "description": "Erro interno do servidor"}
    }
)
async def health_check() -> dict[str, str]:
    """
    Endpoint de verificação de saúde da aplicação.
    
    Returns:
        Status da aplicação.
        
    Raises:
        HTTPException: Em caso de erro na verificação
    """
    try:
        # Aqui poderia incluir verificações de conectividade com DB, etc.
        return {"status": "ok", "service": "Mestre de RPG com IA"}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=ErrorDetail(
                message="Erro na verificação de saúde",
                error_code="HEALTH_CHECK_ERROR",
                details={"original_error": str(e)}
            ).model_dump()
        )