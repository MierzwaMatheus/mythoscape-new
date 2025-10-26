"""Modelos Pydantic para tratamento de erros HTTP."""

from pydantic import BaseModel


class ErrorDetail(BaseModel):
    """Modelo base para detalhes de erro."""
    message: str
    error_code: str | None = None
    details: dict[str, str] | None = None


class HTTPError(BaseModel):
    """Modelo base para erros HTTP."""
    detail: ErrorDetail


class ValidationError(BaseModel):
    """Modelo para erros de validação (422)."""
    detail: list[dict[str, str]]


class AuthenticationError(HTTPError):
    """Modelo para erros de autenticação (401)."""
    pass


class AuthorizationError(HTTPError):
    """Modelo para erros de autorização (403)."""
    pass


class NotFoundError(HTTPError):
    """Modelo para erros de recurso não encontrado (404)."""
    pass


class InternalServerError(HTTPError):
    """Modelo para erros internos do servidor (500)."""
    pass