"""
Utilitário para geração de relatórios de testes.
"""

import os
import json
from datetime import datetime
from typing import Dict, Any, Union, Optional


class ReportGenerator:
    """Classe para geração de relatórios de testes."""
    
    def __init__(self, report_dir: str):
        """
        Inicializa o gerador de relatórios.
        
        Args:
            report_dir: Diretório onde os relatórios serão salvos
        """
        self.report_dir = report_dir
        os.makedirs(report_dir, exist_ok=True)
    
    def generate(
        self, 
        test_name: str, 
        test_data: Dict[str, Any], 
        success: bool = True,
        details: Optional[str] = None,
        format_type: str = "txt"
    ) -> str:
        """
        Gera um relatório de teste.
        
        Args:
            test_name: Nome do teste
            test_data: Dados do teste para incluir no relatório
            success: Indica se o teste foi bem-sucedido
            details: Detalhes adicionais para incluir no relatório
            format_type: Formato do relatório (txt ou json)
            
        Returns:
            Caminho para o arquivo de relatório gerado
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{test_name}_{timestamp}.{format_type}"
        filepath = os.path.join(self.report_dir, filename)
        
        if format_type == "json":
            return self._generate_json_report(filepath, test_name, test_data, success, details)
        else:
            return self._generate_text_report(filepath, test_name, test_data, success, details)
    
    def _generate_text_report(
        self, 
        filepath: str, 
        test_name: str, 
        test_data: Dict[str, Any],
        success: bool,
        details: Optional[str]
    ) -> str:
        """Gera um relatório em formato de texto."""
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(f"=== Relatório de Teste: {test_name} ===\n")
            f.write(f"Data/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Status: {'SUCESSO' if success else 'FALHA'}\n")
            f.write("=" * 50 + "\n\n")
            
            if details:
                f.write("DETALHES:\n")
                f.write(f"{details}\n\n")
                f.write("-" * 50 + "\n\n")
            
            # Escreve os dados do teste
            for key, value in test_data.items():
                f.write(f"{key}:\n")
                if isinstance(value, (dict, list)):
                    try:
                        f.write(json.dumps(value, indent=2, ensure_ascii=False) + "\n\n")
                    except:
                        f.write(str(value) + "\n\n")
                else:
                    f.write(f"{value}\n\n")
        
        return filepath
    
    def _generate_json_report(
        self, 
        filepath: str, 
        test_name: str, 
        test_data: Dict[str, Any],
        success: bool,
        details: Optional[str]
    ) -> str:
        """Gera um relatório em formato JSON."""
        report_data = {
            "test_name": test_name,
            "timestamp": datetime.now().isoformat(),
            "success": success,
            "details": details,
            "data": test_data
        }
        
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        return filepath