"""Aplicação principal FastAPI para o Mestre de RPG com IA."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.utils.env import load_env
from app.routers.chat import router as chat_router

# Carrega variáveis de ambiente
load_env()

# Inicializa a aplicação FastAPI
app = FastAPI(
    title="Mestre de RPG com IA",
    description="API para sistema de RPG assistido por Inteligência Artificial",
    version="1.0.0"
)

# Configuração do CORS para aceitar todas as origens
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclui o roteador de chat
app.include_router(chat_router)


@app.get("/health")
async def health_check() -> dict[str, str]:
    """
    Endpoint de verificação de saúde da aplicação.
    
    Returns:
        Status da aplicação.
    """
    return {"status": "ok"}