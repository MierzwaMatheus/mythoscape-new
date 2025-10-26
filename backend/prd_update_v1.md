Excelente. Agora vamos mergulhar na arquitetura técnica detalhada. Esta é a planta baixa do nosso sistema de IA, definindo *como* cada peça se conecta e opera. Usaremos conceitos e bibliotecas do ecossistema LangChain (como LangGraph e LCEL) para construir isso de forma robusta.

### 1. O Agente Orquestrador (Roteador)

Tecnicamente, o "Agente Roteador" não é um agente que pensa no sentido tradicional. Ele é um **nó de roteamento condicional** dentro de um grafo, construído com **LangGraph**. Sua função é direcionar o fluxo de trabalho, não gerar linguagem.

**Implementação Técnica:**

1.  **Ferramentas de Classificação (Classification Tools):** Primeiro, definimos uma série de "ferramentas" Pydantic que representam cada agente especialista. O nome e a descrição de cada ferramenta são cruciais, pois é isso que o LLM usará para decidir.

    ```python
    # Em app/agents/routing_tools.py
    from langchain_core.pydantic_v1 import BaseModel, Field

    class WorldExpertTool(BaseModel):
        """Encaminha perguntas sobre o ambiente, locais, lore e descrições do mundo."""
        instructions: str = Field(description="Instruções específicas para o Agente de Mundo.")

    class CharacterExpertTool(BaseModel):
        """Encaminha ações e perguntas sobre o estado, inventário ou habilidades de personagens (jogador e NPCs)."""
        instructions: str = Field(description="Instruções específicas para o Agente de Personagem.")

    class MissionExpertTool(BaseModel):
        """Encaminha prompts relacionados à criação, progresso ou status de missões."""
        instructions: str = Field(description="Instruções específicas para o Agente de Missões.")

    # ... e assim por diante para cada agente especialista.
    ```

2.  **O Roteador com LLM:** Criamos um LLM "com ferramentas" (`.with_structured_output()`) que é forçado a escolher uma ou mais dessas ferramentas de classificação com base no prompt do usuário.

    ```python
    # Em app/agents/router.py
    from langchain_openai import ChatOpenAI
    from app.agents.routing_tools import WorldExpertTool, CharacterExpertTool, MissionExpertTool

    # Lista de ferramentas que o roteador pode "chamar"
    routing_tools = [WorldExpertTool, CharacterExpertTool, MissionExpertTool]

    llm = ChatOpenAI(model="gpt-4o-mini")
    # O .with_structured_output força o LLM a retornar um ou mais dos nossos Pydantic models
    router_agent = llm.with_structured_output(routing_tools)
    ```

3.  **O Grafo (LangGraph):** O LangGraph orquestra o fluxo.

    ```python
    # Em app/agents/graph.py
    from langgraph.graph import StateGraph, END

    # 1. Definir o Estado do Grafo
    class AgentState(TypedDict):
        user_prompt: str
        specialist_outputs: list # Armazena as saídas dos especialistas
        # ... outros campos

    # 2. Definir os Nós do Grafo
    def route_to_specialists(state: AgentState):
        prompt = state['user_prompt']
        # Chama o roteador, que retorna uma lista de "ferramentas" (ex: [CharacterExpertTool(...)])
        selected_routes = router_agent.invoke(prompt)
        # O LangGraph pode então chamar os nós correspondentes em paralelo
        # ... lógica para invocar os agentes especialistas com base nas rotas
        return {"specialist_outputs": ...}

    def specialist_node_character(state: AgentState):
        # Lógica do Agente de Personagem
        ...

    def specialist_node_world(state: AgentState):
        # Lógica do Agente de Mundo
        ...

    def synthesizer_node(state: AgentState):
        # Lógica do Agente Sintetizador
        ...

    # 3. Construir o Grafo
    workflow = StateGraph(AgentState)
    workflow.add_node("router", route_to_specialists)
    workflow.add_node("character_agent", specialist_node_character)
    workflow.add_node("world_agent", specialist_node_world)
    workflow.add_node("synthesizer", synthesizer_node)

    # 4. Definir as Arestas (o fluxo)
    workflow.set_entry_point("router")
    # Roteamento condicional: o nó 'router' decide para quais especialistas ir
    workflow.add_conditional_edges(...)
    # Após os especialistas, todos vão para o sintetizador
    workflow.add_edge("character_agent", "synthesizer")
    workflow.add_edge("world_agent", "synthesizer")
    workflow.add_edge("synthesizer", END)

    app = workflow.compile()
    ```

