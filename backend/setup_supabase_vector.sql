-- Script para configurar o Supabase Vector Store
-- Execute este script no SQL Editor do Supabase

-- 1. Habilitar a extensão pgvector
CREATE EXTENSION IF NOT EXISTS vector;

-- 2. Criar a tabela para embeddings do RPG
CREATE TABLE IF NOT EXISTS rpg_embeddings (
    id BIGSERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    metadata JSONB DEFAULT '{}',
    embedding VECTOR(1536) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 3. Criar índice para busca vetorial eficiente
CREATE INDEX IF NOT EXISTS rpg_embeddings_embedding_idx 
ON rpg_embeddings USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- 4. Criar índices para metadados (otimização de filtros)
CREATE INDEX IF NOT EXISTS rpg_embeddings_metadata_gin_idx 
ON rpg_embeddings USING GIN (metadata);

CREATE INDEX IF NOT EXISTS rpg_embeddings_metadata_entity_type_idx 
ON rpg_embeddings USING BTREE ((metadata->>'entity_type'));

CREATE INDEX IF NOT EXISTS rpg_embeddings_metadata_entity_id_idx 
ON rpg_embeddings USING BTREE ((metadata->>'entity_id'));

-- 5. Criar função para busca híbrida (opcional - para uso futuro)
CREATE OR REPLACE FUNCTION search_rpg_embeddings(
    query_embedding VECTOR(1536),
    match_threshold FLOAT DEFAULT 0.8,
    match_count INT DEFAULT 4,
    filter_entity_type TEXT DEFAULT NULL
)
RETURNS TABLE (
    id BIGINT,
    content TEXT,
    metadata JSONB,
    similarity FLOAT
)
LANGUAGE SQL STABLE
AS $$
    SELECT 
        rpg_embeddings.id,
        rpg_embeddings.content,
        rpg_embeddings.metadata,
        1 - (rpg_embeddings.embedding <=> query_embedding) AS similarity
    FROM rpg_embeddings
    WHERE 
        1 - (rpg_embeddings.embedding <=> query_embedding) > match_threshold
        AND (filter_entity_type IS NULL OR metadata->>'entity_type' = filter_entity_type)
    ORDER BY rpg_embeddings.embedding <=> query_embedding
    LIMIT match_count;
$$;

-- 6. Configurar RLS (Row Level Security) se necessário
-- ALTER TABLE rpg_embeddings ENABLE ROW LEVEL SECURITY;

-- 7. Verificar se tudo foi criado corretamente
SELECT 
    'Extensão pgvector' as componente,
    CASE WHEN EXISTS (
        SELECT 1 FROM pg_extension WHERE extname = 'vector'
    ) THEN 'Habilitada ✓' ELSE 'Não encontrada ✗' END as status
UNION ALL
SELECT 
    'Tabela rpg_embeddings' as componente,
    CASE WHEN EXISTS (
        SELECT 1 FROM information_schema.tables 
        WHERE table_name = 'rpg_embeddings'
    ) THEN 'Criada ✓' ELSE 'Não encontrada ✗' END as status
UNION ALL
SELECT 
    'Função search_rpg_embeddings' as componente,
    CASE WHEN EXISTS (
        SELECT 1 FROM information_schema.routines 
        WHERE routine_name = 'search_rpg_embeddings'
    ) THEN 'Criada ✓' ELSE 'Não encontrada ✗' END as status;