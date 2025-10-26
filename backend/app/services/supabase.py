"""Módulo para inicialização e configuração do cliente Supabase."""

import os
from typing import Optional
from supabase import create_client, Client

# Cache global para o cliente Supabase
_supabase_client: Optional[Client] = None


def get_supabase_client() -> Client:
    """
    Inicializa e retorna o cliente Supabase com caching singleton.
    
    Returns:
        Instância do cliente Supabase configurado.
        
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