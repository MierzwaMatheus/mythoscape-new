"""
Agente de criação de campanhas - responsável por gerar o mundo inicial, NPCs e cena de abertura.
"""

from typing import Dict, Any
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from app.utils.env import get_env_var


class CampaignCreationAgent:
    """
    Agente responsável pela criação inicial de campanhas.
    
    Este agente é mais simples e não faz parte do sistema multiagente principal.
    Ele é usado apenas no processo de criação de uma nova campanha.
    """
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-4o",  # Usando modelo mais avançado para criação de conteúdo rico
            temperature=0.8,  # Temperatura mais alta para criatividade
            api_key=get_env_var("OPENAI_API_KEY")
        )
        self.system_prompt = get_env_var("AGENT_CAMPAIGN_CREATION_PROMPT")
    
    async def create_campaign(self, campaign_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Cria uma nova campanha com base nos dados fornecidos pelo usuário.
        
        Args:
            campaign_data: Dicionário contendo os dados iniciais da campanha:
                - name: Nome da campanha
                - genre_tags: Lista de tags de gênero/tema
                - inspiration: Inspiração opcional
                - master_personality: Personalidade do mestre
                - character_concept: Conceito do personagem
                - character_archetypes: Lista de arquétipos do personagem
                - character_approaches: Lista de abordagens do personagem
                
        Returns:
            Dicionário contendo todos os dados da campanha criada, incluindo:
                - Descrição do mundo
                - NPCs iniciais
                - Locais iniciais
                - Cena de abertura
                - Ficha completa do personagem
                - Tempo inicial da campanha
                - Missão inicial
        """
        try:
            # Preparar o prompt para o LLM com os dados da campanha
            prompt = self._prepare_prompt(campaign_data)
            
            # Chamar o LLM para gerar o conteúdo da campanha
            messages = [
                SystemMessage(content=self.system_prompt),
                HumanMessage(content=prompt)
            ]
            
            response = await self.llm.ainvoke(messages)
            
            # Processar a resposta do LLM para extrair o JSON
            campaign_json = self._extract_json_from_response(response.content)
            
            return campaign_json
            
        except Exception as e:
            # Retornar erro estruturado
            return {
                "success": False,
                "error": str(e)
            }
    
    def _prepare_prompt(self, campaign_data: Dict[str, Any]) -> str:
        """
        Prepara o prompt para o LLM com base nos dados da campanha.
        """
        return f"""
        Crie uma nova campanha de RPG com os seguintes parâmetros:
        
        # Cenário
        Nome da Campanha: {campaign_data.get('name', 'Nova Campanha')}
        Gênero/Tema: {', '.join(campaign_data.get('genre_tags', []))}
        Inspiração: {campaign_data.get('inspiration', 'Nenhuma inspiração específica')}
        
        # Mestre
        Personalidade do Mestre: {campaign_data.get('master_personality', 'serious_dark')}
        
        # Protagonista
        Conceito do Personagem: {campaign_data.get('character_concept', 'Um aventureiro em busca de seu destino')}
        Arquétipos: {', '.join(campaign_data.get('character_archetypes', []))}
        Abordagens: {', '.join(campaign_data.get('character_approaches', []))}
        
        Gere um JSON completo com todos os elementos necessários para iniciar esta campanha:
        - Descrição detalhada do mundo
        - 2-3 NPCs iniciais
        - 1-2 locais relevantes
        - Cena de abertura no tom do Mestre escolhido
        - Ficha completa do personagem
        - Tempo inicial da campanha
        - Uma missão inicial para o jogador
        
        Retorne apenas o JSON, sem explicações adicionais.
        """
    
    def _extract_json_from_response(self, response: str) -> Dict[str, Any]:
        """
        Extrai o JSON da resposta do LLM, tratando possíveis erros de formatação.
        """
        # Implementação simplificada - em produção seria mais robusta
        import json
        import re
        
        # Tentar encontrar o JSON na resposta
        json_match = re.search(r'```json\s*([\s\S]*?)\s*```', response)
        if json_match:
            json_str = json_match.group(1)
        else:
            # Se não encontrar o formato com markdown, tentar extrair todo o conteúdo
            json_str = response
        
        try:
            # Limpar possíveis caracteres indesejados
            json_str = json_str.strip()
            return json.loads(json_str)
        except json.JSONDecodeError:
            # Falha ao decodificar JSON
            return {
                "success": False,
                "error": "Falha ao decodificar resposta do LLM"
            }