### 2. Interação dos Agentes com os Endpoints da API

Os agentes especialistas **não chamam os endpoints da API diretamente via HTTP**. Isso seria ineficiente e difícil de gerenciar. Em vez disso, eles usam **Ferramentas (Tools)** que encapsulam a lógica de negócio, a qual por sua vez interage com o banco de dados.

**Implementação Técnica:**

1.  **Camada de Serviço (Services):** Você já tem isso (`WorldContextService`, etc.). Essa camada contém a lógica pura de Python para interagir com o Supabase.

    ```python
    # Em app/services/mission_service.py
    class MissionService:
        def __init__(self, db_client):
            self.db = db_client

        def create_mission(self, world_id: str, name: str, ...) -> dict:
            # Lógica para inserir uma nova missão no Supabase
            # Retorna a missão criada como um dicionário
            ...

        def get_mission_by_id(self, mission_id: str) -> dict:
            # Lógica para buscar uma missão no Supabase
            ...
    ```

2.  **Ferramentas LangChain (Tools):** Para cada função de serviço que um agente precisa usar, criamos uma `Tool` correspondente.

    ```python
    # Em app/tools/mission_tools.py
    from langchain.tools import tool
    from app.services.mission_service import MissionService

    # Instancia o serviço (a injeção de dependência pode ser mais elegante)
    mission_service = MissionService(...)

    @tool
    def create_mission_tool(world_id: str, name: str, ...):
        """Cria uma nova missão na campanha com os detalhes fornecidos."""
        return mission_service.create_mission(world_id, name, ...)

    @tool
    def get_mission_tool(mission_id: str):
        """Busca os detalhes de uma missão específica pelo seu ID."""
        return mission_service.get_mission_by_id(mission_id)
    ```

3.  **O Agente Especialista:** Cada agente especialista é um `create_react_agent` (ou similar) que recebe apenas as ferramentas do seu domínio.

    ```python
    # No nó do Agente de Missões
    from langchain.agents import AgentExecutor, create_react_agent
    from app.tools.mission_tools import create_mission_tool, get_mission_tool

    mission_tools = [create_mission_tool, get_mission_tool]
    mission_agent_executor = AgentExecutor(agent=..., tools=mission_tools, ...)

    # O agente usará essas ferramentas para executar sua tarefa
    result = mission_agent_executor.invoke({"input": "Crie uma missão para resgatar o ferreiro..."})
    ```

### 3. Comunicação entre Agentes e o Sintetizador

A comunicação é gerenciada pelo **estado do grafo (AgentState)**. Cada agente especialista não retorna uma frase, mas sim um **dicionário estruturado** com suas descobertas.

**Implementação Técnica:**

*   **Saída do Especialista:**

    ```python
    # Saída do Agente de Mundo
    world_output = {
        "source_agent": "world_agent",
        "content_type": "description",
        "data": "A sala está empoeirada. Há um baú no canto.",
        "referenced_ids": {"location": "loc_uuid_123"}
    }

    # Saída do Agente de Personagem
    character_output = {
        "source_agent": "character_agent",
        "content_type": "action_result",
        "data": "O personagem, sendo 'Atlético', conseguiu forçar o baú.",
        "referenced_ids": {"character": "char_uuid_abc"}
    }
    ```

*   **O `AgentState` acumula essas saídas:**

    ```python
    # Dentro do LangGraph
    state['specialist_outputs'].append(world_output)
    state['specialist_outputs'].append(character_output)
    ```

