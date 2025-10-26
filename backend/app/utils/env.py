"""Módulo para carregamento de variáveis de ambiente."""

import os
from pathlib import Path
from dotenv import load_dotenv


def load_env() -> None:
    """
    Carrega variáveis de ambiente do arquivo .env.local na raiz do projeto.
    """
    # Obtém o diretório raiz do projeto (backend)
    root_dir = Path(__file__).parent.parent.parent
    env_file = root_dir / ".env.local"
    
    # Carrega o arquivo .env.local se existir
    if env_file.exists():
        load_dotenv(env_file)
    else:
        # Fallback para .env se .env.local não existir
        load_dotenv()


def get_env_var(var_name: str, default: str = None) -> str:
    """
    Obtém uma variável de ambiente.
    
    Args:
        var_name: Nome da variável de ambiente
        default: Valor padrão se a variável não existir
        
    Returns:
        Valor da variável de ambiente
        
    Raises:
        ValueError: Se a variável não estiver definida e não houver valor padrão
    """
    load_env()
    value = os.getenv(var_name, default)
    if value is None:
        raise ValueError(f"{var_name} não está definida nas variáveis de ambiente")
    return value


def get_supabase_url() -> str:
    """
    Obtém a URL do Supabase das variáveis de ambiente.
    
    Returns:
        URL do Supabase
        
    Raises:
        ValueError: Se a variável não estiver definida
    """
    load_env()
    url = os.getenv("SUPABASE_URL")
    if not url:
        raise ValueError("SUPABASE_URL não está definida nas variáveis de ambiente")
    return url


def get_supabase_anon_key() -> str:
    """
    Obtém a chave anônima do Supabase das variáveis de ambiente.
    
    Returns:
        Chave anônima do Supabase
        
    Raises:
        ValueError: Se a variável não estiver definida
    """
    load_env()
    key = os.getenv("SUPABASE_ANON_KEY")
    if not key:
        raise ValueError("SUPABASE_ANON_KEY não está definida nas variáveis de ambiente")
    return key


def get_supabase_service_key() -> str:
    """
    Obtém a chave de service role do Supabase das variáveis de ambiente.
    
    Returns:
        Chave de service role do Supabase
        
    Raises:
        ValueError: Se a variável não estiver definida
    """
    load_env()
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    if not key:
        raise ValueError("SUPABASE_SERVICE_ROLE_KEY não está definida nas variáveis de ambiente")
    return key