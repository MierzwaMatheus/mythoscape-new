# Product Requirements Document (PRD) - Mestre de RPG com IA

## 1. Visão Geral

Este documento define os requisitos do produto para o desenvolvimento de uma aplicação web de Mestre de RPG (Role-Playing Game) assistido por Inteligência Artificial. O objetivo principal é criar um ambiente dinâmico e coerente, onde um agente de IA (o Mestre de RPG) interage com o jogador, mantendo um contexto de mundo persistente e acessível.

O projeto será construído sobre uma arquitetura moderna e de baixo custo, utilizando a stack Python/FastAPI/LangChain no backend e React/Vite no frontend, conforme o resumo técnico fornecido.

## 2. Metas do Produto

*   Oferecer uma experiência de RPG imersiva e responsiva, onde a IA atua como mestre.
*   Garantir a **coerência e persistência** do mundo do jogo, independentemente da sessão.
*   Implementar uma arquitetura de dados robusta que permita aos agentes de IA consultar e atualizar o estado do mundo de forma eficiente.
*   Manter a arquitetura **modular, de baixo custo e escalável** (utilizando serviços gratuitos/freemium).

## 3. Público-Alvo

*   Jogadores de RPG solo que buscam uma experiência narrativa rica e dinâmica.
*   Desenvolvedores de IA interessados em aplicações práticas de agentes e persistência de memória de longo prazo.

## 4. Requisitos de Funcionalidade (Features)

| ID | Funcionalidade | Descrição | Prioridade |
| :--- | :--- | :--- | :--- |
| F.1 | Interação de Chat | O usuário deve poder enviar comandos e perguntas em linguagem natural ao Mestre de RPG (Agente de IA). | Alta |
| F.2 | Resposta Contextual | O Mestre de RPG deve utilizar o contexto do mundo (NPCs, Locais, Conhecimento) para gerar respostas coerentes. | Alta |
| F.3 | Atualização do Mundo | O Mestre de RPG deve ser capaz de atualizar o banco de dados do mundo com novas informações (ex: um NPC morre, um local é descoberto, o jogador aprende algo). | Alta |
| F.4 | Interface Web | Interface de chat simples e responsiva para interação. | Alta |
| F.5 | RAG (Retrieval Augmented Generation) | Utilização de busca vetorial para recuperação de contexto semântico relevante antes da geração da resposta. | Alta |
| F.6 | Múltiplos Mundos/Campanhas | O usuário deve poder criar e gerenciar múltiplos mundos/campanhas independentes, cada um com seu próprio contexto isolado. | Alta |
| F.7 | Gerenciamento de Mundos | Interface para criar, listar, atualizar e excluir mundos/campanhas, incluindo estatísticas e metadados. | Média |

## 5. Requisitos Técnicos e Arquitetura de Dados

### 5.1. Arquitetura Geral (Conforme Resumo Técnico)

*   **Frontend:** React + TypeScript + Vite (Deploy: Vercel)
*   **Backend/API:** Python + FastAPI (Deploy: Render)
*   **Agente de IA:** LangChain + LLM (Groq/OpenRouter)
*   **Ferramenta de Busca Semântica (RAG):** Supabase Vector (Postgres `pg_vector`)

### 5.2. Persistência de Dados do Mundo (Requisito Chave)

Para atender ao requisito de persistência de contexto dinâmico e flexível para o Agente de IA, será adotada uma estratégia de **Banco de Dados Híbrido** com foco em um modelo **NoSQL** para o *Contexto do Mundo*.

| Tipo de Dado | Tecnologia Proposta | Justificativa |
| :--- | :--- | :--- |
| **Dados Estruturados** (Usuários, Logs, Configurações de Agentes) | **Supabase (Postgres)** | Conforme arquitetura inicial. Ideal para dados relacionais e segurança. |
| **Memória de Longo Prazo** (Embeddings, RAG) | **Supabase Vector** | Conforme arquitetura inicial. Essencial para busca semântica de contexto. |
| **Contexto do Mundo** (NPCs, Locais, Conhecimento do Jogador) | **MongoDB (ou Supabase com JSONB)** | **Requisito do Produto:** Modelo NoSQL para flexibilidade na criação e manipulação de entidades dinâmicas pelo Agente de IA. |

**Decisão de Implementação do Contexto do Mundo:**

Devido à arquitetura inicial já utilizar o Supabase (Postgres) e para manter a simplicidade e o foco em serviços gratuitos/freemium, será explorado o uso do tipo de dado **JSONB** nativo do PostgreSQL (Supabase) para simular o comportamento NoSQL.

*   **Tabela Proposta:** `world_context`
*   **Estrutura:**
    *   `id` (UUID): Identificador único.
    *   `world_id` (UUID): Identificador do mundo/campanha (FK para tabela `worlds`).
    *   `user_id` (UUID): Identificador do usuário proprietário (FK para tabela `users`).
    *   `type` (VARCHAR): Tipo da entidade (`npc`, `location`, `knowledge`).
    *   `data` (JSONB): Campo flexível para armazenar os dados da entidade.
    *   `created_at` (TIMESTAMP): Data de criação.
    *   `updated_at` (TIMESTAMP): Data da última atualização.

*   **Tabela Adicional:** `worlds`
*   **Estrutura:**
    *   `id` (UUID): Identificador único do mundo/campanha.
    *   `user_id` (UUID): Identificador do usuário proprietário.
    *   `name` (VARCHAR): Nome do mundo/campanha.
    *   `description` (TEXT): Descrição do mundo/campanha.
    *   `is_active` (BOOLEAN): Se o mundo está ativo.
    *   `created_at` (TIMESTAMP): Data de criação.
    *   `updated_at` (TIMESTAMP): Data da última atualização.

