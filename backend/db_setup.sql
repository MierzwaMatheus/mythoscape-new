-- =====================================================
-- Script de configuração do banco de dados Supabase
-- para o sistema RPG com IA - VERSÃO IDEMPOTENTE
-- =====================================================
-- Este script pode ser executado múltiplas vezes sem problemas
-- Verifica estruturas existentes antes de modificar

-- Habilitar extensões necessárias
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS vector;

-- =====================================================
-- FUNÇÕES AUXILIARES PARA MIGRAÇÃO SEGURA
-- =====================================================

-- Função para verificar se uma coluna existe
CREATE OR REPLACE FUNCTION column_exists(p_table_name TEXT, p_column_name TEXT)
RETURNS BOOLEAN AS $$
DECLARE
    column_count INTEGER;
BEGIN
    SELECT COUNT(*)
    INTO column_count
    FROM information_schema.columns 
    WHERE table_schema = 'public' 
    AND table_name = p_table_name 
    AND column_name = p_column_name;
    
    RETURN column_count > 0;
END;
$$ LANGUAGE plpgsql;

-- Função para verificar se um índice existe
CREATE OR REPLACE FUNCTION index_exists(p_index_name TEXT)
RETURNS BOOLEAN AS $$
DECLARE
    index_count INTEGER;
BEGIN
    SELECT COUNT(*)
    INTO index_count
    FROM pg_indexes 
    WHERE schemaname = 'public' 
    AND indexname = p_index_name;
    
    RETURN index_count > 0;
END;
$$ LANGUAGE plpgsql;

-- Função para verificar se uma política RLS existe
CREATE OR REPLACE FUNCTION policy_exists(p_table_name TEXT, p_policy_name TEXT)
RETURNS BOOLEAN AS $$
DECLARE
    policy_count INTEGER;
BEGIN
    SELECT COUNT(*)
    INTO policy_count
    FROM pg_policies 
    WHERE schemaname = 'public' 
    AND tablename = p_table_name 
    AND policyname = p_policy_name;
    
    RETURN policy_count > 0;
END;
$$ LANGUAGE plpgsql;

-- Criar tabela worlds se não existir
CREATE TABLE IF NOT EXISTS worlds (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    genre_tags JSONB DEFAULT '[]',
    master_personality VARCHAR(50) DEFAULT 'serious_dark',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Verificar e adicionar colunas necessárias à tabela worlds
DO $$
BEGIN
    -- Adicionar genre_tags se não existir
    IF NOT column_exists('worlds', 'genre_tags') THEN
        ALTER TABLE worlds ADD COLUMN genre_tags JSONB DEFAULT '[]';
        RAISE NOTICE '%', 'Coluna genre_tags adicionada à tabela worlds';
    END IF;
    
    -- Adicionar master_personality se não existir
    IF NOT column_exists('worlds', 'master_personality') THEN
        ALTER TABLE worlds ADD COLUMN master_personality VARCHAR(50) DEFAULT 'serious_dark';
        RAISE NOTICE '%', 'Coluna master_personality adicionada à tabela worlds';
    END IF;
    
    -- Adicionar campaign_time se não existir
    IF NOT column_exists('worlds', 'campaign_time') THEN
        ALTER TABLE worlds ADD COLUMN campaign_time JSONB DEFAULT '{"day": 1, "hour": 12, "minute": 0, "season": "spring", "year": 1}';
        RAISE NOTICE '%', 'Coluna campaign_time adicionada à tabela worlds';
    END IF;
    
    -- Adicionar campaign_id se não existir
    IF NOT column_exists('worlds', 'campaign_id') THEN
        ALTER TABLE worlds ADD COLUMN campaign_id UUID REFERENCES campaigns(id);
        RAISE NOTICE '%', 'Coluna campaign_id adicionada à tabela worlds';
    END IF;
    
    -- Adicionar world_data se não existir
    IF NOT column_exists('worlds', 'world_data') THEN
        ALTER TABLE worlds ADD COLUMN world_data JSONB DEFAULT '{}';
        RAISE NOTICE '%', 'Coluna world_data adicionada à tabela worlds';
    END IF;
END $$;
DO $$
BEGIN
    IF NOT index_exists('idx_worlds_user_id') THEN
        CREATE INDEX idx_worlds_user_id ON worlds(user_id);
        RAISE NOTICE '%', 'Índice idx_worlds_user_id criado';
    END IF;
    
    IF NOT index_exists('idx_worlds_user_id_active') THEN
        CREATE INDEX idx_worlds_user_id_active ON worlds(user_id, is_active);
        RAISE NOTICE '%', 'Índice idx_worlds_user_id_active criado';
    END IF;
END $$;

-- Habilitar RLS se não estiver habilitado
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_tables 
        WHERE schemaname = 'public' 
        AND tablename = 'worlds' 
        AND rowsecurity = true
    ) THEN
        ALTER TABLE worlds ENABLE ROW LEVEL SECURITY;
        RAISE NOTICE '%', 'RLS habilitado para tabela worlds';
    END IF;
