"""Módulo para inicialização e configuração do cliente Supabase."""

import os
from typing import Optional
from supabase import create_client, Client

# Cache global para os clientes Supabase
_supabase_client: Optional[Client] = None
_supabase_admin_client: Optional[Client] = None


def get_supabase_client() -> Client:
    """
    Inicializa e retorna o cliente Supabase com caching singleton.
    
    Returns:
        Instância do cliente Supabase configurado com chave anônima.
        
    Raises:
        ValueError: Se as variáveis de ambiente necessárias não estiverem definidas.
    """
    global _supabase_client
    
    if _supabase_client is None:
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_ANON_KEY")
        
        if not url or not key:
            raise ValueError("SUPABASE_URL e SUPABASE_ANON_KEY devem estar definidas nas variáveis de ambiente")
        
        _supabase_client = create_client(url, key)
    
    return _supabase_client


def get_supabase_admin_client() -> Client:
    """
    Inicializa e retorna o cliente Supabase com privilégios de administrador.
    Este cliente pode fazer bypass das políticas RLS.
    
    Returns:
        Instância do cliente Supabase configurado com chave de serviço.
        
    Raises:
        ValueError: Se as variáveis de ambiente necessárias não estiverem definidas.
    """
    global _supabase_admin_client
    
    if _supabase_admin_client is None:
        url = os.getenv("SUPABASE_URL")
        # Usa a chave de service role para bypass do RLS
        key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        
        if not url or not key:
            raise ValueError("SUPABASE_URL e SUPABASE_SERVICE_ROLE_KEY devem estar definidas nas variáveis de ambiente")
        
        _supabase_admin_client = create_client(url, key)
    
    return _supabase_admin_client