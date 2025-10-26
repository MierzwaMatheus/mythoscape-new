"""Agente principal do sistema RPG - Mestre de RPG com IA."""

import os
from typing import Any
from langgraph.prebuilt import create_react_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI

from app.services.vector_store import VectorStoreManager
from app.tools.world_context_tool import world_context_tools


class RPGAgent:
    """
    Agente principal que atua como Mestre de RPG com IA.
    
    Combina RAG (Retrieval Augmented Generation) para contexto semântico
    com ferramentas estruturadas para manipulação de fatos do mundo,
    implementando a estratégia híbrida definida no PRD seção 5.4.
    """
    
    def __init__(self) -> None:
        """
        Inicializa o agente RPG com todas as funcionalidades necessárias.
        
        Raises:
            ValueError: Se as chaves de API necessárias não estiverem configuradas.
        """
        # Validação das variáveis de ambiente
        if not os.getenv("OPENAI_API_KEY"):
            raise ValueError("OPENAI_API_KEY deve estar definida nas variáveis de ambiente")
        
        # Inicialização do VectorStoreManager para RAG
        self._vector_store_manager = VectorStoreManager()
        
        # Inicialização do LLM otimizado
        self._llm = ChatOpenAI(
            model="gpt-4o-mini",  # Modelo eficiente e rápido
            temperature=0.7,      # Criatividade balanceada para RPG
            max_tokens=1000,      # Limite para respostas concisas
            streaming=False       # Performance: sem streaming para simplicidade
        )
        
        # System Prompt detalhado para Mestre de RPG
        self._system_prompt = self._create_system_prompt()
        
        # Criação do prompt template
        self._prompt = ChatPromptTemplate.from_messages([
            ("system", self._system_prompt),
            MessagesPlaceholder(variable_name="chat_history", optional=True),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ])
        
        # Criação do agente com ferramentas usando langgraph
        self._agent_executor = create_react_agent(
            model=self._llm,
            tools=world_context_tools,
            prompt=self._system_prompt
        )
    
    def _create_system_prompt(self) -> str:
        """
        Cria o system prompt detalhado para o Mestre de RPG.
        
        Returns:
            String com o prompt do sistema otimizado.
        """
        return """Você é um Mestre de RPG experiente e criativo, especializado em criar aventuras imersivas e envolventes.

## IDENTIDADE E PERSONALIDADE
- Você é um narrador habilidoso que equilibra drama, humor e suspense
- Mantenha um tom envolvente, mas não excessivamente dramático
- Seja criativo, mas consistente com o mundo estabelecido
- Responda sempre em português brasileiro

## PRIORIDADES DE FUNCIONAMENTO (ORDEM OBRIGATÓRIA)

### 1. FERRAMENTAS ESTRUTURADAS (PRIORIDADE MÁXIMA)
- **SEMPRE** use as ferramentas disponíveis para consultar e atualizar fatos do mundo
- **get_entity**: Para buscar informações sobre NPCs, locais ou conhecimentos existentes
- **create_entity**: Para registrar novos NPCs, locais ou conhecimentos descobertos
- **update_entity**: Para atualizar o estado de entidades quando algo mudar

### 2. CONTEXTO SEMÂNTICO (RAG)
- Use o contexto recuperado para enriquecer descrições e narrativa
- O RAG fornece detalhes descritivos e atmosféricos
- Combine informações estruturadas (ferramentas) com contexto semântico (RAG)

## REGRAS DE CONSISTÊNCIA
- **NUNCA** invente fatos sobre entidades sem consultar as ferramentas primeiro
- **SEMPRE** registre novos elementos importantes usando create_entity
- **SEMPRE** atualize o estado quando algo significativo mudar
- Mantenha coerência entre sessões usando as informações estruturadas

## ESTILO DE RESPOSTA
- Respostas entre 100-300 palavras (conciso mas envolvente)
- Use descrições vívidas mas não excessivamente longas
- Inclua elementos sensoriais (sons, cheiros, texturas)
- Termine com uma pergunta ou situação que demande decisão do jogador

## MECÂNICAS DE JOGO
- Considere as ações do jogador e suas consequências lógicas
- Introduza desafios apropriados ao contexto
- Mantenha o ritmo da aventura equilibrado
- Recompense criatividade e pensamento estratégico

## EXEMPLO DE FLUXO
1. Jogador menciona um NPC → get_entity para verificar informações
2. NPC não existe → create_entity para registrar
3. Interação muda o estado do NPC → update_entity para atualizar
4. Use contexto RAG para descrições ricas e atmosfera

Lembre-se: Você é o guardião da consistência do mundo. Use as ferramentas religiosamente!"""
    
    async def run(self, player_input: str) -> str:
        """
        Processa a entrada do jogador e retorna a resposta do Mestre de RPG.
        
        Implementa o fluxo híbrido: RAG para contexto + ferramentas para fatos.
        
        Args:
            player_input: Entrada do jogador em linguagem natural.
            
        Returns:
            Resposta do Mestre de RPG.
        """
        try:
            # Etapa 1: Busca semântica para contexto (RAG)
            relevant_context = await self._get_semantic_context(player_input)
            
            # Etapa 2: Enriquecimento da entrada com contexto
            enriched_input = self._enrich_input_with_context(player_input, relevant_context)
            
            # Etapa 3: Execução do agente com ferramentas estruturadas
            response = await self._agent_executor.ainvoke({
                "messages": [("human", enriched_input)]
            })
            
            # Extração da resposta do formato langgraph
            if "messages" in response and response["messages"]:
                return response["messages"][-1].content
            
            return "Desculpe, não consegui processar sua solicitação."
            
        except Exception as e:
            # Fallback gracioso em caso de erro
            return f"*O Mestre parece confuso por um momento...* \n\nDesculpe, houve um problema técnico. Pode repetir sua ação? \n\nErro: {str(e)}"
    
    async def _get_semantic_context(self, query: str) -> list[str]:
        """
        Busca contexto semântico relevante usando RAG.
        
        Args:
            query: Consulta do jogador.
            
        Returns:
            Lista de contextos relevantes.
        """
        try:
            # Busca semântica otimizada
            documents = await self._vector_store_manager.similarity_search(
                query=query,
                k=3  # Limite para performance
            )
            
            # Extração do conteúdo dos documentos
            return [doc.page_content for doc in documents]
            
        except Exception:
            # Fallback silencioso - continua sem contexto RAG
            return []
    
    def _enrich_input_with_context(self, player_input: str, context: list[str]) -> str:
        """
        Enriquece a entrada do jogador com contexto semântico.
        
        Args:
            player_input: Entrada original do jogador.
            context: Lista de contextos relevantes.
            
        Returns:
            Entrada enriquecida com contexto.
        """
        if not context:
            return player_input
        
        context_str = "\n".join([f"- {ctx}" for ctx in context[:2]])  # Máximo 2 contextos
        
        return f"""ENTRADA DO JOGADOR: {player_input}

CONTEXTO RELEVANTE DISPONÍVEL:
{context_str}

Use o contexto acima para enriquecer sua resposta, mas SEMPRE priorize as ferramentas para fatos estruturados."""