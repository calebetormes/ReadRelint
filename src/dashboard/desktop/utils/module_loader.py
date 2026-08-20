import os
import sys
import importlib
import inspect
from pathlib import Path
from typing import Dict, Type, Any

class ModuleLoader:
    """
    Utilitário para varredura e carregamento dinâmico de módulos Python,
    evitando a necessidade de imports manuais em novos componentes.
    Implementa um Registry simples para recuperar as classes carregadas.
    """
    _registry: Dict[str, Type] = {}

    @classmethod
    def load_modules_from_directory(cls, base_dir: str | Path, package_prefix: str) -> None:
        """
        Faz a varredura recursiva a partir do `base_dir` e importa todos os arquivos .py.
        """
        base_path = Path(base_dir).resolve()
        
        for root, dirs, files in os.walk(base_path):
            # Ignora pastas de cache (ex: __pycache__)
            if "__pycache__" in root:
                continue

            for file in files:
                if file.endswith(".py") and file != "__init__.py":
                    file_path = Path(root) / file
                    # Calcula o caminho relativo do arquivo em relação ao base_path
                    try:
                        rel_path = file_path.relative_to(base_path)
                        # Monta o nome do módulo no formato de pacote Python
                        module_name = f"{package_prefix}.{str(rel_path.with_suffix('')).replace(os.sep, '.')}"
                        
                        # Importa o módulo dinamicamente
                        module = importlib.import_module(module_name)
                        
                        # Registra todas as classes definidas no módulo
                        for name, obj in inspect.getmembers(module, inspect.isclass):
                            if obj.__module__ == module_name:
                                cls._registry[name] = obj
                                
                    except Exception as e:
                        print(f"Erro ao carregar dinamicamente o módulo {file_path}: {e}")

    @classmethod
    def get_class(cls, class_name: str) -> Type:
        """
        Recupera uma classe previamente registrada pelo carregador dinâmico.
        """
        if class_name not in cls._registry:
            raise ValueError(f"Classe {class_name} não foi encontrada no registry de módulos dinâmicos.")
        return cls._registry[class_name]

    @classmethod
    def get_classes_by_suffix(cls, suffix: str) -> Dict[str, Type]:
        """
        Retorna todas as classes cadastradas cujo nome termina com um sufixo específico.
        """
        return {name: obj for name, obj in cls._registry.items() if name.endswith(suffix)}
