"""
Agente de criação de campanhas - responsável por gerar o mundo inicial, NPCs e cena de abertura.
"""

from typing import Dict, Any
import json
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from app.utils.env import get_env_var
from app.services.supabase import get_supabase_client


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
        Cria uma nova campanha com base nos dados fornecidos pelo usuário e persiste no Supabase.
        
        Args:
            campaign_data: Dicionário contendo os dados iniciais da campanha:
                - name: Nome da campanha
                - genre_tags: Lista de tags de gênero/tema
                - inspiration: Inspiração opcional
                - master_personality: Personalidade do mestre
                - character_concept: Conceito do personagem
                - character_archetypes: Lista de arquétipos do personagem
                - character_approaches: Lista de abordagens do personagem
                - user_id: ID do usuário autenticado
                
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
            
            # Adicionar o ID do usuário ao JSON da campanha
            user_id = campaign_data.get("user_id")
            if not user_id:
                raise ValueError("ID do usuário não fornecido")
            
            # Persistir os dados no Supabase
            supabase = get_supabase_client()
            
            # Preparar dados para inserção na tabela campaigns
            campaign_record = {
                "name": campaign_data.get("name"),
                "user_id": user_id,
                "genre_tags": json.dumps(campaign_data.get("genre_tags", [])),
                "master_personality": campaign_data.get("master_personality"),
                "world_description": campaign_json.get("campaign", {}).get("world_description", ""),
                "campaign_data": json.dumps(campaign_json)
            }
            
            # Inserir na tabela campaigns
            result = supabase.table("campaigns").insert(campaign_record).execute()
            
            # Verificar se a inserção foi bem-sucedida
            if not result.data:
                raise Exception("Falha ao salvar campanha no banco de dados")
                
            # Adicionar o ID da campanha ao resultado
            campaign_id = result.data[0].get("id")
            campaign_json["id"] = campaign_id
            
            # Persistir dados relacionados (world, execution_logs)
            self._persist_related_data(campaign_id, user_id, campaign_json)
            
            return campaign_json
            
        except Exception as e:
            # Retornar erro estruturado
            return {
                "success": False,
                "error_message": str(e)
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
            
    def _persist_related_data(self, campaign_id: str, user_id: str, campaign_json: Dict[str, Any]) -> None:
        """
        Persiste dados relacionados à campanha em tabelas adicionais.
        
        Args:
            campaign_id: ID da campanha criada
            user_id: ID do usuário
            campaign_json: Dados completos da campanha gerados pelo LLM
        """
        try:
            # Obtém o cliente Supabase com as credenciais de serviço para bypass do RLS
            from app.services.supabase import get_supabase_admin_client
            supabase = get_supabase_admin_client()
            
            # 1. Persistir dados do mundo na tabela worlds
            mundo_data = campaign_json.get("mundo", {})
            if mundo_data:
                # Extrair dados do mundo conforme a estrutura do JSON
                world_record = {
                    "user_id": user_id,
                    "campaign_id": campaign_id,  # Adicionando o campaign_id para associar o mundo à campanha
                    "name": campaign_json.get("campanha", {}).get("nome", "Mundo sem nome"),
                    "description": mundo_data.get("descricao", ""),
                    "genre_tags": json.dumps(campaign_json.get("campanha", {}).get("genero_tema", "").split(", ")),
                    "master_personality": campaign_json.get("mestre", {}).get("personalidade", "serious_dark"),
                    "world_data": json.dumps(mundo_data)
                }
                
                # Adicionamos o campaign_time conforme definido no db_setup.sql
                # Extrair o tempo inicial do mundo, se disponível
                tempo_inicial = mundo_data.get("tempo_inicial", "")
                campaign_time = {
                    "day": 1, 
                    "hour": 12, 
                    "minute": 0, 
                    "season": "spring", 
                    "year": 1,
                    "description": tempo_inicial
                }
                world_record["campaign_time"] = json.dumps(campaign_time)
                
                # Inserir registro na tabela worlds
                result = supabase.table("worlds").insert(world_record).execute()
                print(f"✅ Dados do mundo persistidos com sucesso: {world_record['name']}")
                print(f"Resultado da inserção do mundo: {result.data}")
            
            # 2. Persistir dados do personagem (protagonista)
            personagem_data = campaign_json.get("protagonista", {})
            if personagem_data:
                # Extrair dados do personagem conforme a estrutura do JSON
                character_record = {
                    "user_id": user_id,
                    "campaign_id": campaign_id,
                    "name": personagem_data.get("ficha", {}).get("nome", "Personagem sem nome"),
                    "character_class": personagem_data.get("ficha", {}).get("classe", ""),
                    "level": personagem_data.get("ficha", {}).get("nivel", 1),
                    # Armazenar todos os dados do personagem em um único campo JSONB
                    "character_data": json.dumps(personagem_data)
                }
                
                # Inserir registro na tabela characters (se existir)
                try:
                    result = supabase.table("characters").insert(character_record).execute()
                    print(f"✅ Dados do personagem persistidos com sucesso: {character_record['name']}")
                    print(f"Resultado da inserção do personagem: {result.data}")
                except Exception as char_error:
                    print(f"Erro ao persistir dados do personagem: {str(char_error)}")
            
            # 3. Registrar log de execução
            try:
                log_record = {
                    "user_id": user_id,
                    "input_text": "Criação de campanha",
                    "output_narrative": f"Campanha '{campaign_json.get('campanha', {}).get('nome', 'Sem nome')}' criada com sucesso",
                    "execution_time": 0.0,  # Em uma implementação real, calcularíamos o tempo
                    "agents_used": json.dumps(["campaign_creation"]),
                    "success": True,
                    "metadata": json.dumps({"campaign_id": campaign_id})
                }
                
                result = supabase.table("execution_logs").insert(log_record).execute()
                print("✅ Log de execução registrado com sucesso")
                print(f"Resultado da inserção do log: {result.data}")
            except Exception as log_error:
                print(f"Erro ao registrar log de execução: {str(log_error)}")
            
        except Exception as e:
            # Apenas logamos o erro, mas não interrompemos o fluxo principal
            print(f"Erro ao persistir dados relacionados: {str(e)}")
            # Em produção, usaríamos um logger apropriado