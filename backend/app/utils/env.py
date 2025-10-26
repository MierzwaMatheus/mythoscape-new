"""Módulo para carregamento de variáveis de ambiente."""

from pathlib import Path
from dotenv import load_dotenv


def load_env() -> None:
    """
    Carrega variáveis de ambiente do arquivo .env.local na raiz do projeto.
    """
    # Obtém o diretório raiz do projeto (backend)
    root_dir = Path(__file__).parent.parent.parent
    env_file = root_dir / ".env.local"
    
    # Carrega o arquivo .env.local se existir
    if env_file.exists():
        load_dotenv(env_file)
    else:
        # Fallback para .env se .env.local não existir
        load_dotenv()