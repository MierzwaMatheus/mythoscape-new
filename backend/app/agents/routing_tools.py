"""
Ferramentas de classificação para o sistema multiagente.
Define as ferramentas Pydantic que representam cada agente especialista.
"""

from pydantic import BaseModel, Field


class WorldExpertTool(BaseModel):
    """Encaminha perguntas sobre o ambiente, locais, lore e descrições do mundo."""
    instructions: str = Field(description="Instruções específicas para o Agente de Mundo.")


class CharacterExpertTool(BaseModel):
    """Encaminha ações e perguntas sobre o estado, inventário ou habilidades de personagens."""
    instructions: str = Field(description="Instruções específicas para o Agente de Personagem.")


class MissionExpertTool(BaseModel):
    """Encaminha prompts relacionados à criação, progresso ou status de missões."""
    instructions: str = Field(description="Instruções específicas para o Agente de Missões.")


class RulesExpertTool(BaseModel):
    """Encaminha questões sobre aplicação de regras SAA, modificadores e mecânicas."""
    instructions: str = Field(description="Instruções específicas para o Agente de Regras.")


class TimeExpertTool(BaseModel):
    """Encaminha questões sobre tempo da campanha, eventos temporais e cronologia."""
    instructions: str = Field(description="Instruções específicas para o Agente de Tempo.")


class ItemsExpertTool(BaseModel):
    """Encaminha questões sobre inventário, objetos, equipamentos e recursos."""
    instructions: str = Field(description="Instruções específicas para o Agente de Itens.")


class PlotExpertTool(BaseModel):
    """Encaminha questões sobre narrativa principal, arcos de história e plot twists."""
    instructions: str = Field(description="Instruções específicas para o Agente de Plot.")


class SocialExpertTool(BaseModel):
    """Encaminha questões sobre interações sociais, relacionamentos e dinâmicas sociais."""
    instructions: str = Field(description="Instruções específicas para o Agente Social.")


# Lista de todas as ferramentas de roteamento disponíveis
ROUTING_TOOLS = [
    WorldExpertTool,
    CharacterExpertTool,
    MissionExpertTool,
    RulesExpertTool,
    TimeExpertTool,
    ItemsExpertTool,
    PlotExpertTool,
    SocialExpertTool,
]