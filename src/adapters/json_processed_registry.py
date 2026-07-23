import json
import threading
from typing import Optional
from pathlib import Path
from src.ports.processed_registry import IProcessedRegistry

class JsonProcessedRegistry(IProcessedRegistry):
    """
    Implementação concreta (Adapter) do IProcessedRegistry que salva o histórico
    de arquivos processados em um arquivo JSON local de maneira thread-safe.
    """

    def __init__(self, file_path: Path):
        self.file_path = Path(file_path)
        self.lock = threading.Lock()
        self._ensure_file_exists()

    def _ensure_file_exists(self) -> None:
        with self.lock:
            if not self.file_path.exists():
                self.file_path.parent.mkdir(parents=True, exist_ok=True)
                with open(self.file_path, "w", encoding="utf-8") as f:
                    json.dump({}, f)

    def _read_data(self) -> dict:
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {}

    def _write_data(self, data: dict) -> None:
        try:
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except IOError as e:
            print(f"Erro ao gravar histórico de processamento em {self.file_path}: {e}")

    def is_processed(self, filename: str, rule_name: str) -> bool:
        with self.lock:
            data = self._read_data()
            file_record = data.get(filename)
            if isinstance(file_record, dict):
                return rule_name in file_record
            return False

    def register_processed(self, filename: str, rule_name: str, status: str) -> None:
        with self.lock:
            data = self._read_data()
            if filename not in data:
                data[filename] = {}
            data[filename][rule_name] = status
            self._write_data(data)

    def clear(self) -> None:
        with self.lock:
            self._write_data({})

    def remove_record(self, filename: str, rule_name: str) -> None:
        with self.lock:
            data = self._read_data()
            if filename in data and isinstance(data[filename], dict):
                if rule_name in data[filename]:
                    del data[filename][rule_name]
                    # Se não sobrar nenhuma regra para este arquivo, limpamos a chave dele
                    if not data[filename]:
                        del data[filename]
                    self._write_data(data)

    def get_all_records(self) -> dict:
        with self.lock:
            return self._read_data()

    def save_user_edit(self, filename: str, rule_name: str, fact: str) -> None:
        with self.lock:
            data = self._read_data()
            if filename not in data:
                data[filename] = {}
            if "user_edits" not in data[filename]:
                data[filename]["user_edits"] = {}
            data[filename]["user_edits"][rule_name] = fact
            self._write_data(data)

    def get_user_edit(self, filename: str, rule_name: str) -> Optional[str]:
        with self.lock:
            data = self._read_data()
            file_record = data.get(filename)
            if isinstance(file_record, dict):
                user_edits = file_record.get("user_edits")
                if isinstance(user_edits, dict):
                    return user_edits.get(rule_name)
            return None
