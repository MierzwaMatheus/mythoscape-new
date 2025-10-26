"""
Configuração do banco de dados SQLAlchemy com Supabase.
"""

from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from app.utils.env import get_env_var


class Base(DeclarativeBase):
    """Classe base para todos os modelos SQLAlchemy."""
    pass


# Configuração do engine assíncrono
def get_database_url() -> str:
    """
    Constrói a URL de conexão com o banco de dados Supabase.
    
    Returns:
        str: URL de conexão formatada para PostgreSQL assíncrono
    """
    supabase_url = get_env_var("SUPABASE_URL")
    supabase_service_key = get_env_var("SUPABASE_SERVICE_ROLE_KEY")
    
    # Extrai o host da URL do Supabase
    # Formato: https://project-id.supabase.co
    host = supabase_url.replace("https://", "").replace("http://", "")
    
    # Constrói a URL de conexão PostgreSQL
    return f"postgresql+asyncpg://postgres:{supabase_service_key}@{host}:5432/postgres"


# Engine assíncrono
engine = create_async_engine(
    get_database_url(),
    echo=False,  # Set to True for SQL logging in development
    pool_pre_ping=True,
    pool_recycle=300,
)

# Session factory assíncrona
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependência para obter sessão do banco de dados.
    
    Yields:
        AsyncSession: Sessão assíncrona do SQLAlchemy
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()