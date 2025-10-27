"""
Script para execução automatizada de testes e geração de relatórios.
"""

import os
import sys
import pytest
import json
from datetime import datetime
from pathlib import Path

# Adiciona o diretório raiz ao path para importação dos módulos
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Diretório para relatórios
REPORT_DIR = os.path.join(os.path.dirname(__file__), "reports")
os.makedirs(REPORT_DIR, exist_ok=True)

# Arquivo de resumo dos testes
SUMMARY_FILE = os.path.join(REPORT_DIR, f"test_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")


def run_tests():
    """Executa os testes e gera relatórios."""
    print("Iniciando execução dos testes...")
    
    # Configura os argumentos para o pytest
    pytest_args = [
        "-v",                                  # Modo verboso
        "--asyncio-mode=auto",                 # Modo assíncrono automático
        os.path.join(os.path.dirname(__file__), "unit"),  # Diretório de testes unitários
    ]
    
    # Executa os testes
    result = pytest.main(pytest_args)
    
    # Gera o resumo dos testes
    generate_summary(result)
    
    return result


def generate_summary(result_code):
    """Gera um resumo dos testes executados."""
    # Coleta os arquivos de relatório gerados
    report_files = [f for f in os.listdir(REPORT_DIR) if f.endswith('.txt') or f.endswith('.json')]
    report_files = [f for f in report_files if not f.startswith('test_summary')]
    
    # Organiza os relatórios por tipo de teste
    reports_by_type = {}
    for file in report_files:
        test_name = file.split('_')[0]
        if test_name not in reports_by_type:
            reports_by_type[test_name] = []
        reports_by_type[test_name].append(os.path.join(REPORT_DIR, file))
    
    # Cria o resumo
    summary = {
        "timestamp": datetime.now().isoformat(),
        "success": result_code == 0,
        "exit_code": result_code,
        "report_count": len(report_files),
        "reports_by_type": reports_by_type
    }
    
    # Salva o resumo em um arquivo JSON
    with open(SUMMARY_FILE, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    
    print(f"\nResumo dos testes salvo em: {SUMMARY_FILE}")
    print(f"Total de relatórios gerados: {len(report_files)}")
    print(f"Status dos testes: {'SUCESSO' if result_code == 0 else 'FALHA'}")


if __name__ == "__main__":
    sys.exit(run_tests())