END $$;

-- Políticas RLS para worlds
DO $$
BEGIN
    -- Remover políticas antigas se existirem
    IF policy_exists('worlds', 'Allow service_role full access to worlds') THEN
        DROP POLICY "Allow service_role full access to worlds" ON worlds;
    END IF;
    
    IF policy_exists('worlds', 'Users can access their own worlds') THEN
        DROP POLICY "Users can access their own worlds" ON worlds;
    END IF;
    
    -- Criar políticas com isolamento por user_id
    CREATE POLICY "Allow service_role full access to worlds" ON worlds
        FOR ALL
        TO service_role
        USING (true)
        WITH CHECK (true);
    
    -- Política para usuários autenticados acessarem apenas seus próprios mundos
    CREATE POLICY "Users can access their own worlds" ON worlds
        FOR ALL
        TO authenticated
        USING (auth.uid() = user_id)
        WITH CHECK (auth.uid() = user_id);
    
    RAISE NOTICE '%', 'Políticas RLS para worlds configuradas com isolamento por user_id';
END $$;

-- =====================================================
-- TABELA CHARACTERS (Sistema de Arquétipos e Abordagens)
-- =====================================================

CREATE TABLE IF NOT EXISTS characters (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    world_id UUID NOT NULL,
    user_id UUID NOT NULL,
    name VARCHAR(255) NOT NULL,
    concept TEXT,
    archetypes JSONB DEFAULT '[]',
    approaches JSONB DEFAULT '[]',
    vitality INTEGER DEFAULT 5 CHECK (vitality >= 1 AND vitality <= 5),
    inventory JSONB DEFAULT '[]',
    active_missions JSONB DEFAULT '[]',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Verificar e adicionar colunas necessárias à tabela characters
DO $$
BEGIN
    -- Adicionar campaign_id se não existir
    IF NOT column_exists('characters', 'campaign_id') THEN
        ALTER TABLE characters ADD COLUMN campaign_id UUID REFERENCES campaigns(id);
        RAISE NOTICE '%', 'Coluna campaign_id adicionada à tabela characters';
    END IF;
    
    -- Adicionar character_class se não existir
    IF NOT column_exists('characters', 'character_class') THEN
        ALTER TABLE characters ADD COLUMN character_class VARCHAR(100);
        RAISE NOTICE '%', 'Coluna character_class adicionada à tabela characters';
    END IF;
    
    -- Adicionar level se não existir
    IF NOT column_exists('characters', 'level') THEN
        ALTER TABLE characters ADD COLUMN level INTEGER DEFAULT 1;
        RAISE NOTICE '%', 'Coluna level adicionada à tabela characters';
    END IF;
    
    -- Adicionar character_data se não existir
    IF NOT column_exists('characters', 'character_data') THEN
        ALTER TABLE characters ADD COLUMN character_data JSONB DEFAULT '{}';
        RAISE NOTICE '%', 'Coluna character_data adicionada à tabela characters';
    END IF;
END $$;

-- Adicionar foreign key constraints se não existirem
DO $$
BEGIN
    -- FK para worlds
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints 
        WHERE constraint_name = 'fk_characters_world_id' AND table_name = 'characters'
    ) THEN
        ALTER TABLE characters 
        ADD CONSTRAINT fk_characters_world_id 
        FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE;
        RAISE NOTICE '%', 'Foreign key fk_characters_world_id criada';
    END IF;
END $$;

-- Adicionar índices otimizados se não existirem
DO $$
BEGIN
    IF NOT index_exists('idx_characters_world_user') THEN
        CREATE INDEX idx_characters_world_user ON characters(world_id, user_id);
        RAISE NOTICE '%', 'Índice idx_characters_world_user criado';
    END IF;
    
    IF NOT index_exists('idx_characters_world_active') THEN
        CREATE INDEX idx_characters_world_active ON characters(world_id, is_active);
        RAISE NOTICE '%', 'Índice idx_characters_world_active criado';
    END IF;
    
    IF NOT index_exists('idx_characters_archetypes_gin') THEN
        CREATE INDEX idx_characters_archetypes_gin ON characters USING GIN(archetypes);
        RAISE NOTICE '%', 'Índice idx_characters_archetypes_gin criado';
    END IF;
    
    IF NOT index_exists('idx_characters_approaches_gin') THEN
        CREATE INDEX idx_characters_approaches_gin ON characters USING GIN(approaches);
        RAISE NOTICE '%', 'Índice idx_characters_approaches_gin criado';
    END IF;