**Exemplo de Estrutura `data` (JSONB):**

| Entidade | Exemplo de `data` (JSONB) |
| :--- | :--- |
| **NPC** | `{"name": "Guarda Borin", "status": "Vivo", "location_id": "loc_001", "personality": "Desconfiado", "history": "Antigo soldado que perdeu a família."}` |
| **Local** | `{"name": "Taverna do Dragão Adormecido", "description": "Local movimentado, cheiro de cerveja e fumaça.", "is_discovered": true, "npcs_present": ["npc_001"]}` |
| **Conhecimento** | `{"topic": "A Lenda da Espada", "known_by_player": false, "details": "A espada está escondida nas montanhas. Informação secreta."}` |

### 5.3. Interação do Agente com o Banco de Dados

O Mestre de RPG (Agente LangChain) deve ser equipado com uma **Tool** (Ferramenta) específica para manipulação do `world_context` (via JSONB no Supabase).

*   **Tool Name:** `WorldContextManager`
*   **Funções Expostas ao Agente:**
    *   `get_entity(world_id: str, type: str, name: str)`: Consulta dados de uma entidade em um mundo específico.
    *   `update_entity(world_id: str, type: str, id: str, new_data: dict)`: Altera dados de uma entidade existente em um mundo específico.
    *   `create_entity(world_id: str, type: str, data: dict)`: Cria uma nova entidade no mundo específico.

**Fluxo de Decisão do Agente:**

1.  O jogador envia um prompt (`F.1`) em um mundo/campanha específico.
2.  O Agente de IA (LangChain) decide se precisa de contexto do mundo.
3.  Se precisar, ele chama a `Tool` (`WorldContextManager.get_entity`) com o `world_id` para buscar informações sobre NPCs ou Locais do mundo específico.
4.  O Agente gera a resposta (`F.2`) baseada no contexto do mundo correto.
5.  Se a ação do jogador resultar em uma mudança no mundo (ex: "Eu mato o Guarda Borin"), o Agente chama a `Tool` (`WorldContextManager.update_entity`) para registrar a mudança no mundo específico (`F.3`).

### 5.4. Coerência Factual entre RAG e JSONB (Memória Híbrida)

Para garantir que a resposta do Agente de IA seja rica em detalhes (RAG) e factualmente correta (JSONB), será implementada uma estratégia de **Memória Híbrida** utilizando Metadados.

**Mecanismo:**

1.  Cada *chunk* de texto armazenado no **Vector Store (RAG)** deve conter metadados que sirvam como um elo de ligação com o registro estruturado no **JSONB**.
2.  Os metadados obrigatórios serão: `entity_id` (ID único do registro no JSONB), `entity_type` (tipo da entidade: `npc`, `location`, etc.) e `world_id` (ID do mundo/campanha).

**Fluxo de Consulta Otimizado:**

1.  O Agente realiza a **Busca Semântica** no RAG filtrada por `world_id` para garantir contexto do mundo correto.
2.  O RAG retorna os *chunks* mais relevantes e seus **Metadados** (`entity_id`, `entity_type`, `world_id`).
3.  O Agente utiliza os Metadados (`entity_id`) para realizar uma **Consulta Factual** no JSONB, recuperando o estado mais recente e canônico da entidade (ex: `status: "Morto"`).
4.  O Agente envia o prompt ao LLM **aumentado** com a descrição do RAG e o estado factual do JSONB, garantindo que a resposta seja detalhada e coerente com a verdade do mundo específico.

---

## 6. Requisitos de Performance

O Mestre de RPG (Agente LangChain) deve ser equipado com uma **Tool** (Ferramenta) específica para manipulação do `world_context` (via JSONB no Supabase).

*   **Tool Name:** `WorldContextManager`
*   **Funções Expostas ao Agente:**
    *   `get_entity(type: str, name: str)`: Consulta dados de uma entidade.
    *   `update_entity(type: str, id: str, new_data: dict)`: Altera dados de uma entidade existente.
    *   `create_entity(type: str, data: dict)`: Cria uma nova entidade no mundo.

**Fluxo de Decisão do Agente:**

1.  O jogador envia um prompt (`F.1`).
2.  O Agente de IA (LangChain) decide se precisa de contexto do mundo.
3.  Se precisar, ele chama a `Tool` (`WorldContextManager.get_entity`) para buscar informações sobre NPCs ou Locais.
4.  O Agente gera a resposta (`F.2`).
5.  Se a ação do jogador resultar em uma mudança no mundo (ex: "Eu mato o Guarda Borin"), o Agente chama a `Tool` (`WorldContextManager.update_entity`) para registrar a mudança (`F.3`).

## 6. Requisitos de Performance

*   Tempo de resposta do Mestre de RPG: Máximo de 5 segundos por turno.
*   Latência da API (FastAPI): Mínimo impacto no tempo total de resposta.
*   Consultas ao DB: Otimizadas para retornar dados de contexto rapidamente.

## 7. Critérios de Sucesso

*   O Mestre de RPG mantém a coerência narrativa por mais de 100 interações em cada mundo/campanha.
*   Novas entidades (NPCs/Locais) criadas pelo Agente são persistidas e recuperadas corretamente em sessões futuras dentro do mundo específico.
*   O sistema suporta múltiplos mundos/campanhas por usuário com isolamento completo de contexto.
*   A aplicação é implantada com sucesso utilizando os serviços gratuitos/freemium propostos (Vercel/Render/Supabase).
*   A flexibilidade do JSONB permite a evolução do esquema de dados do mundo sem a necessidade de migrações complexas.
*   O sistema de RAG funciona corretamente com filtros por `world_id`, garantindo que o contexto semântico seja específico do mundo.
