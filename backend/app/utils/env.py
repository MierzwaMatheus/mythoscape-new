"""Módulo para carregamento de variáveis de ambiente."""

from dotenv import load_dotenv


def load_env() -> None:
    """
    Carrega variáveis de ambiente do arquivo .env na raiz do projeto.
    """
    load_dotenv()