END $$;

-- Habilitar RLS se não estiver habilitado
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_tables 
        WHERE schemaname = 'public' 
        AND tablename = 'characters' 
        AND rowsecurity = true
    ) THEN
        ALTER TABLE characters ENABLE ROW LEVEL SECURITY;
        RAISE NOTICE '%', 'RLS habilitado para tabela characters';
    END IF;
END $$;

-- Políticas RLS para characters
DO $$
BEGIN
    -- Remover políticas antigas se existirem
    IF policy_exists('characters', 'Allow service_role full access to characters') THEN
        DROP POLICY "Allow service_role full access to characters" ON characters;
    END IF;
    
    IF policy_exists('characters', 'Users can access their own characters') THEN
        DROP POLICY "Users can access their own characters" ON characters;
    END IF;
    
    -- Criar políticas com isolamento por user_id
    CREATE POLICY "Allow service_role full access to characters" ON characters
        FOR ALL
        TO service_role
        USING (true)
        WITH CHECK (true);
    
    CREATE POLICY "Users can access their own characters" ON characters
        FOR ALL
        TO authenticated
        USING (auth.uid() = user_id)
        WITH CHECK (auth.uid() = user_id);
    
    RAISE NOTICE '%', 'Políticas RLS para characters configuradas com isolamento por user_id';
END $$;

-- =====================================================
-- TABELA PLAYER_NOTES (Sistema de Anotações)
-- =====================================================

CREATE TABLE IF NOT EXISTS player_notes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    world_id UUID NOT NULL,
    user_id UUID NOT NULL,
    category VARCHAR(50) NOT NULL CHECK (category IN ('characters', 'places', 'lore', 'general')),
    title VARCHAR(255) NOT NULL,
    content TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Adicionar foreign key constraints se não existirem
DO $$
BEGIN
    -- FK para worlds
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints 
        WHERE constraint_name = 'fk_player_notes_world_id' AND table_name = 'player_notes'
    ) THEN
        ALTER TABLE player_notes 
        ADD CONSTRAINT fk_player_notes_world_id 
        FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE;
        RAISE NOTICE '%', 'Foreign key fk_player_notes_world_id criada';
    END IF;
END $$;

-- Adicionar índices otimizados se não existirem
DO $$
BEGIN
    IF NOT index_exists('idx_player_notes_world_user') THEN
        CREATE INDEX idx_player_notes_world_user ON player_notes(world_id, user_id);
        RAISE NOTICE '%', 'Índice idx_player_notes_world_user criado';
    END IF;
    
    IF NOT index_exists('idx_player_notes_category') THEN
        CREATE INDEX idx_player_notes_category ON player_notes(world_id, category);
        RAISE NOTICE '%', 'Índice idx_player_notes_category criado';
    END IF;
    
    IF NOT index_exists('idx_player_notes_title_gin') THEN
        CREATE INDEX idx_player_notes_title_gin ON player_notes USING GIN(to_tsvector('portuguese', title));
        RAISE NOTICE '%', 'Índice idx_player_notes_title_gin criado';
    END IF;
    
    IF NOT index_exists('idx_player_notes_content_gin') THEN
        CREATE INDEX idx_player_notes_content_gin ON player_notes USING GIN(to_tsvector('portuguese', content));
        RAISE NOTICE '%', 'Índice idx_player_notes_content_gin criado';
    END IF;
END $$;

-- Habilitar RLS se não estiver habilitado
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_tables 
        WHERE schemaname = 'public' 
        AND tablename = 'player_notes' 
        AND rowsecurity = true
    ) THEN
        ALTER TABLE player_notes ENABLE ROW LEVEL SECURITY;
        RAISE NOTICE '%', 'RLS habilitado para tabela player_notes';
    END IF;
END $$;

-- Políticas RLS para player_notes
DO $$
BEGIN
    -- Remover políticas antigas se existirem
    IF policy_exists('player_notes', 'Allow service_role full access to player_notes') THEN
        DROP POLICY "Allow service_role full access to player_notes" ON player_notes;
    END IF;
    
    IF policy_exists('player_notes', 'Users can access their own notes') THEN
        DROP POLICY "Users can access their own notes" ON player_notes;
    END IF;
    
    -- Criar políticas com isolamento por user_id
    CREATE POLICY "Allow service_role full access to player_notes" ON player_notes
        FOR ALL
        TO service_role
        USING (true)
        WITH CHECK (true);
    
    CREATE POLICY "Users can access their own notes" ON player_notes
        FOR ALL
        TO authenticated
        USING (auth.uid() = user_id)
        WITH CHECK (auth.uid() = user_id);
    
    RAISE NOTICE '%', 'Políticas RLS para player_notes configuradas com isolamento por user_id';
