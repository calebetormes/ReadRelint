from pathlib import Path
from typing import List, Optional
from tinydb import TinyDB, Query
from src.domain.entities import IncidentReport
from src.ports.database_repo import IDatabaseRepo

class TinyDbRepo(IDatabaseRepo):
    """
    Implementação concreta (Adapter) para persistência de relatórios de incidentes
    usando o TinyDB (banco de dados NoSQL serverless armazenado em arquivo JSON local).
    """

    def __init__(self, db_path: Path):
        """
        Inicializa o repositório TinyDB apontando para o arquivo de banco fornecido.

        :param db_path: Caminho completo para o arquivo JSON do banco de dados.
        """
        # Garante que o diretório pai existe
        db_path_obj = Path(db_path)
        db_path_obj.parent.mkdir(parents=True, exist_ok=True)
        self.db = TinyDB(db_path_obj, encoding="utf-8", ensure_ascii=False)

    def save(self, report: IncidentReport) -> str:
        """
        Salva um relatório de incidente no TinyDB.

        :param report: Entidade IncidentReport a ser persistida.
        :return: ID único atribuído ao relatório persistido, convertido em string.
        """
        # Converte a entidade Pydantic para dicionário primitivo
        report_data = report.model_dump()
        
        # Insere no banco e retorna o ID gerado pelo TinyDB convertido em str
        doc_id = self.db.insert(report_data)
        return str(doc_id)

    def get_by_id(self, report_id: str) -> Optional[IncidentReport]:
        """
        Busca um relatório de incidente no TinyDB pelo ID do documento.

        :param report_id: ID do relatório a ser pesquisado.
        :return: A entidade IncidentReport correspondente, ou None se não for encontrada.
        :raises ValueError: Se o ID não puder ser convertido para um identificador válido.
        """
        try:
            doc_id_int = int(report_id)
        except ValueError:
            return None

        doc = self.db.get(doc_id=doc_id_int)
        if doc is None:
            return None

        # Transforma os dados lidos do JSON de volta na entidade IncidentReport
        return IncidentReport(**dict(doc))  # type: ignore

    def get_all(self) -> List[IncidentReport]:
        """
        Retorna todos os relatórios cadastrados no banco de dados.

        :return: Lista contendo todas as entidades IncidentReport.
        """
        all_docs = self.db.all()
        return [IncidentReport(**dict(doc)) for doc in all_docs]  # type: ignore

    def exists_by_source_file(self, filename: str) -> bool:
        """
        Verifica se um relatório originado do arquivo fornecido já existe no banco de dados.

        :param filename: Nome do arquivo PDF.
        :return: True se já existir, False caso contrário.
        """
        report_query = Query()
        return self.db.contains(report_query.source_file == filename)

