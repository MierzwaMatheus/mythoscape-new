"""Dependências FastAPI para autenticação e autorização."""

from typing import Annotated
from fastapi import Depends, HTTPException, status, Request

from app.middleware.auth import jwt_bearer, get_current_user_id, is_localhost_request


async def get_authenticated_user(
    request: Request,
    token: Annotated[str, Depends(jwt_bearer)]
) -> str:
    """
    Dependência que garante que o usuário está autenticado.
    Permite acesso do localhost em desenvolvimento.
    
    Args:
        request: Requisição HTTP do FastAPI
        token: Token JWT validado pelo middleware
        
    Returns:
        ID do usuário autenticado
        
    Raises:
        HTTPException: Se o usuário não estiver autenticado
    """
    # Em desenvolvimento, permite acesso do localhost sem autenticação
    if is_localhost_request(request):
        return "localhost_user"  # ID fictício para desenvolvimento
    
    # Em produção, exige autenticação válida
    try:
        user_id = get_current_user_id(token)
        return user_id
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Falha na autenticação do usuário",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e


async def get_optional_user(
    request: Request,
    token: Annotated[str | None, Depends(jwt_bearer)] = None
) -> str | None:
    """
    Dependência que permite acesso opcional (com ou sem autenticação).
    Útil para endpoints que podem funcionar com usuários anônimos.
    
    Args:
        request: Requisição HTTP do FastAPI
        token: Token JWT opcional
        
    Returns:
        ID do usuário se autenticado, None caso contrário
    """
    # Se é localhost, sempre permite
    if is_localhost_request(request):
        return "localhost_user"
    
    # Se não há token, retorna None (usuário anônimo)
    if not token:
        return None
    
    # Se há token, tenta extrair o ID do usuário
    try:
        return get_current_user_id(token)
    except Exception:
        # Se o token é inválido, trata como usuário anônimo
        return None


# Aliases para facilitar o uso
AuthenticatedUser = Annotated[str, Depends(get_authenticated_user)]
OptionalUser = Annotated[str | None, Depends(get_optional_user)]