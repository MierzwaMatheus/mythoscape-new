"""
Utilitário de cache para o sistema multiagente.
"""

import json
import asyncio
from typing import Optional, Any, Union
from datetime import datetime, timedelta
from app.utils.env import get_env_var


class CacheManager:
    """Gerenciador de cache simples baseado em memória."""
    
    def __init__(self):
        self._cache: dict[str, dict] = {}
        self._cleanup_task = None
        self._start_cleanup_task()
    
    async def get(self, key: str) -> Optional[Any]:
        """Recupera um valor do cache."""
        
        if key not in self._cache:
            return None
        
        entry = self._cache[key]
        
        # Verifica se expirou
        if entry["expires_at"] and datetime.now() > entry["expires_at"]:
            del self._cache[key]
            return None
        
        return entry["value"]
    
    async def set(
        self, 
        key: str, 
        value: Any, 
        expire_seconds: Optional[int] = None
    ) -> None:
        """Armazena um valor no cache."""
        
        expires_at = None
        if expire_seconds:
            expires_at = datetime.now() + timedelta(seconds=expire_seconds)
        
        self._cache[key] = {
            "value": value,
            "created_at": datetime.now(),
            "expires_at": expires_at
        }
    
    async def delete(self, key: str) -> bool:
        """Remove um valor do cache."""
        
        if key in self._cache:
            del self._cache[key]
            return True
        
        return False
    
    async def delete_pattern(self, pattern: str) -> int:
        """Remove valores do cache que correspondem ao padrão."""
        
        # Implementação simples de pattern matching
        # Suporta apenas wildcards no final (*)
        if pattern.endswith("*"):
            prefix = pattern[:-1]
            keys_to_delete = [
                key for key in self._cache.keys() 
                if key.startswith(prefix)
            ]
        else:
            keys_to_delete = [key for key in self._cache.keys() if key == pattern]
        
        for key in keys_to_delete:
            del self._cache[key]
        
        return len(keys_to_delete)
    
    async def clear(self) -> None:
        """Limpa todo o cache."""
        self._cache.clear()
    
    async def size(self) -> int:
        """Retorna o número de entradas no cache."""
        return len(self._cache)
    
    async def keys(self) -> list[str]:
        """Retorna todas as chaves do cache."""
        return list(self._cache.keys())
    
    def _start_cleanup_task(self) -> None:
        """Inicia tarefa de limpeza automática do cache."""
        
        if self._cleanup_task is None:
            self._cleanup_task = asyncio.create_task(self._cleanup_expired())
    
    async def _cleanup_expired(self) -> None:
        """Remove entradas expiradas do cache periodicamente."""
        
        while True:
            try:
                await asyncio.sleep(300)  # Executa a cada 5 minutos
                
                now = datetime.now()
                expired_keys = []
                
                for key, entry in self._cache.items():
                    if entry["expires_at"] and now > entry["expires_at"]:
                        expired_keys.append(key)
                
                for key in expired_keys:
                    del self._cache[key]
                    
            except asyncio.CancelledError:
                break
            except Exception:
                # Continua em caso de erro
                continue
    
    def __del__(self):
        """Cancela a tarefa de limpeza ao destruir o objeto."""
        if self._cleanup_task:
            self._cleanup_task.cancel()


# Cache global para uso em dependências
_global_cache = None


def get_cache_manager() -> CacheManager:
    """Retorna instância global do gerenciador de cache."""
    global _global_cache
    
    if _global_cache is None:
        _global_cache = CacheManager()
    
    return _global_cache


# Dependência para FastAPI
def get_cache() -> CacheManager:
    """Dependência do FastAPI para injeção do cache."""
    return get_cache_manager()