END $$;
-- Nota: Este script assume que a tabela world_context já existe.
-- Se ela não existir, você precisará de um CREATE TABLE IF NOT EXISTS.

-- Verificar e adicionar colunas necessárias à tabela world_context
DO $$
BEGIN
    -- Adicionar world_id se não existir
    IF NOT column_exists('world_context', 'world_id') THEN
        ALTER TABLE world_context ADD COLUMN world_id UUID;
        RAISE NOTICE '%', 'Coluna world_id adicionada à tabela world_context';
    END IF;
    
    -- Adicionar user_id se não existir
    IF NOT column_exists('world_context', 'user_id') THEN
        ALTER TABLE world_context ADD COLUMN user_id UUID;
        RAISE NOTICE '%', 'Coluna user_id adicionada à tabela world_context';
    END IF;
    
    -- Verificar se created_at existe, se não, adicionar
    IF NOT column_exists('world_context', 'created_at') THEN
        ALTER TABLE world_context ADD COLUMN created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW();
        RAISE NOTICE '%', 'Coluna created_at adicionada à tabela world_context';
    END IF;
    
    -- Verificar se updated_at existe, se não, adicionar
    IF NOT column_exists('world_context', 'updated_at') THEN
        ALTER TABLE world_context ADD COLUMN updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW();
        RAISE NOTICE '%', 'Coluna updated_at adicionada à tabela world_context';
    END IF;
END $$;

-- Adicionar foreign key constraints se não existirem
DO $$
BEGIN
    -- FK para worlds
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints 
        WHERE constraint_name = 'fk_world_context_world_id' AND table_name = 'world_context'
    ) THEN
        ALTER TABLE world_context 
        ADD CONSTRAINT fk_world_context_world_id 
        FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE;
        RAISE NOTICE '%', 'Foreign key fk_world_context_world_id criada';
    END IF;
END $$;

-- Adicionar índices otimizados se não existirem
DO $$
BEGIN
    IF NOT index_exists('idx_world_context_world_user') THEN
        CREATE INDEX idx_world_context_world_user ON world_context(world_id, user_id);
        RAISE NOTICE '%', 'Índice idx_world_context_world_user criado';
    END IF;
    
    IF NOT index_exists('idx_world_context_world_type') THEN
        CREATE INDEX idx_world_context_world_type ON world_context(world_id, type);
        RAISE NOTICE '%', 'Índice idx_world_context_world_type criado';
    END IF;
    
    IF NOT index_exists('idx_world_context_type') THEN
        CREATE INDEX idx_world_context_type ON world_context(type);
        RAISE NOTICE '%', 'Índice idx_world_context_type criado';
    END IF;
    
    IF NOT index_exists('idx_world_context_data_gin') THEN
        CREATE INDEX idx_world_context_data_gin ON world_context USING GIN(data);
        RAISE NOTICE '%', 'Índice idx_world_context_data_gin criado';
    END IF;
END $$;

-- Habilitar RLS se não estiver habilitado
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_tables 
        WHERE schemaname = 'public' 
        AND tablename = 'world_context' 
        AND rowsecurity = true
    ) THEN
        ALTER TABLE world_context ENABLE ROW LEVEL SECURITY;
        RAISE NOTICE '%', 'RLS habilitado para tabela world_context';
    END IF;
END $$;

-- Atualizar políticas RLS para world_context
DO $$
BEGIN
    -- Remover políticas antigas
    IF policy_exists('world_context', 'Deny all access to anon and authenticated') THEN
        DROP POLICY "Deny all access to anon and authenticated" ON world_context;
    END IF;
    
    IF policy_exists('world_context', 'Allow service_role full access') THEN
        DROP POLICY "Allow service_role full access" ON world_context;
    END IF;
    
    IF policy_exists('world_context', 'Users can access their own world contexts') THEN
        DROP POLICY "Users can access their own world contexts" ON world_context;
    END IF;
    
    -- Criar novas políticas
    CREATE POLICY "Allow service_role full access" ON world_context
        FOR ALL
        TO service_role
        USING (true)
        WITH CHECK (true);
    
    CREATE POLICY "Users can access their own world contexts" ON world_context
        FOR ALL
        TO authenticated
        USING (auth.uid() = user_id)
        WITH CHECK (auth.uid() = user_id);
    
    RAISE NOTICE '%', 'Políticas RLS para world_context atualizadas com isolamento por user_id';
END $$;

-- =====================================================
-- TABELA RPG_EMBEDDINGS (para RAG)
-- =====================================================

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

