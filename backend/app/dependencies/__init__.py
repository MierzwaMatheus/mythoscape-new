"""Módulo de dependências FastAPI para autenticação e autorização."""

from .auth import get_authenticated_user, get_optional_user, AuthenticatedUser, OptionalUser

__all__ = ["get_authenticated_user", "get_optional_user", "AuthenticatedUser", "OptionalUser"]