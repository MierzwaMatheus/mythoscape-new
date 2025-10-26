"""Aplicação principal FastAPI para o Mestre de RPG com IA."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.utils.env import load_env

# Carrega variáveis de ambiente ANTES de qualquer importação que dependa delas
load_env()

# Agora importa o RPGAgent após carregar as variáveis de ambiente
from app.agents.rpg_agent import RPGAgent
from app.routers.chat import router as chat_router
from app.dependencies.auth import AuthenticatedUser

# Inicializa o agente RPG globalmente para eficiência
rpg_agent = RPGAgent()

# Modelos Pydantic para requisição e resposta de chat
class ChatRequest(BaseModel):
    """Modelo para requisição de chat."""
    prompt: str

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
@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest, user_id: AuthenticatedUser) -> ChatResponse:
    """
    Endpoint principal de chat com o Mestre de RPG.
    Requer autenticação válida (exceto para localhost em desenvolvimento).
    
    Args:
        request: Requisição contendo o prompt do jogador.
        user_id: ID do usuário autenticado (injetado pela dependência).
        
    Returns:
        Resposta do agente RPG formatada.
    """
    try:
        # Adiciona contexto do usuário ao prompt se necessário
        enhanced_prompt = f"[Usuário: {user_id}] {request.prompt}"
        response = await rpg_agent.run(enhanced_prompt)
        return ChatResponse(response=response)
    except Exception as e:
        return ChatResponse(response=f"Erro interno: {str(e)}")

# Inclui o roteador de chat (endpoints adicionais)
app.include_router(chat_router)


@app.get("/health")
async def health_check() -> dict[str, str]:
    """
    Endpoint de verificação de saúde da aplicação.
    
    Returns:
        Status da aplicação.
    """
    return {"status": "ok"}