*   **Entrada para o Sintetizador:** O Agente Sintetizador recebe a lista completa `state['specialist_outputs']`. Seu prompt de sistema será algo como:

    > "Você é o Mestre Narrador. Sua personalidade é [Personalidade do Mestre]. Abaixo estão os resultados de vários especialistas. Sua tarefa é:
    > 1.  Sintetize esses fatos em uma única resposta narrativa coerente para o jogador.
    > 2.  Determine a duração em minutos que essas ações levaram.
    > 3.  Liste todas as entidades (`referenced_ids`) que foram mencionadas ou criadas para que possam ser adicionadas à memória de longo prazo (Vector Store).
    >
    > **Dados dos Especialistas:**
    > ```json
    > [
    >   {"source_agent": "world_agent", "data": "A sala está...", "referenced_ids": {"location": "loc_uuid_123"}},
    >   {"source_agent": "character_agent", "data": "O personagem forçou o baú.", "referenced_ids": {"character": "char_uuid_abc"}}
    > ]
    > ```
    >
    > Retorne sua resposta estritamente no seguinte formato JSON:
    > `{"narrative": "...", "duration_minutes": ..., "vector_store_updates": [{"entity_id": "...", "text_chunk": "..."}, ...]}`"

### 4. Atualização do Vector Store pelo Sintetizador

O Sintetizador usa as `referenced_ids` e a narrativa que ele mesmo criou para preparar os dados para o RAG.

1.  **Coleta de IDs:** Ele extrai todos os `referenced_ids` das saídas dos especialistas.
2.  **Criação de Chunks:** Para cada trecho da sua própria narrativa, ele associa os IDs relevantes. Por exemplo, a frase *"Você entra na sala do trono, um lugar há muito esquecido..."* será associada ao `entity_id: "loc_uuid_123"`.
3.  **Saída Estruturada:** Ele gera a lista `vector_store_updates` conforme o formato JSON solicitado.
4.  **Processo Final (Backend):** Após o grafo terminar, uma função final no backend pega essa lista e usa o `VectorStoreManager` para adicionar os novos chunks de texto com os metadados corretos ao Supabase Vector.

### 5. Agente de Criação de Campanhas

Este é um agente mais simples, de uso único.

*   **Fluxo:** Ele não precisa do sistema multiagente completo. É um fluxo linear.
*   **Input:** Recebe um JSON com as escolhas do usuário (Gênero, Tom do Mestre, Conceito do Personagem, Arquétipos, etc.).
*   **Prompt:** Seu prompt de sistema é massivo e detalhado, instruindo-o a:
    1.  Gerar uma descrição detalhada do mundo com base no gênero e inspiração.
    2.  Criar a ficha inicial do personagem com base no SAA.
    3.  Criar 2-3 NPCs iniciais e 1-2 locais relevantes.
    4.  Escrever a cena de abertura da campanha, no tom do Mestre escolhido.
    5.  **Crucial:** Gerar uma lista de chamadas de função (`tool calls`) para persistir tudo o que ele criou (`create_world`, `create_character`, `create_npc`, `create_location`).
*   **Execução:** O backend executa o agente, recebe a lista de chamadas de função e as executa em ordem para popular o banco de dados.

### 6. Agente de Sumarização para Anotações

Este também é um agente mais simples e "on-demand".

*   **Gatilho:** O usuário clica em um ícone "Anotar" em uma mensagem do Mestre.
*   **Fluxo:**
    1.  O frontend envia o `message_id` da mensagem a ser sumarizada para um endpoint específico (ex: `POST /notes/summarize`).
    2.  O backend busca o conteúdo completo daquela mensagem.
    3.  Ele chama um LLM com um prompt simples e focado:
        > "Você é um assistente de anotações para um jogo de RPG. Resuma o texto a seguir em 2-3 pontos principais (bullet points), focando em nomes de NPCs, locais, itens e objetivos.
        >
        > **Texto Original:**
        > '[Conteúdo da mensagem do Mestre]'
        >
        > **Resumo:**"
    4.  O resultado é retornado ao frontend, que pode então pré-popular uma nova nota no editor Tiptap para o usuário refinar.