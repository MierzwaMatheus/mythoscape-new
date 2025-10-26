"""Módulo para inicialização e configuração do modelo de linguagem."""

import os
from langchain_openai import ChatOpenAI


def get_llm() -> ChatOpenAI:
    """
    Inicializa e retorna o modelo de linguagem configurado para RPG.
    
    Returns:
        Instância configurada do ChatOpenAI com temperatura otimizada para criatividade.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    model_name = os.getenv("AGENT_MODEL_NAME", "gpt-4o-mini")
    
    return ChatOpenAI(
        api_key=api_key,
        model=model_name,
        temperature=0.7
    )