-- Índices específicos para isolamento por world_id
DO $$
BEGIN
    IF NOT index_exists('idx_rpg_embeddings_world_id') THEN
        CREATE INDEX idx_rpg_embeddings_world_id ON rpg_embeddings USING BTREE ((metadata->>'world_id'));
        RAISE NOTICE '%', 'Índice idx_rpg_embeddings_world_id criado';
    END IF;
    
    IF NOT index_exists('idx_rpg_embeddings_world_entity') THEN
        CREATE INDEX idx_rpg_embeddings_world_entity ON rpg_embeddings USING BTREE ((metadata->>'world_id'), (metadata->>'entity_id'));
        RAISE NOTICE '%', 'Índice idx_rpg_embeddings_world_entity criado';
    END IF;
    
    IF NOT index_exists('idx_rpg_embeddings_world_type') THEN
        CREATE INDEX idx_rpg_embeddings_world_type ON rpg_embeddings USING BTREE ((metadata->>'world_id'), (metadata->>'entity_type'));
        RAISE NOTICE '%', 'Índice idx_rpg_embeddings_world_type criado';
    END IF;
END $$;

-- Habilitar Row Level Security (RLS)
ALTER TABLE rpg_embeddings ENABLE ROW LEVEL SECURITY;

-- Remover políticas existentes para garantir idempotência
DROP POLICY IF EXISTS "Allow public read access for RAG" ON rpg_embeddings;
DROP POLICY IF EXISTS "Allow service_role full access for embeddings" ON rpg_embeddings;

-- Criar novas políticas
CREATE POLICY "Allow public read access for RAG" ON rpg_embeddings
    FOR SELECT
    TO anon, authenticated, service_role
    USING (true);

CREATE POLICY "Allow service_role full access for embeddings" ON rpg_embeddings
    FOR ALL
    TO service_role
    USING (true)
    WITH CHECK (true);

-- =====================================================
-- FUNÇÕES AUXILIARES
-- =====================================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Triggers para atualizar updated_at automaticamente
DROP TRIGGER IF EXISTS update_worlds_updated_at ON worlds;
CREATE TRIGGER update_worlds_updated_at
    BEFORE UPDATE ON worlds
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

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

CREATE OR REPLACE FUNCTION match_embeddings(
    query_embedding VECTOR(1536),
    match_threshold FLOAT DEFAULT 0.78,
    match_count INT DEFAULT 10
)
RETURNS TABLE(id BIGINT, content TEXT, metadata JSONB, similarity FLOAT)
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

CREATE OR REPLACE FUNCTION match_embeddings_by_world(
    query_embedding VECTOR(1536),
    world_id_filter TEXT,
    match_threshold FLOAT DEFAULT 0.78,
    match_count INT DEFAULT 10
)
RETURNS TABLE(id BIGINT, content TEXT, metadata JSONB, similarity FLOAT)
LANGUAGE SQL STABLE
AS $$
    SELECT
        rpg_embeddings.id,
        rpg_embeddings.content,
        rpg_embeddings.metadata,
        1 - (rpg_embeddings.embedding <=> query_embedding) AS similarity
    FROM rpg_embeddings
    WHERE 
        (metadata->>'world_id') = world_id_filter
        AND 1 - (rpg_embeddings.embedding <=> query_embedding) > match_threshold
    ORDER BY rpg_embeddings.embedding <=> query_embedding
    LIMIT match_count;
$$;

-- =====================================================
-- TABELA MISSIONS (Sistema de Missões Dinâmicas)
-- =====================================================

CREATE TABLE IF NOT EXISTS missions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    world_id UUID NOT NULL,
    user_id UUID NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'completed', 'failed', 'expired')),
    created_at_ingame JSONB DEFAULT '{"day": 1, "hour": 12, "minute": 0, "season": "spring", "year": 1}',
    expires_at_ingame JSONB,
    plot_twist_trigger TEXT,
    secret_plot_info TEXT,
    success_outcome TEXT,
    failure_outcome TEXT,
    expiration_outcome TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Adicionar foreign key constraints se não existirem
DO $$
BEGIN
    -- FK para worlds
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints 
        WHERE constraint_name = 'fk_missions_world_id' AND table_name = 'missions'
    ) THEN
        ALTER TABLE missions 
        ADD CONSTRAINT fk_missions_world_id 
        FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE CASCADE;
        RAISE NOTICE '%', 'Foreign key fk_missions_world_id criada';
    END IF;
END $$;

