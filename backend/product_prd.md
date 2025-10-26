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
| F.8 | Sistema de Arquétipos e Abordagens (SAA) | Sistema de criação de personagem baseado em tags de Arquétipos (talentos) e Abordagens (estilo de ação), substituindo sistemas numéricos complexos. | Alta |
| F.9 | Personalidades do Mestre de IA | Quatro personalidades narrativas distintas: Sério/Sombrio, Épico/Heroico, Cômico/Leve, Misterioso/Oculto, que definem o tom e estilo da narração. | Alta |
| F.10 | Sistema de Comandos de Chat Expandido | Comandos divididos entre processamento frontend (instantâneo) e IA (contextual), incluindo /roll, /meta, /think, /edit, /create, /inspect. | Alta |
| F.11 | Sistema de Anotações | Sistema organizado de anotações do jogador com estrutura de pastas (Personagens, Lugares, Lendas, Geral) e integração com IA. | Média |
| F.12 | Interface de Criação em 3 Passos | Fluxo UX otimizado para criação de campanhas: Cenário, Personalidade do Mestre, e Criação do Protagonista com SAA. | Alta |
| F.13 | Sistema de Ficha Visual | Interface de ficha do personagem baseada em tags visuais ao invés de números, mostrando Arquétipos, Abordagens, Vitalidade e Inventário. | Média |
| F.14 | Sistema de Missões Dinâmicas | Sistema completo de missões com prazos, consequências, plot twists e informações secretas para a IA, permitindo narrativas complexas e ramificadas. | Alta |
| F.15 | Sistema de Tempo da Campanha | Relógio persistente do mundo que avança baseado nas ações do jogador, permitindo eventos temporais e expiração de missões. | Alta |
| F.16 | Arquitetura Multiagente | Sistema de agentes especializados (Roteador, Mundo, Personagem, Missões, Tempo, Plot, etc.) coordenados por um Agente Sintetizador. | Alta |

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
    *   `genre_tags` (JSONB): Tags de gênero/tema (ex: ["Cyberpunk", "Investigação", "Noir"]).
    *   `master_personality` (VARCHAR): Personalidade do Mestre de IA ("serious_dark", "epic_heroic", "comic_light", "mysterious_occult").
    *   `campaign_time` (JSONB): Tempo atual da campanha (ex: {"day": 1, "hour": 12, "minute": 0, "season": "spring", "year": 1}).
    *   `is_active` (BOOLEAN): Se o mundo está ativo.
    *   `created_at` (TIMESTAMP): Data de criação.
    *   `updated_at` (TIMESTAMP): Data da última atualização.

*   **Nova Tabela:** `characters`
*   **Estrutura:**
    *   `id` (UUID): Identificador único do personagem.
    *   `world_id` (UUID): Identificador do mundo/campanha (FK para tabela `worlds`).
    *   `user_id` (UUID): Identificador do usuário proprietário.
    *   `name` (VARCHAR): Nome do personagem.
    *   `concept` (TEXT): Conceito do personagem em uma frase.
    *   `archetypes` (JSONB): Array de arquétipos selecionados (ex: ["Tecnológico", "Observador", "Persuasivo"]).
    *   `approaches` (JSONB): Array de abordagens selecionadas (ex: ["Cuidadosa", "Direta"]).
    *   `vitality` (INTEGER): Nível de vitalidade (1-5).
    *   `inventory` (JSONB): Inventário do personagem.
    *   `active_missions` (JSONB): Missões ativas do personagem.
    *   `is_active` (BOOLEAN): Se o personagem está ativo.
    *   `created_at` (TIMESTAMP): Data de criação.
    *   `updated_at` (TIMESTAMP): Data da última atualização.

*   **Nova Tabela:** `player_notes`
*   **Estrutura:**
    *   `id` (UUID): Identificador único da anotação.
    *   `world_id` (UUID): Identificador do mundo/campanha (FK para tabela `worlds`).
    *   `user_id` (UUID): Identificador do usuário proprietário.
    *   `category` (VARCHAR): Categoria da anotação ("characters", "places", "lore", "general").
    *   `title` (VARCHAR): Título da anotação.
    *   `content` (TEXT): Conteúdo da anotação (formato rich text/HTML).
    *   `created_at` (TIMESTAMP): Data de criação.
    *   `updated_at` (TIMESTAMP): Data da última atualização.

