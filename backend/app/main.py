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

# Configuração do CORS para localhost:8080
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Endpoint POST /chat
@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest) -> ChatResponse:
    """
    Endpoint principal de chat com o Mestre de RPG.
    
    Args:
        request: Requisição contendo o prompt do jogador.
        
    Returns:
        Resposta do agente RPG formatada.
    """
    try:
        response = await rpg_agent.run(request.prompt)
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