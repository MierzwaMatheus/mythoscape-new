"""Módulo para gerenciamento do banco de vetores usando Supabase Vector Store."""

import os
from typing import Optional
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import SupabaseVectorStore

from .supabase import get_supabase_client

# Constantes de configuração
TABLE_NAME = "rpg_embeddings"
EMBEDDING_MODEL = "text-embedding-3-small"  # Modelo mais eficiente da OpenAI


class VectorStoreManager:
    """
    Gerenciador do banco de vetores para armazenamento e busca semântica de documentos.
    
    Utiliza o Supabase Vector Store com embeddings da OpenAI para implementar
    funcionalidades de RAG (Retrieval Augmented Generation) no contexto do RPG.
    
    Note: O SupabaseVectorStore da langchain-community já inclui suporte nativo
    para Supabase Vector, eliminando a necessidade de langchain-supabase.
    """
    
    def __init__(self) -> None:
        """
        Inicializa o gerenciador com modelo de embeddings e conexão com Supabase.
        
        Raises:
            ValueError: Se a chave da OpenAI não estiver configurada.
        """
        # Validação da chave da API
        if not os.getenv("OPENAI_API_KEY"):
            raise ValueError("OPENAI_API_KEY deve estar definida nas variáveis de ambiente")
        
        # Inicialização otimizada do modelo de embeddings
        self._embeddings = OpenAIEmbeddings(
            model=EMBEDDING_MODEL,
            show_progress_bar=False  # Performance: evita overhead desnecessário
        )
        
        # Inicialização do vector store com cliente Supabase
        self._vector_store = SupabaseVectorStore(
            client=get_supabase_client(),
            embedding=self._embeddings,
            table_name=TABLE_NAME
        )
    
    async def add_documents(
        self, 
        documents: list[Document], 
        entity_id: str, 
        entity_type: str
    ) -> list[str]:
        """
        Adiciona documentos ao banco de vetores com metadados de entidade.
        
        Conforme especificado no PRD (Seção 5.4), cada documento recebe metadados
        que servem como elo de ligação com o registro estruturado no JSONB.
        
        Args:
            documents: Lista de documentos a serem inseridos.
            entity_id: ID único da entidade no banco JSONB.
            entity_type: Tipo da entidade (npc, location, knowledge).
            
        Returns:
            Lista de IDs dos documentos inseridos.
        """
        # Otimização: adiciona metadados em batch para todos os documentos
        for doc in documents:
            doc.metadata.update({
                "entity_id": entity_id,
                "entity_type": entity_type
            })
        
        # Inserção assíncrona para melhor performance
        return await self._vector_store.aadd_documents(documents)
    
    async def similarity_search(
        self, 
        query: str, 
        k: int = 4,
        filter_metadata: Optional[dict[str, str]] = None
    ) -> list[Document]:
        """
        Realiza busca semântica no banco de vetores.
        
        Args:
            query: Consulta em linguagem natural.
            k: Número de documentos mais relevantes a retornar.
            filter_metadata: Filtros opcionais por metadados (ex: entity_type).
            
        Returns:
            Lista de documentos mais relevantes ordenados por similaridade.
        """
        # Busca assíncrona otimizada
        if filter_metadata:
            return await self._vector_store.asimilarity_search(
                query=query,
                k=k,
                filter=filter_metadata
            )
        
        return await self._vector_store.asimilarity_search(query=query, k=k)
    
    async def similarity_search_with_score(
        self, 
        query: str, 
        k: int = 4
    ) -> list[tuple[Document, float]]:
        """
        Busca semântica com scores de similaridade.
        
        Args:
            query: Consulta em linguagem natural.
            k: Número de documentos a retornar.
            
        Returns:
            Lista de tuplas (documento, score) ordenadas por relevância.
        """
        return await self._vector_store.asimilarity_search_with_score(query=query, k=k)
    
    def get_vector_store(self) -> SupabaseVectorStore:
        """
        Retorna a instância do vector store para uso avançado.
        
        Returns:
            Instância configurada do SupabaseVectorStore.
        """
        return self._vector_store