*   **Nova Tabela:** `missions`
*   **Estrutura:**
    *   `id` (UUID): Identificador único da missão.
    *   `world_id` (UUID): Identificador do mundo/campanha (FK para tabela `worlds`).
    *   `user_id` (UUID): Identificador do usuário proprietário.
    *   `name` (VARCHAR): Nome da missão.
    *   `description` (TEXT): Descrição da missão visível ao jogador.
    *   `status` (VARCHAR): Status da missão ("active", "completed", "failed", "expired").
    *   `created_at_ingame` (JSONB): Tempo do jogo quando a missão foi criada.
    *   `expires_at_ingame` (JSONB): Tempo do jogo quando a missão expira (opcional).
    *   `plot_twist_trigger` (TEXT): Condição que ativa um plot twist (informação secreta da IA).
    *   `secret_plot_info` (TEXT): Informações secretas sobre a missão que apenas a IA conhece.
    *   `success_outcome` (TEXT): Consequências do sucesso da missão.
    *   `failure_outcome` (TEXT): Consequências do fracasso da missão.
    *   `expiration_outcome` (TEXT): Consequências se a missão expirar.
    *   `created_at` (TIMESTAMP): Data de criação real.
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

*   **Tool Name:** `CharacterManager`
*   **Funções Expostas ao Agente:**
    *   `get_character(world_id: str, user_id: str)`: Consulta dados do personagem ativo no mundo.
    *   `update_character(world_id: str, character_id: str, updates: dict)`: Atualiza dados do personagem (vitalidade, inventário, missões).
    *   `add_to_inventory(world_id: str, character_id: str, item: dict)`: Adiciona item ao inventário.
    *   `update_vitality(world_id: str, character_id: str, new_vitality: int)`: Atualiza nível de vitalidade.

*   **Tool Name:** `NotesManager`
*   **Funções Expostas ao Agente:**
    *   `create_note(world_id: str, user_id: str, category: str, title: str, content: str)`: Cria nova anotação.
    *   `search_notes(world_id: str, user_id: str, query: str)`: Busca anotações por conteúdo.

*   **Tool Name:** `MissionManager`
*   **Funções Expostas ao Agente:**
    *   `create_mission(world_id: str, user_id: str, mission_data: dict)`: Cria nova missão com prazos e informações secretas.
    *   `update_mission_status(world_id: str, mission_id: str, status: str)`: Atualiza status da missão.
    *   `get_active_missions(world_id: str, user_id: str)`: Consulta missões ativas do jogador.
    *   `check_expired_missions(world_id: str, current_time: dict)`: Verifica missões expiradas baseado no tempo da campanha.
    *   `trigger_plot_twist(world_id: str, mission_id: str, condition: str)`: Ativa plot twist quando condição é atendida.

*   **Tool Name:** `TimeManager`
*   **Funções Expostas ao Agente:**
    *   `get_campaign_time(world_id: str)`: Consulta o tempo atual da campanha.
    *   `advance_time(world_id: str, time_increment: dict)`: Avança o tempo da campanha baseado nas ações.
    *   `schedule_event(world_id: str, event_time: dict, event_data: dict)`: Agenda eventos futuros no tempo da campanha.

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

## 6. Arquitetura Multiagente

### 6.1. Visão Geral da Arquitetura "Hub and Spoke"

O sistema utiliza uma arquitetura multiagente coordenada por um **Agente Roteador** central que distribui tarefas para **Agentes Especialistas** e um **Agente Sintetizador** que consolida as respostas.

### 6.2. Agentes do Sistema

