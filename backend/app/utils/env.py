"""Módulo para carregamento de variáveis de ambiente."""

import os
from pathlib import Path
from dotenv import load_dotenv


def load_env() -> None:
    """
    Carrega variáveis de ambiente do arquivo .env.local na raiz do projeto.
    Implementa um parser personalizado para lidar com prompts multilinhas.
    """
    # Obtém o diretório raiz do projeto (backend)
    root_dir = Path(__file__).parent.parent.parent
    env_file = root_dir / ".env.local"
    
    # Se o arquivo não existir, tenta o fallback para .env
    if not env_file.exists():
        env_file = root_dir / ".env"
        if not env_file.exists():
            return
    
    # Parser personalizado para lidar com prompts multilinhas
    try:
        with open(env_file, 'r', encoding='utf-8') as f:
            current_var = None
            current_value = ""
            
            for line in f:
                line = line.strip()
                
                # Linha vazia - finaliza a variável atual se existir
                if not line:
                    if current_var and current_value:
                        os.environ[current_var] = current_value
                        current_var = None
                        current_value = ""
                    continue
                
                # Comentário - ignora
                if line.startswith('#'):
                    continue
                
                # Nova variável
                if '=' in line and not current_var:
                    parts = line.split('=', 1)
                    current_var = parts[0].strip()
                    current_value = parts[1].strip()
                    
                    # Se a variável já foi definida completamente
                    if not current_value.endswith('\\'):
                        os.environ[current_var] = current_value
                        current_var = None
                        current_value = ""
                    else:
                        # Remove o caractere de continuação
                        current_value = current_value[:-1]
                
                # Continuação de uma variável existente
                elif current_var:
                    if line.endswith('\\'):
                        current_value += line[:-1] + "\n"
                    else:
                        current_value += line + "\n"
            
            # Finaliza a última variável se existir
            if current_var and current_value:
                os.environ[current_var] = current_value
    except Exception as e:
        print(f"Erro ao carregar variáveis de ambiente: {e}")


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