-- Adicionar índices otimizados se não existirem
DO $$
BEGIN
    IF NOT index_exists('idx_missions_world_user') THEN
        CREATE INDEX idx_missions_world_user ON missions(world_id, user_id);
        RAISE NOTICE '%', 'Índice idx_missions_world_user criado';
    END IF;
    
    IF NOT index_exists('idx_missions_world_status') THEN
        CREATE INDEX idx_missions_world_status ON missions(world_id, status);
        RAISE NOTICE '%', 'Índice idx_missions_world_status criado';
    END IF;
    
    IF NOT index_exists('idx_missions_expires_at_gin') THEN
        CREATE INDEX idx_missions_expires_at_gin ON missions USING GIN(expires_at_ingame);
        RAISE NOTICE '%', 'Índice idx_missions_expires_at_gin criado';
    END IF;
END $$;

-- Habilitar RLS se não estiver habilitado
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_tables 
        WHERE schemaname = 'public' 
        AND tablename = 'missions' 
        AND rowsecurity = true
    ) THEN
        ALTER TABLE missions ENABLE ROW LEVEL SECURITY;
        RAISE NOTICE '%', 'RLS habilitado para tabela missions';
    END IF;
END $$;

-- Políticas RLS para missions
DO $$
BEGIN
    -- Remover políticas antigas se existirem
    IF policy_exists('missions', 'Allow service_role full access to missions') THEN
        DROP POLICY "Allow service_role full access to missions" ON missions;
    END IF;
    
    IF policy_exists('missions', 'Users can access their own missions') THEN
        DROP POLICY "Users can access their own missions" ON missions;
    END IF;
    
    -- Criar políticas com isolamento por user_id
    CREATE POLICY "Allow service_role full access to missions" ON missions
        FOR ALL
        TO service_role
        USING (true)
        WITH CHECK (true);
    
    -- Política para usuários autenticados acessarem apenas suas próprias missões
    CREATE POLICY "Users can access their own missions" ON missions
        FOR ALL
        TO authenticated
        USING (auth.uid() = user_id)
        WITH CHECK (auth.uid() = user_id);
    
    RAISE NOTICE '%', 'Políticas RLS para missions configuradas com isolamento por user_id';
END $$;

-- =====================================================
-- COMENTÁRIOS E DOCUMENTAÇÃO
-- =====================================================

COMMENT ON TABLE worlds IS 'Armazena os mundos criados pelos usuários.';
COMMENT ON TABLE world_context IS 'Tabela para armazenar contexto do mundo RPG (personagens, locais, eventos, etc.)';
COMMENT ON COLUMN world_context.type IS 'Tipo de entidade (character, location, event, item, etc.)';
COMMENT ON COLUMN world_context.data IS 'Dados da entidade em formato JSON';
COMMENT ON TABLE rpg_embeddings IS 'Tabela para armazenar embeddings para sistema RAG do RPG';
COMMENT ON COLUMN rpg_embeddings.content IS 'Conteúdo textual que foi convertido em embedding';
COMMENT ON COLUMN rpg_embeddings.metadata IS 'Metadados associados ao conteúdo (world_id, entity_id, etc.)';
COMMENT ON COLUMN rpg_embeddings.embedding IS 'Vetor de embedding (1536 dimensões para OpenAI)';
COMMENT ON TABLE characters IS 'Armazena os personagens dos jogadores com sistema SAA';
COMMENT ON TABLE player_notes IS 'Armazena as anotações organizadas dos jogadores';
COMMENT ON TABLE missions IS 'Armazena as missões dinâmicas com prazos e plot twists';
COMMENT ON COLUMN missions.created_at_ingame IS 'Tempo do jogo quando a missão foi criada';
COMMENT ON COLUMN missions.expires_at_ingame IS 'Tempo do jogo quando a missão expira';
COMMENT ON COLUMN missions.plot_twist_trigger IS 'Condição que ativa um plot twist';
COMMENT ON COLUMN missions.secret_plot_info IS 'Informações secretas que apenas a IA conhece';
COMMENT ON FUNCTION match_embeddings IS 'Função para buscar embeddings similares baseado em cosine similarity';
COMMENT ON FUNCTION match_embeddings_by_world IS 'Função para buscar embeddings similares em um mundo específico';

-- =====================================================
-- TABELA EXECUTION_LOGS (Sistema de Logs de Execução do Multiagente)
-- =====================================================

CREATE TABLE IF NOT EXISTS execution_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL,
    input_text TEXT NOT NULL,
    output_narrative TEXT,
    execution_time FLOAT DEFAULT 0.0,
    agents_used JSONB DEFAULT '[]',
    success BOOLEAN DEFAULT true,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Adicionar índices otimizados se não existirem
