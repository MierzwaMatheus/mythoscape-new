-- =====================================================
-- Script de configuração do banco de dados Supabase
-- para o sistema RPG com IA
-- =====================================================

-- Habilitar extensões necessárias
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS vector;

-- =====================================================
-- TABELA WORLD_CONTEXT
-- =====================================================

-- Criar tabela world_context para armazenar contexto do mundo RPG
CREATE TABLE IF NOT EXISTS world_context (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    type VARCHAR(50) NOT NULL,
    data JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Criar índices para otimização de consultas
CREATE INDEX IF NOT EXISTS idx_world_context_type ON world_context(type);
CREATE INDEX IF NOT EXISTS idx_world_context_data_gin ON world_context USING GIN(data);

-- Habilitar Row Level Security (RLS)
ALTER TABLE world_context ENABLE ROW LEVEL SECURITY;

-- Remover políticas existentes se houver
DROP POLICY IF EXISTS "Deny all access to anon and authenticated" ON world_context;
DROP POLICY IF EXISTS "Allow service_role full access" ON world_context;

-- Política que nega acesso a usuários anônimos e autenticados
CREATE POLICY "Deny all access to anon and authenticated" ON world_context
    FOR ALL
    TO anon, authenticated
    USING (false)
    WITH CHECK (false);

-- Política que permite acesso completo ao service_role
CREATE POLICY "Allow service_role full access" ON world_context
    FOR ALL
    TO service_role
    USING (true)
    WITH CHECK (true);

-- =====================================================
-- TABELA RPG_EMBEDDINGS (para RAG)
-- =====================================================

-- Criar tabela rpg_embeddings para armazenar embeddings do RAG
CREATE TABLE IF NOT EXISTS rpg_embeddings (
    id BIGSERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    metadata JSONB DEFAULT '{}',
    embedding VECTOR(1536) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Criar índices para otimização de consultas de similaridade
CREATE INDEX IF NOT EXISTS idx_rpg_embeddings_embedding ON rpg_embeddings 
    USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
CREATE INDEX IF NOT EXISTS idx_rpg_embeddings_metadata_gin ON rpg_embeddings USING GIN(metadata);

-- Habilitar Row Level Security (RLS)
ALTER TABLE rpg_embeddings ENABLE ROW LEVEL SECURITY;

-- Remover políticas existentes se houver
DROP POLICY IF EXISTS "Allow public read access for RAG" ON rpg_embeddings;
DROP POLICY IF EXISTS "Allow service_role full access for embeddings" ON rpg_embeddings;

-- Política que permite SELECT para todos (necessário para RAG)
CREATE POLICY "Allow public read access for RAG" ON rpg_embeddings
    FOR SELECT
    TO anon, authenticated, service_role
    USING (true);

-- Política que permite INSERT/UPDATE/DELETE apenas para service_role
CREATE POLICY "Allow service_role full access for embeddings" ON rpg_embeddings
    FOR ALL
    TO service_role
    USING (true)
    WITH CHECK (true);

-- =====================================================
-- FUNÇÕES AUXILIARES
-- =====================================================

-- Função para atualizar o campo updated_at automaticamente
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers para atualizar updated_at automaticamente
DROP TRIGGER IF EXISTS update_world_context_updated_at ON world_context;
CREATE TRIGGER update_world_context_updated_at
    BEFORE UPDATE ON world_context
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_rpg_embeddings_updated_at ON rpg_embeddings;
CREATE TRIGGER update_rpg_embeddings_updated_at
    BEFORE UPDATE ON rpg_embeddings
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- =====================================================
-- FUNÇÃO DE BUSCA POR SIMILARIDADE
-- =====================================================

-- Função para buscar embeddings similares (útil para RAG)
CREATE OR REPLACE FUNCTION match_embeddings(
    query_embedding VECTOR(1536),
    match_threshold FLOAT DEFAULT 0.78,
    match_count INT DEFAULT 10
)
RETURNS TABLE(
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
    WHERE 1 - (rpg_embeddings.embedding <=> query_embedding) > match_threshold
    ORDER BY rpg_embeddings.embedding <=> query_embedding
    LIMIT match_count;
$$;

-- =====================================================
-- COMENTÁRIOS E DOCUMENTAÇÃO
-- =====================================================

COMMENT ON TABLE world_context IS 'Tabela para armazenar contexto do mundo RPG (personagens, locais, eventos, etc.)';
COMMENT ON COLUMN world_context.type IS 'Tipo de entidade (character, location, event, item, etc.)';
COMMENT ON COLUMN world_context.data IS 'Dados da entidade em formato JSON';

COMMENT ON TABLE rpg_embeddings IS 'Tabela para armazenar embeddings para sistema RAG do RPG';
COMMENT ON COLUMN rpg_embeddings.content IS 'Conteúdo textual que foi convertido em embedding';
COMMENT ON COLUMN rpg_embeddings.metadata IS 'Metadados associados ao conteúdo (fonte, tipo, etc.)';
COMMENT ON COLUMN rpg_embeddings.embedding IS 'Vetor de embedding (1536 dimensões para OpenAI)';

COMMENT ON FUNCTION match_embeddings IS 'Função para buscar embeddings similares baseado em cosine similarity';

-- =====================================================
-- VERIFICAÇÃO FINAL
-- =====================================================

-- Verificar se as tabelas foram criadas corretamente
DO $$
BEGIN
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'world_context') THEN
        RAISE NOTICE 'Tabela world_context criada com sucesso';
    END IF;
    
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'rpg_embeddings') THEN
        RAISE NOTICE 'Tabela rpg_embeddings criada com sucesso';
    END IF;
END $$;