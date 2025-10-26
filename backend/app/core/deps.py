"""
Dependências centrais do FastAPI.
"""

from typing import AsyncGenerator
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db as get_database_session
from app.dependencies.auth import get_authenticated_user
from app.models.user import User


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependência para obter sessão do banco de dados.
    
    Yields:
        AsyncSession: Sessão assíncrona do SQLAlchemy
    """
    async for session in get_database_session():
        yield session


async def get_current_user(
    user_id: str = Depends(get_authenticated_user),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Dependência para obter o usuário atual autenticado.
    
    Args:
        user_id: ID do usuário obtido da autenticação
        db: Sessão do banco de dados
        
    Returns:
        User: Objeto do usuário atual
        
    Raises:
        HTTPException: Se o usuário não for encontrado
    """
    # Para desenvolvimento com localhost, cria usuário mock
    if user_id == "localhost_user":
        return User(
            id="localhost_user",
            email="dev@localhost.com",
            name="Usuário de Desenvolvimento",
            is_active=True
        )
    
    # TODO: Implementar busca real do usuário no banco de dados
    # Por enquanto, retorna usuário mock baseado no ID
    return User(
        id=user_id,
        email=f"user_{user_id}@example.com",
        name=f"Usuário {user_id}",
        is_active=True
    )