DO $$
BEGIN
    IF NOT index_exists('idx_execution_logs_user_id') THEN
        CREATE INDEX idx_execution_logs_user_id ON execution_logs(user_id);
        RAISE NOTICE '%', 'Índice idx_execution_logs_user_id criado';
    END IF;
    
    IF NOT index_exists('idx_execution_logs_user_created') THEN
        CREATE INDEX idx_execution_logs_user_created ON execution_logs(user_id, created_at DESC);
        RAISE NOTICE '%', 'Índice idx_execution_logs_user_created criado';
    END IF;
    
    IF NOT index_exists('idx_execution_logs_success') THEN
        CREATE INDEX idx_execution_logs_success ON execution_logs(success);
        RAISE NOTICE '%', 'Índice idx_execution_logs_success criado';
    END IF;
    
    IF NOT index_exists('idx_execution_logs_agents_gin') THEN
        CREATE INDEX idx_execution_logs_agents_gin ON execution_logs USING GIN(agents_used);
        RAISE NOTICE '%', 'Índice idx_execution_logs_agents_gin criado';
    END IF;
    
    IF NOT index_exists('idx_execution_logs_metadata_gin') THEN
        CREATE INDEX idx_execution_logs_metadata_gin ON execution_logs USING GIN(metadata);
        RAISE NOTICE '%', 'Índice idx_execution_logs_metadata_gin criado';
    END IF;
END $$;

-- Habilitar RLS se não estiver habilitado
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_tables 
        WHERE schemaname = 'public' 
        AND tablename = 'execution_logs' 
        AND rowsecurity = true
    ) THEN
        ALTER TABLE execution_logs ENABLE ROW LEVEL SECURITY;
        RAISE NOTICE '%', 'RLS habilitado para tabela execution_logs';
    END IF;
END $$;

-- Políticas RLS para execution_logs
DO $$
BEGIN
    -- Remover políticas antigas se existirem
    IF policy_exists('execution_logs', 'Allow service_role full access to execution_logs') THEN
        DROP POLICY "Allow service_role full access to execution_logs" ON execution_logs;
    END IF;
    
    IF policy_exists('execution_logs', 'Users can access their own execution logs') THEN
        DROP POLICY "Users can access their own execution logs" ON execution_logs;
    END IF;
    
    -- Criar políticas com isolamento por user_id
    CREATE POLICY "Allow service_role full access to execution_logs" ON execution_logs
        FOR ALL
        TO service_role
        USING (true)
        WITH CHECK (true);
    
    CREATE POLICY "Users can access their own execution logs" ON execution_logs
        FOR ALL
        TO authenticated
        USING (auth.uid() = user_id)
        WITH CHECK (auth.uid() = user_id);
    
    RAISE NOTICE '%', 'Políticas RLS para execution_logs configuradas com isolamento por user_id';
END $$;

-- =====================================================
-- TABELA USERS (Sistema de Usuários)
-- =====================================================

CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255),
    avatar_url TEXT,
    is_active BOOLEAN DEFAULT true,
    preferences JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_login TIMESTAMP WITH TIME ZONE
);

-- Adicionar índices otimizados se não existirem
DO $$
BEGIN
    IF NOT index_exists('idx_users_email') THEN
        CREATE UNIQUE INDEX idx_users_email ON users(email);
        RAISE NOTICE '%', 'Índice idx_users_email criado';
    END IF;
    
    IF NOT index_exists('idx_users_active') THEN
        CREATE INDEX idx_users_active ON users(is_active);
        RAISE NOTICE '%', 'Índice idx_users_active criado';
    END IF;
    
    IF NOT index_exists('idx_users_preferences_gin') THEN
        CREATE INDEX idx_users_preferences_gin ON users USING GIN(preferences);
        RAISE NOTICE '%', 'Índice idx_users_preferences_gin criado';
    END IF;
END $$;

-- Habilitar RLS se não estiver habilitado
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_tables 
        WHERE schemaname = 'public' 
        AND tablename = 'users' 
        AND rowsecurity = true
    ) THEN
        ALTER TABLE users ENABLE ROW LEVEL SECURITY;
        RAISE NOTICE '%', 'RLS habilitado para tabela users';
    END IF;
END $$;

-- Políticas RLS para users
DO $$
BEGIN
    -- Remover políticas antigas se existirem
    IF policy_exists('users', 'Allow service_role full access to users') THEN
        DROP POLICY "Allow service_role full access to users" ON users;
    END IF;
    
    IF policy_exists('users', 'Users can access their own profile') THEN
        DROP POLICY "Users can access their own profile" ON users;
    END IF;
    
    -- Criar políticas com isolamento por user_id
    CREATE POLICY "Allow service_role full access to users" ON users
        FOR ALL
        TO service_role
        USING (true)
        WITH CHECK (true);
    
    CREATE POLICY "Users can access their own profile" ON users
        FOR ALL
        TO authenticated
        USING (auth.uid() = id)
        WITH CHECK (auth.uid() = id);
    
    RAISE NOTICE '%', 'Políticas RLS para users configuradas com isolamento por user_id';
