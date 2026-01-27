from __future__ import annotations

import json
import os
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from .db import DBConfig, parse_iso_datetime
from .mpp import MPPReader


@dataclass
class ImportReport:
    """Relatório detalhado de uma importação."""
    
    # Identificação
    project_id: Optional[int] = None
    import_log_id: Optional[int] = None
    source_file: str = ""
    file_storage_path: Optional[str] = None
    file_hash: Optional[str] = None
    
    # Metadados do projeto
    project_name: str = ""
    project_external_id: str = ""
    project_action: str = ""  # "created" ou "updated"
    
    # Datas do projeto
    project_start_date: Optional[str] = None
    project_finish_date: Optional[str] = None
    project_author: Optional[str] = None
    project_company: Optional[str] = None
    project_creation_date: Optional[str] = None
    project_last_saved: Optional[str] = None
    
    # Contagens
    custom_field_definitions: int = 0
    tasks: int = 0
    resources: int = 0
    assignments: int = 0
    calendars: int = 0
    dependencies: int = 0
    
    # Tempos (em ms)
    timings_ms: Dict[str, float] = field(default_factory=dict)
    
    # Timestamp
    imported_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    # Status
    success: bool = True
    error_message: Optional[str] = None
    
    def total_time_seconds(self) -> float:
        """Retorna o tempo total em segundos."""
        return self.timings_ms.get("total", 0) / 1000
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário."""
        return {
            "identification": {
                "project_id": self.project_id,
                "import_log_id": self.import_log_id,
                "source_file": self.source_file,
                "file_storage_path": self.file_storage_path,
                "file_hash": self.file_hash,
                "imported_at": self.imported_at,
            },
            "project": {
                "name": self.project_name,
                "external_id": self.project_external_id,
                "action": self.project_action,
                "start_date": self.project_start_date,
                "finish_date": self.project_finish_date,
                "author": self.project_author,
                "company": self.project_company,
                "creation_date": self.project_creation_date,
                "last_saved": self.project_last_saved,
            },
            "counts": {
                "custom_field_definitions": self.custom_field_definitions,
                "tasks": self.tasks,
                "resources": self.resources,
                "assignments": self.assignments,
                "calendars": self.calendars,
                "dependencies": self.dependencies,
            },
            "performance": {
                "timings_ms": self.timings_ms,
                "total_seconds": self.total_time_seconds(),
            },
            "status": {
                "success": self.success,
                "error_message": self.error_message,
            },
        }
    
    def to_json(self, indent: int = 2) -> str:
        """Converte para JSON formatado."""
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)
    
    def generate_text_report(self) -> str:
        """Gera o relatório em formato texto."""
        lines = []
        
        lines.append("=" * 70)
        lines.append("                    RELATÓRIO DE IMPORTAÇÃO MPP")
        lines.append("=" * 70)
        lines.append("")
        
        # Status
        status_text = "SUCESSO" if self.success else "FALHA"
        lines.append(f"Status: {status_text}")
        lines.append(f"Data/Hora: {self.imported_at}")
        lines.append("")
        
        # Projeto
        lines.append("-" * 70)
        lines.append("PROJETO")
        lines.append("-" * 70)
        lines.append(f"  Nome:         {self.project_name}")
        lines.append(f"  ID Interno:   {self.project_id}")
        lines.append(f"  External ID:  {self.project_external_id}")
        lines.append(f"  Ação:         {self.project_action}")
        if self.project_author:
            lines.append(f"  Autor:        {self.project_author}")
        if self.project_company:
            lines.append(f"  Empresa:      {self.project_company}")
        if self.project_start_date:
            lines.append(f"  Data Início:  {self.project_start_date}")
        if self.project_finish_date:
            lines.append(f"  Data Fim:     {self.project_finish_date}")
        if self.project_creation_date:
            lines.append(f"  Criado em:    {self.project_creation_date}")
        if self.project_last_saved:
            lines.append(f"  Último Save:  {self.project_last_saved}")
        lines.append("")
        
        # Contagens
        lines.append("-" * 70)
        lines.append("ENTIDADES IMPORTADAS")
        lines.append("-" * 70)
        lines.append(f"  Custom Field Definitions:  {self.custom_field_definitions:>10}")
        lines.append(f"  Tasks:                     {self.tasks:>10}")
        lines.append(f"  Resources:                 {self.resources:>10}")
        lines.append(f"  Assignments:               {self.assignments:>10}")
        lines.append(f"  Calendars:                 {self.calendars:>10}")
        lines.append(f"  Dependencies:              {self.dependencies:>10}")
        lines.append("")
        
        # Performance
        lines.append("-" * 70)
        lines.append("PERFORMANCE")
        lines.append("-" * 70)
        for phase, ms in self.timings_ms.items():
            if phase != "total":
                lines.append(f"  {phase:<35} {ms:>10.2f} ms")
        lines.append("  " + "-" * 50)
        lines.append(f"  {'TOTAL':<35} {self.total_time_seconds():>10.3f} s")
        lines.append("")
        
        # Arquivo
        lines.append("-" * 70)
        lines.append("ARQUIVO")
        lines.append("-" * 70)
        lines.append(f"  Source File:    {self.source_file}")
        if self.file_storage_path:
            lines.append(f"  Storage Path:   {self.file_storage_path}")
        if self.file_hash:
            lines.append(f"  File Hash:      {self.file_hash}")
        lines.append(f"  Import Log ID:  {self.import_log_id}")
        lines.append("")
        
        # Erro (se houver)
        if self.error_message:
            lines.append("-" * 70)
            lines.append("ERRO")
            lines.append("-" * 70)
            lines.append(f"  {self.error_message}")
            lines.append("")
        
        lines.append("=" * 70)
        lines.append("")
        
        return "\n".join(lines)
    
    def save_to_file(self, output_dir: str = ".") -> str:
        """Salva o relatório em um arquivo TXT.
        
        Args:
            output_dir: Diretório onde salvar o arquivo
            
        Returns:
            Caminho completo do arquivo salvo
        """
        # Cria nome do arquivo baseado no timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_name = "".join(c if c.isalnum() or c in "._-" else "_" for c in self.project_name)
        filename = f"import_report_{safe_name}_{timestamp}.txt"
        
        filepath = os.path.join(output_dir, filename)
        
        # Garante que o diretório existe
        os.makedirs(output_dir, exist_ok=True)
        
        # Gera e salva o relatório
        report_text = self.generate_text_report()
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(report_text)
        
        # Também salva versão JSON
        json_filepath = filepath.replace(".txt", ".json")
        with open(json_filepath, "w", encoding="utf-8") as f:
            f.write(self.to_json())
        
        return filepath
    
    def print_summary(self) -> None:
        """Imprime um resumo curto no terminal."""
        status = "OK" if self.success else "ERRO"
        print(f"[{status}] {self.project_name} - {self.total_time_seconds():.2f}s")


class Timer:
    """Context manager para medir tempo de execução."""
    
    def __init__(self, name: str, timings: Dict[str, float]):
        self.name = name
        self.timings = timings
        self.start = 0.0
    
    def __enter__(self):
        self.start = time.perf_counter()
        return self
    
    def __exit__(self, *args):
        elapsed = time.perf_counter() - self.start
        self.timings[self.name] = round(elapsed * 1000, 2)  # em ms
        print(f"  [{self.name}] {elapsed:.3f}s")


class MPPImporter:
    def __init__(self, db_config: DBConfig, created_by: int = 1):
        self.db_config = db_config
        self.created_by = created_by

    def _connect(self):
        try:
            import psycopg
        except ImportError as e:
            raise SystemExit(
                "Driver Postgres não encontrado. Instale as dependências: pip install -r requirements.txt"
            ) from e

        return psycopg.connect(self.db_config.to_dsn())

    def import_project(
        self,
        mpp_path: str,
        source_file: Optional[str] = None,
        file_storage_path: Optional[str] = None,
        file_hash: Optional[str] = None,
    ) -> ImportReport:
        """Importa um arquivo .mpp para o banco de dados.
        
        Args:
            mpp_path: Caminho local do arquivo .mpp
            source_file: Nome do arquivo original (para log)
            file_storage_path: Caminho onde o arquivo foi armazenado (ex: S3)
            file_hash: Hash SHA256 do arquivo (para detectar duplicatas)
        
        Returns:
            ImportReport com todos os detalhes da importação
        """
        total_start = time.perf_counter()
        timings: Dict[str, float] = {}
        
        # Inicializa o relatório
        report = ImportReport(
            source_file=source_file or os.path.basename(mpp_path),
            file_storage_path=file_storage_path,
            file_hash=file_hash,
        )

        try:
            # Fase 1: Leitura do arquivo .mpp
            with Timer("read_mpp_file", timings):
                reader = MPPReader(mpp_path)
                reader.read()

            # Fase 2: Extração de metadados do projeto
            with Timer("extract_project_info", timings):
                info = reader.get_project_info()

            project_name = info.get("name") or os.path.basename(mpp_path)
            project_external_id = info.get("id")
            
            if not project_external_id:
                project_external_id = str(uuid.uuid4())
            
            # Preenche dados do projeto no relatório
            report.project_name = project_name
            report.project_external_id = project_external_id
            report.project_start_date = info.get("start_date")
            report.project_finish_date = info.get("finish_date")
            report.project_author = info.get("author")
            report.project_company = info.get("company")
            report.project_creation_date = info.get("creation_date")
            report.project_last_saved = info.get("last_saved")

            # Fase 3: Conexão com banco
            with Timer("db_connect", timings):
                conn = self._connect()

            try:
                with conn.cursor() as cur:
                    with conn.transaction():
                        # Fase 4: Busca/cria projeto
                        with Timer("upsert_project", timings):
                            cur.execute(
                                """
                                SELECT id FROM pm.project
                                WHERE external_id = %s AND deleted_at IS NULL
                                LIMIT 1
                                """,
                                (project_external_id,),
                            )
                            row = cur.fetchone()
                            project_id = row[0] if row else None
                            
                            if project_id:
                                cur.execute(
                                    """
                                    UPDATE pm.project SET
                                        name = COALESCE(%s, name),
                                        start_date = COALESCE(%s, start_date),
                                        finish_date = COALESCE(%s, finish_date),
                                        author = COALESCE(%s, author),
                                        company = COALESCE(%s, company),
                                        comments = COALESCE(%s, comments),
                                        creation_date = COALESCE(%s, creation_date),
                                        last_saved = COALESCE(%s, last_saved),
                                        updated_at = CURRENT_TIMESTAMP,
                                        updated_by = %s
                                    WHERE id = %s
                                    """,
                                    (
                                        project_name,
                                        parse_iso_datetime(info.get("start_date")),
                                        parse_iso_datetime(info.get("finish_date")),
                                        info.get("author"),
                                        info.get("company"),
                                        info.get("comments"),
                                        parse_iso_datetime(info.get("creation_date")),
                                        parse_iso_datetime(info.get("last_saved")),
                                        self.created_by,
                                        project_id,
                                    ),
                                )
                                report.project_action = "updated"
                            else:
                                cur.execute(
                                    """
                                    INSERT INTO pm.project (
                                        name, external_id, start_date, finish_date, author, company, comments,
                                        creation_date, last_saved, created_by
                                    ) VALUES (
                                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                                    ) RETURNING id
                                    """,
                                    (
                                        project_name,
                                        project_external_id,
                                        parse_iso_datetime(info.get("start_date")),
                                        parse_iso_datetime(info.get("finish_date")),
                                        info.get("author"),
                                        info.get("company"),
                                        info.get("comments"),
                                        parse_iso_datetime(info.get("creation_date")),
                                        parse_iso_datetime(info.get("last_saved")),
                                        self.created_by,
                                    ),
                                )
                                project_id = cur.fetchone()[0]
                                report.project_action = "created"
                        
                        report.project_id = project_id

                        # Fase 5: Extração de custom fields
                        with Timer("extract_custom_fields", timings):
                            custom_field_definitions, _ = reader.get_custom_field_definitions()
                        
                        # Fase 6: Import custom field definitions
                        with Timer("import_custom_field_definitions", timings):
                            custom_field_count = self._import_custom_field_definitions(
                                cur, project_id, custom_field_definitions
                            )
                        report.custom_field_definitions = custom_field_count

                        # Fase 7: Extração de calendários
                        with Timer("extract_calendars", timings):
                            calendars_data = reader.get_calendars()
                        
                        # Fase 8: Import calendários
                        with Timer("import_calendars", timings):
                            calendar_count = self._import_calendars(
                                cur, project_id, calendars_data
                            )
                        report.calendars = calendar_count

                        # Fase 9: Extração de resources
                        with Timer("extract_resources", timings):
                            _, fields_by_class = reader.get_custom_field_definitions()
                            resources_data = reader.get_resources(
                                resource_custom_fields=fields_by_class.get("RESOURCE", [])
                            )
                        
                        # Fase 10: Import resources
                        with Timer("import_resources", timings):
                            resource_count, resource_id_map = self._import_resources(
                                cur, project_id, resources_data
                            )
                        report.resources = resource_count

                        # Fase 11: Extração de tasks
                        with Timer("extract_tasks", timings):
                            tasks_data = reader.get_tasks(
                                task_custom_fields=fields_by_class.get("TASK", [])
                            )
                        
                        # Fase 12: Import tasks
                        with Timer("import_tasks", timings):
                            task_count, task_id_map = self._import_tasks(
                                cur, project_id, tasks_data
                            )
                        report.tasks = task_count

                        # Calcula tempo total antes de salvar no log
                        total_elapsed = time.perf_counter() - total_start
                        timings["total"] = round(total_elapsed * 1000, 2)
                        report.timings_ms = timings

                        # Fase 13: Registra log de importação
                        with Timer("create_import_log", timings):
                            cur.execute(
                                """
                                INSERT INTO pm.import_log (
                                    project_id, source_file, file_storage_path, file_hash,
                                    custom_field_definitions, tasks, resources, assignments,
                                    calendars, dependencies, total_time_ms, timings_ms,
                                    status, error_message, stats, created_by
                                ) VALUES (
                                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                                ) RETURNING id
                                """,
                                (
                                    project_id,
                                    report.source_file,
                                    file_storage_path,
                                    file_hash,
                                    report.custom_field_definitions,
                                    report.tasks,
                                    report.resources,
                                    report.assignments,
                                    report.calendars,
                                    report.dependencies,
                                    timings.get("total"),
                                    json.dumps(timings),
                                    "completed",
                                    None,
                                    json.dumps({
                                        "project_action": report.project_action,
                                        "project_name": report.project_name,
                                        "project_external_id": report.project_external_id,
                                    }),
                                    self.created_by,
                                ),
                            )
                            report.import_log_id = cur.fetchone()[0]
            finally:
                conn.close()

            report.success = True

        except Exception as e:
            report.success = False
            report.error_message = str(e)
            
            # Tenta salvar o erro no banco
            try:
                # Calcula tempo até o erro
                total_elapsed = time.perf_counter() - total_start
                timings["total"] = round(total_elapsed * 1000, 2)
                report.timings_ms = timings
                
                # Conecta novamente para salvar o erro
                conn = self._connect()
                try:
                    with conn.cursor() as cur:
                        cur.execute(
                            """
                            INSERT INTO pm.import_log (
                                project_id, source_file, file_storage_path, file_hash,
                                custom_field_definitions, tasks, resources, assignments,
                                calendars, dependencies, total_time_ms, timings_ms,
                                status, error_message, stats, created_by
                            ) VALUES (
                                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                            ) RETURNING id
                            """,
                            (
                                report.project_id,
                                report.source_file,
                                report.file_storage_path,
                                report.file_hash,
                                report.custom_field_definitions,
                                report.tasks,
                                report.resources,
                                report.assignments,
                                report.calendars,
                                report.dependencies,
                                timings.get("total"),
                                json.dumps(timings),
                                "failed",
                                str(e),
                                json.dumps({
                                    "project_action": report.project_action,
                                    "project_name": report.project_name,
                                    "project_external_id": report.project_external_id,
                                }),
                                self.created_by,
                            ),
                        )
                        report.import_log_id = cur.fetchone()[0]
                finally:
                    conn.close()
            except Exception as db_error:
                # Se falhar ao salvar no banco, apenas loga
                print(f"Erro ao salvar log de importação no banco: {db_error}")
            
            raise

        finally:
            # Atualiza timings no report se ainda não foi calculado (caso de erro)
            if "total" not in report.timings_ms:
                total_elapsed = time.perf_counter() - total_start
                timings["total"] = round(total_elapsed * 1000, 2)
                report.timings_ms = timings
            
            # Imprime resumo curto
            report.print_summary()

        return report

    def _import_custom_field_definitions(
        self,
        cur,
        project_id: int,
        definitions: List[Dict[str, Any]],
    ) -> int:
        """Importa definições de campos customizados para o projeto.
        
        Usa UPSERT para atualizar definições existentes ou inserir novas.
        
        Returns:
            Número de definições importadas/atualizadas.
        """
        if not definitions:
            return 0

        count = 0
        for defn in definitions:
            field_type = defn.get("field_type")
            field_class = defn.get("field_class")
            
            if not field_type or not field_class:
                continue

            # UPSERT: atualiza se já existe, senão insere
            cur.execute(
                """
                INSERT INTO pm.custom_field_definition (
                    project_id, field_type, field_class, alias, data_type, created_by
                ) VALUES (
                    %s, %s, %s, %s, %s, %s
                )
                ON CONFLICT (project_id, field_type, field_class)
                WHERE deleted_at IS NULL
                DO UPDATE SET
                    alias = EXCLUDED.alias,
                    data_type = EXCLUDED.data_type,
                    updated_by = EXCLUDED.created_by,
                    updated_at = CURRENT_TIMESTAMP
                """,
                (
                    project_id,
                    field_type,
                    field_class,
                    defn.get("alias"),
                    defn.get("data_type", "STRING"),
                    self.created_by,
                ),
            )
            count += 1

        return count

    def _import_calendars(
        self,
        cur,
        project_id: int,
        calendars: List[Dict[str, Any]],
    ) -> int:
        """Importa calendários do projeto.
        
        Os calendários são importados em duas passadas:
        1. Primeiro insere todos os calendários (sem parent)
        2. Depois atualiza os parent_calendar_id
        
        Returns:
            Número de calendários importados/atualizados.
        """
        if not calendars:
            return 0

        # Mapa de external_id -> calendar_id (do banco)
        external_to_db_id: Dict[str, int] = {}
        
        # Primeira passada: UPSERT de todos os calendários
        for cal in calendars:
            external_id = cal.get("external_id")
            name = cal.get("name")
            
            if not name:
                continue
            
            # UPSERT do calendário
            cur.execute(
                """
                INSERT INTO pm.calendar (
                    project_id, external_id, name, created_by
                ) VALUES (
                    %s, %s, %s, %s
                )
                ON CONFLICT (project_id, external_id)
                WHERE deleted_at IS NULL AND external_id IS NOT NULL
                DO UPDATE SET
                    name = EXCLUDED.name,
                    updated_by = EXCLUDED.created_by,
                    updated_at = CURRENT_TIMESTAMP
                RETURNING id
                """,
                (project_id, external_id, name, self.created_by),
            )
            row = cur.fetchone()
            calendar_id = row[0] if row else None
            
            if calendar_id and external_id:
                external_to_db_id[external_id] = calendar_id

        # Segunda passada: atualiza parent_calendar_id
        for cal in calendars:
            external_id = cal.get("external_id")
            parent_external_id = cal.get("parent_external_id")
            
            if not external_id or not parent_external_id:
                continue
            
            calendar_id = external_to_db_id.get(external_id)
            parent_id = external_to_db_id.get(parent_external_id)
            
            if calendar_id and parent_id:
                cur.execute(
                    """
                    UPDATE pm.calendar SET
                        parent_calendar_id = %s,
                        updated_by = %s,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = %s
                    """,
                    (parent_id, self.created_by, calendar_id),
                )

        # Terceira passada: importa weekdays, working_times e exceptions
        for cal in calendars:
            external_id = cal.get("external_id")
            if not external_id:
                continue
            
            calendar_id = external_to_db_id.get(external_id)
            if not calendar_id:
                continue
            
            # Importa dias da semana
            for weekday in cal.get("weekdays", []):
                cur.execute(
                    """
                    INSERT INTO pm.calendar_weekday (
                        calendar_id, day_of_week, working, created_by
                    ) VALUES (
                        %s, %s, %s, %s
                    )
                    ON CONFLICT (calendar_id, day_of_week)
                    WHERE deleted_at IS NULL
                    DO UPDATE SET
                        working = EXCLUDED.working,
                        updated_by = EXCLUDED.created_by,
                        updated_at = CURRENT_TIMESTAMP
                    """,
                    (
                        calendar_id,
                        weekday.get("day_of_week"),
                        weekday.get("working", False),
                        self.created_by,
                    ),
                )
            
            # Limpa working times antigos e insere novos
            cur.execute(
                """
                UPDATE pm.calendar_working_time SET
                    deleted_at = CURRENT_TIMESTAMP,
                    deleted_by = %s
                WHERE calendar_id = %s AND deleted_at IS NULL
                """,
                (self.created_by, calendar_id),
            )
            
            for wt in cal.get("working_times", []):
                if wt.get("start_time") and wt.get("end_time"):
                    cur.execute(
                        """
                        INSERT INTO pm.calendar_working_time (
                            calendar_id, day_of_week, start_time, end_time, created_by
                        ) VALUES (
                            %s, %s, %s, %s, %s
                        )
                        """,
                        (
                            calendar_id,
                            wt.get("day_of_week"),
                            wt.get("start_time"),
                            wt.get("end_time"),
                            self.created_by,
                        ),
                    )
            
            # Importa exceções
            for exc in cal.get("exceptions", []):
                from_date = exc.get("from_date")
                if not from_date:
                    continue
                
                # Por simplicidade, usa apenas from_date como exception_date
                # Para ranges de data, seria necessário expandir
                cur.execute(
                    """
                    INSERT INTO pm.calendar_exception (
                        calendar_id, exception_date, working, created_by
                    ) VALUES (
                        %s, %s, %s, %s
                    )
                    ON CONFLICT (calendar_id, exception_date)
                    WHERE deleted_at IS NULL
                    DO UPDATE SET
                        working = EXCLUDED.working,
                        updated_by = EXCLUDED.created_by,
                        updated_at = CURRENT_TIMESTAMP
                    """,
                    (
                        calendar_id,
                        from_date,
                        exc.get("working", False),
                        self.created_by,
                    ),
                )

        return len(external_to_db_id)

    def _import_resources(
        self,
        cur,
        project_id: int,
        resources: List[Dict[str, Any]],
    ) -> Tuple[int, Dict[str, int]]:
        """Importa recursos do projeto.
        
        Returns:
            Tuple com:
            - Número de recursos importados/atualizados
            - Mapa de external_id -> resource_id (do banco)
        """
        if not resources:
            return 0, {}

        external_to_db_id: Dict[str, int] = {}
        
        for res in resources:
            external_id = res.get("external_id")
            name = res.get("name")
            
            # Resources sem nome são ignorados (ex: "Unassigned")
            if not name:
                continue
            
            # UPSERT do resource
            cur.execute(
                """
                INSERT INTO pm.resource (
                    project_id, external_id, name, email, type, "group",
                    max_units, standard_rate, cost, notes, custom_fields, created_by
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
                ON CONFLICT (project_id, external_id)
                WHERE deleted_at IS NULL AND external_id IS NOT NULL
                DO UPDATE SET
                    name = EXCLUDED.name,
                    email = EXCLUDED.email,
                    type = EXCLUDED.type,
                    "group" = EXCLUDED."group",
                    max_units = EXCLUDED.max_units,
                    standard_rate = EXCLUDED.standard_rate,
                    cost = EXCLUDED.cost,
                    notes = EXCLUDED.notes,
                    custom_fields = EXCLUDED.custom_fields,
                    updated_by = EXCLUDED.created_by,
                    updated_at = CURRENT_TIMESTAMP
                RETURNING id
                """,
                (
                    project_id,
                    external_id,
                    name,
                    res.get("email"),
                    res.get("type"),
                    res.get("group"),
                    res.get("max_units"),
                    res.get("standard_rate"),
                    res.get("cost"),
                    res.get("notes"),
                    json.dumps(res.get("custom_fields", {})),
                    self.created_by,
                ),
            )
            row = cur.fetchone()
            resource_id = row[0] if row else None
            
            if resource_id and external_id:
                external_to_db_id[external_id] = resource_id

        return len(external_to_db_id), external_to_db_id

    def _import_tasks(
        self,
        cur,
        project_id: int,
        tasks: List[Dict[str, Any]],
    ) -> Tuple[int, Dict[str, int]]:
        """Importa tarefas do projeto.
        
        Returns:
            Tuple com:
            - Número de tarefas importadas/atualizadas
            - Mapa de external_id -> task_id (do banco)
        """
        if not tasks:
            return 0, {}

        external_to_db_id: Dict[str, int] = {}
        
        for task in tasks:
            external_id = task.get("external_id")
            name = task.get("name")
            
            # Tasks sem nome são ignoradas
            if not name:
                continue
            
            # UPSERT da task
            cur.execute(
                """
                INSERT INTO pm.task (
                    project_id, external_id, name, start_date, finish_date,
                    duration, work, percent_complete, priority, notes, wbs,
                    outline_level, milestone, summary, custom_fields, created_by
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
                ON CONFLICT (project_id, external_id)
                WHERE deleted_at IS NULL AND external_id IS NOT NULL
                DO UPDATE SET
                    name = EXCLUDED.name,
                    start_date = EXCLUDED.start_date,
                    finish_date = EXCLUDED.finish_date,
                    duration = EXCLUDED.duration,
                    work = EXCLUDED.work,
                    percent_complete = EXCLUDED.percent_complete,
                    priority = EXCLUDED.priority,
                    notes = EXCLUDED.notes,
                    wbs = EXCLUDED.wbs,
                    outline_level = EXCLUDED.outline_level,
                    milestone = EXCLUDED.milestone,
                    summary = EXCLUDED.summary,
                    custom_fields = EXCLUDED.custom_fields,
                    updated_by = EXCLUDED.created_by,
                    updated_at = CURRENT_TIMESTAMP
                RETURNING id
                """,
                (
                    project_id,
                    external_id,
                    name,
                    parse_iso_datetime(task.get("start")),
                    parse_iso_datetime(task.get("finish")),
                    task.get("duration"),
                    task.get("work"),
                    task.get("percent_complete", 0),
                    task.get("priority"),
                    task.get("notes"),
                    task.get("wbs"),
                    task.get("outline_level", 0),
                    task.get("milestone", False),
                    task.get("summary", False),
                    json.dumps(task.get("custom_fields", {})),
                    self.created_by,
                ),
            )
            row = cur.fetchone()
            task_id = row[0] if row else None
            
            if task_id and external_id:
                external_to_db_id[external_id] = task_id

        return len(external_to_db_id), external_to_db_id