*   **Agente Roteador:** Analisa a entrada do usuário e determina quais agentes especialistas devem ser acionados.
*   **Agente Sintetizador:** Consolida as respostas dos agentes especialistas em uma narrativa coerente.
*   **Agentes Especialistas:**
    *   **Agente Mundo:** Gerencia contexto do mundo, NPCs e locais.
    *   **Agente Personagem:** Gerencia dados do personagem, vitalidade e inventário.
    *   **Agente Missões:** Cria, atualiza e gerencia missões dinâmicas.
    *   **Agente Regras:** Interpreta e aplica regras do SAA.
    *   **Agente Tempo:** Gerencia o tempo da campanha e eventos temporais.
    *   **Agente Itens:** Gerencia inventário e objetos do mundo.
    *   **Agente Plot:** Gerencia narrativa principal e plot twists.
    *   **Agente Social:** Gerencia interações sociais e relacionamentos entre personagens.

### 6.3. Configuração de Prompts via Variáveis de Ambiente

Para garantir flexibilidade e facilitar ajustes nos comportamentos dos agentes, todos os prompts do sistema são configuráveis através de variáveis de ambiente:

**Estrutura das Variáveis:**
*   `AGENT_ROUTER_PROMPT`: Prompt do agente roteador
*   `AGENT_SYNTHESIZER_PROMPT`: Prompt do agente sintetizador
*   `AGENT_WORLD_PROMPT`: Prompt do agente especialista em mundo
*   `AGENT_CHARACTER_PROMPT`: Prompt do agente especialista em personagem
*   `AGENT_MISSIONS_PROMPT`: Prompt do agente especialista em missões
*   `AGENT_RULES_PROMPT`: Prompt do agente especialista em regras
*   `AGENT_TIME_PROMPT`: Prompt do agente especialista em tempo
*   `AGENT_ITEMS_PROMPT`: Prompt do agente especialista em itens
*   `AGENT_PLOT_PROMPT`: Prompt do agente especialista em plot
*   `AGENT_SOCIAL_PROMPT`: Prompt do agente especialista em interações sociais

**Benefícios:**
*   Ajustes rápidos de comportamento sem redeployment
*   Testes A/B de diferentes abordagens narrativas
*   Personalização por ambiente (desenvolvimento, produção)
*   Facilita experimentação com diferentes personalidades de IA
    *   **Agente Social:** Gerencia interações sociais e relacionamentos.

## 7. Requisitos de Performance

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

## 8. Critérios de Sucesso

*   O Mestre de RPG mantém a coerência narrativa por mais de 100 interações em cada mundo/campanha.
*   Novas entidades (NPCs/Locais) criadas pelo Agente são persistidas e recuperadas corretamente em sessões futuras dentro do mundo específico.
*   O sistema suporta múltiplos mundos/campanhas por usuário com isolamento completo de contexto.
*   A aplicação é implantada com sucesso utilizando os serviços gratuitos/freemium propostos (Vercel/Render/Supabase).
*   A flexibilidade do JSONB permite a evolução do esquema de dados do mundo sem a necessidade de migrações complexas.
*   O sistema de RAG funciona corretamente com filtros por `world_id`, garantindo que o contexto semântico seja específico do mundo.
*   O Sistema de Arquétipos e Abordagens (SAA) permite criação intuitiva de personagens sem conhecimento prévio de RPG.
*   As quatro personalidades do Mestre de IA produzem narrativas distintamente diferentes e coerentes com o tom escolhido.
*   O sistema de comandos de chat funciona corretamente, com comandos frontend respondendo instantaneamente e comandos IA processando contexto adequadamente.
*   O sistema de anotações permite organização eficiente do conhecimento do jogador com integração fluida com a IA.
*   A interface de criação em 3 passos resulta em alta taxa de conclusão de criação de campanhas (>80%).
*   A ficha visual do personagem é compreensível para jogadores novatos sem necessidade de explicação adicional.
*   O sistema de missões dinâmicas cria narrativas complexas com consequências temporais e plot twists ativados contextualmente.
*   O sistema de tempo da campanha avança de forma consistente e permite eventos temporais programados.
*   A arquitetura multiagente distribui tarefas eficientemente, resultando em respostas mais rápidas e especializadas.