END $$;

-- Trigger para atualizar updated_at automaticamente na tabela users
DROP TRIGGER IF EXISTS update_users_updated_at ON users;
CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- =====================================================
-- VERIFICAÇÃO FINAL E VALIDAÇÃO DE IDEMPOTÊNCIA
-- =====================================================

DO $$
BEGIN
    -- Verificar tabelas
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'worlds') THEN
        RAISE NOTICE '%', '✓ Tabela worlds verificada.';
    ELSE
        RAISE EXCEPTION 'ERRO: Tabela worlds não foi criada';
    END IF;
    
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'world_context') THEN
        RAISE NOTICE '%', '✓ Tabela world_context verificada.';
    ELSE
        RAISE EXCEPTION 'ERRO: Tabela world_context não foi criada';
    END IF;
    
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'rpg_embeddings') THEN
        RAISE NOTICE '%', '✓ Tabela rpg_embeddings verificada.';
    ELSE
        RAISE EXCEPTION 'ERRO: Tabela rpg_embeddings não foi criada';
    END IF;
    
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'characters') THEN
        RAISE NOTICE '%', '✓ Tabela characters verificada.';
    ELSE
        RAISE EXCEPTION 'ERRO: Tabela characters não foi criada';
    END IF;
    
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'player_notes') THEN
        RAISE NOTICE '%', '✓ Tabela player_notes verificada.';
    ELSE
        RAISE EXCEPTION 'ERRO: Tabela player_notes não foi criada';
    END IF;
    
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'missions') THEN
        RAISE NOTICE '%', '✓ Tabela missions verificada.';
    ELSE
        RAISE EXCEPTION 'ERRO: Tabela missions não foi criada';
    END IF;
    
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'execution_logs') THEN
        RAISE NOTICE '%', '✓ Tabela execution_logs verificada.';
    ELSE
        RAISE EXCEPTION 'ERRO: Tabela execution_logs não foi criada';
    END IF;
    
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'users') THEN
        RAISE NOTICE '%', '✓ Tabela users verificada.';
    ELSE
        RAISE EXCEPTION 'ERRO: Tabela users não foi criada';
    END IF;
    
    -- Verificar colunas críticas
    IF column_exists('world_context', 'world_id') AND column_exists('world_context', 'user_id') THEN
        RAISE NOTICE '%', '✓ Colunas de isolamento em world_context verificadas.';
    ELSE
        RAISE EXCEPTION 'ERRO: Colunas de isolamento ausentes em world_context';
    END IF;
    
    IF column_exists('worlds', 'campaign_time') THEN
        RAISE NOTICE '%', '✓ Coluna campaign_time em worlds verificada.';
    ELSE
        RAISE EXCEPTION 'ERRO: Coluna campaign_time ausente em worlds';
    END IF;
    
    -- Verificar índices críticos
    IF index_exists('idx_worlds_user_id') AND index_exists('idx_world_context_world_user') AND index_exists('idx_rpg_embeddings_world_id') THEN
        RAISE NOTICE '%', '✓ Índices críticos para multi-mundo verificados.';
    ELSE
        RAISE EXCEPTION 'ERRO: Índices críticos ausentes';
    END IF;
    
    -- Verificar funções
    IF EXISTS (SELECT FROM information_schema.routines WHERE routine_name = 'match_embeddings_by_world') THEN
        RAISE NOTICE '%', '✓ Função match_embeddings_by_world verificada.';
    ELSE
        RAISE EXCEPTION 'ERRO: Função match_embeddings_by_world não foi criada';
    END IF;
    
    RAISE NOTICE '%', '🎉 SCRIPT EXECUTADO COM SUCESSO - SISTEMA MULTI-MUNDO CONFIGURADO';
    RAISE NOTICE '%', '📋 Resumo das funcionalidades:';
    RAISE NOTICE '%', '   - Suporte a múltiplos mundos por usuário';
    RAISE NOTICE '%', '   - Isolamento de dados por world_id e user_id';
    RAISE NOTICE '%', '   - RAG com busca isolada por mundo';
    RAISE NOTICE '%', '   - Políticas RLS para segurança';
    RAISE NOTICE '%', '   - Sistema de Arquétipos e Abordagens (SAA)';
    RAISE NOTICE '%', '   - Sistema de Anotações organizadas';
    RAISE NOTICE '%', '   - Sistema de Missões Dinâmicas com tempo';
    RAISE NOTICE '%', '   - Sistema de Tempo da Campanha';
    RAISE NOTICE '%', '   - Sistema de Logs de Execução do Multiagente';
    RAISE NOTICE '%', '   - Sistema de Usuários com autenticação';
    RAISE NOTICE '%', '   - Script 100% idempotente';
END $$;

