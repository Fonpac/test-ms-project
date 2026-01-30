from __future__ import annotations

import json
import os
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

from .db import DBConfig, parse_iso_datetime
from .mpp import MPPReader


@dataclass
class ImportReport:
    """Relatório detalhado de uma importação."""
    
    # Identificação
    masterplan_id: Optional[int] = None
    import_log_id: Optional[int] = None
    source_file: str = ""
    file_storage_path: Optional[str] = None
    file_hash: Optional[str] = None
    
    # Metadados do projeto
    masterplan_name: str = ""
    masterplan_external_id: str = ""
    masterplan_action: str = ""  # "created" ou "updated"
    
    # Datas do projeto
    masterplan_start_date: Optional[str] = None
    masterplan_finish_date: Optional[str] = None
    masterplan_author: Optional[str] = None
    masterplan_company: Optional[str] = None
    masterplan_creation_date: Optional[str] = None
    masterplan_last_saved: Optional[str] = None
    
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
                "masterplan_id": self.masterplan_id,
                "import_log_id": self.import_log_id,
                "source_file": self.source_file,
                "file_storage_path": self.file_storage_path,
                "file_hash": self.file_hash,
                "imported_at": self.imported_at,
            },
            "project": {
                "name": self.masterplan_name,
                "external_id": self.masterplan_external_id,
                "action": self.masterplan_action,
                "start_date": self.masterplan_start_date,
                "finish_date": self.masterplan_finish_date,
                "author": self.masterplan_author,
                "company": self.masterplan_company,
                "creation_date": self.masterplan_creation_date,
                "last_saved": self.masterplan_last_saved,
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
        lines.append(f"  Nome:         {self.masterplan_name}")
        lines.append(f"  ID Interno:   {self.masterplan_id}")
        lines.append(f"  External ID:  {self.masterplan_external_id}")
        lines.append(f"  Ação:         {self.masterplan_action}")
        if self.masterplan_author:
            lines.append(f"  Autor:        {self.masterplan_author}")
        if self.masterplan_company:
            lines.append(f"  Empresa:      {self.masterplan_company}")
        if self.masterplan_start_date:
            lines.append(f"  Data Início:  {self.masterplan_start_date}")
        if self.masterplan_finish_date:
            lines.append(f"  Data Fim:     {self.masterplan_finish_date}")
        if self.masterplan_creation_date:
            lines.append(f"  Criado em:    {self.masterplan_creation_date}")
        if self.masterplan_last_saved:
            lines.append(f"  Último Save:  {self.masterplan_last_saved}")
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
        safe_name = "".join(c if c.isalnum() or c in "._-" else "_" for c in self.masterplan_name)
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
        print(f"[{status}] {self.masterplan_name} - {self.total_time_seconds():.2f}s")


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
        masterplan_external_id: Optional[str] = None,
    ) -> ImportReport:
        """Importa um arquivo .mpp para o banco de dados.
        
        Args:
            mpp_path: Caminho local do arquivo .mpp
            source_file: Nome do arquivo original (para log)
            file_storage_path: Caminho onde o arquivo foi armazenado (ex: S3)
            file_hash: Hash SHA256 do arquivo (para detectar duplicatas)
            masterplan_external_id: UUID do masterplan para atualização (opcional).
                Se fornecido, será usado ao invés do external_id do arquivo ou gerado.
        
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

            masterplan_name = info.get("name") or os.path.basename(mpp_path)
            
            # Se masterplan_external_id foi fornecido, usa ele (para atualização)
            # Caso contrário, tenta pegar do arquivo ou gera um novo
            if masterplan_external_id:
                # Usa o UUID fornecido (para atualização de masterplan existente)
                pass
            else:
                masterplan_external_id = info.get("id")
                if not masterplan_external_id:
                    masterplan_external_id = str(uuid.uuid4())
            
            # Preenche dados do projeto no relatório
            report.masterplan_name = masterplan_name
            report.masterplan_external_id = masterplan_external_id
            report.masterplan_start_date = info.get("start_date")
            report.masterplan_finish_date = info.get("finish_date")
            report.masterplan_author = info.get("author")
            report.masterplan_company = info.get("company")
            report.masterplan_creation_date = info.get("creation_date")
            report.masterplan_last_saved = info.get("last_saved")

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
                                SELECT id FROM pm.masterplan
                                WHERE external_id = %s AND deleted_at IS NULL
                                LIMIT 1
                                """,
                                (masterplan_external_id,),
                            )
                            row = cur.fetchone()
                            masterplan_id = row[0] if row else None
                            
                            if masterplan_id:
                                cur.execute(
                                    """
                                    UPDATE pm.masterplan SET
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
                                        masterplan_name,
                                        parse_iso_datetime(info.get("start_date")),
                                        parse_iso_datetime(info.get("finish_date")),
                                        info.get("author"),
                                        info.get("company"),
                                        info.get("comments"),
                                        parse_iso_datetime(info.get("creation_date")),
                                        parse_iso_datetime(info.get("last_saved")),
                                        self.created_by,
                                        masterplan_id,
                                    ),
                                )
                                report.masterplan_action = "updated"
                            else:
                                cur.execute(
                                    """
                                    INSERT INTO pm.masterplan (
                                        name, external_id, start_date, finish_date, author, company, comments,
                                        creation_date, last_saved, created_by
                                    ) VALUES (
                                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                                    ) RETURNING id
                                    """,
                                    (
                                        masterplan_name,
                                        masterplan_external_id,
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
                                masterplan_id = cur.fetchone()[0]
                                report.masterplan_action = "created"
                        
                        report.masterplan_id = masterplan_id

                        # Inicializa contadores de baseline e timephased
                        baseline_count = 0
                        task_baseline_count = 0
                        resource_baseline_count = 0
                        timephased_planned_rows = 0
                        timephased_complete_rows = 0
                        timephased_assignments_with_data = 0
                        timephased_negative_values_count = 0

                        # Fase 5: Extração de custom fields (cache para reuso)
                        with Timer("extract_custom_fields", timings):
                            custom_field_definitions, fields_by_class = reader.get_custom_field_definitions()
                        
                        # Fase 6: Import custom field definitions
                        with Timer("import_custom_field_definitions", timings):
                            custom_field_count = self._import_custom_field_definitions(
                                cur, masterplan_id, custom_field_definitions
                            )
                        report.custom_field_definitions = custom_field_count

                        # Fase 7: Extração de calendários
                        with Timer("extract_calendars", timings):
                            calendars_data = reader.get_calendars()
                        
                        # Fase 8: Import calendários
                        with Timer("import_calendars", timings):
                            calendar_count = self._import_calendars(
                                cur, masterplan_id, calendars_data
                            )
                        report.calendars = calendar_count

                        # Fase 9: Descobre baselines (antes de extrair tasks/resources para usar nos bundles)
                        with Timer("discover_baselines", timings):
                            baselines_meta = reader.get_baseline_indices_and_names()
                            baseline_indices = [b["index"] for b in baselines_meta] if baselines_meta else []

                        # Fase 10: Extração otimizada de resources + resource baselines (single pass)
                        with Timer("extract_resources", timings):
                            resources_data, resource_baselines_data = reader.extract_resources_bundle(
                                resource_custom_fields=fields_by_class.get("RESOURCE", []),
                                baseline_indices=baseline_indices if baseline_indices else None,
                            )
                        
                        # Fase 11: Import resources
                        with Timer("import_resources", timings):
                            resource_count, resource_id_map = self._import_resources(
                                cur, masterplan_id, resources_data
                            )
                        report.resources = resource_count

                        # Fase 12: Extração otimizada de tasks + dependencies + task baselines (single pass)
                        with Timer("extract_tasks", timings):
                            tasks_data, dependencies_data, task_baselines_data = reader.extract_tasks_bundle(
                                task_custom_fields=fields_by_class.get("TASK", []),
                                baseline_indices=baseline_indices if baseline_indices else None,
                            )
                        
                        # Fase 13: Import tasks
                        with Timer("import_tasks", timings):
                            task_count, task_id_map = self._import_tasks(
                                cur, masterplan_id, tasks_data
                            )
                        report.tasks = task_count

                        # Fase 14: Extração de assignments
                        with Timer("extract_assignments", timings):
                            assignments_data = reader.get_assignments(
                                assignment_custom_fields=fields_by_class.get("ASSIGNMENT", [])
                            )
                        
                        # Fase 15: Import assignments
                        with Timer("import_assignments", timings):
                            assignment_count = self._import_assignments(
                                cur, masterplan_id, assignments_data, task_id_map, resource_id_map
                            )
                        report.assignments = assignment_count

                        # Fase 16: Extração de timephased data
                        with Timer("extract_timephased", timings):
                            timephased_data, negative_values_count = reader.get_assignment_timephased()
                        
                        # Fase 17: Import timephased data
                        with Timer("import_timephased", timings):
                            planned_rows, complete_rows, assignments_with_timephased = self._import_assignment_timephased(
                                cur, masterplan_id, timephased_data
                            )
                        timephased_planned_rows = planned_rows
                        timephased_complete_rows = complete_rows
                        timephased_assignments_with_data = assignments_with_timephased
                        timephased_negative_values_count = negative_values_count

                        # Fase 18: Import dependencies (já extraídas no bundle)
                        with Timer("import_dependencies", timings):
                            dependency_count = self._import_dependencies(
                                cur, masterplan_id, dependencies_data, task_id_map
                            )
                        report.dependencies = dependency_count

                        # Fase 19: Import baselines (já extraídas nos bundles)
                        with Timer("import_baselines", timings):
                            baseline_id_map = self._import_baselines(
                                cur, masterplan_id, baselines_meta
                            )
                            task_baseline_count = self._import_task_baselines(
                                cur, baseline_id_map, task_id_map, task_baselines_data
                            )
                            resource_baseline_count = self._import_resource_baselines(
                                cur, baseline_id_map, resource_id_map, resource_baselines_data
                            )
                        
                        # Atualiza stats com contagens de baseline
                        baseline_count = len(baseline_id_map) if baselines_meta else 0

                        # Calcula tempo total antes de salvar no log
                        total_elapsed = time.perf_counter() - total_start
                        timings["total"] = round(total_elapsed * 1000, 2)
                        report.timings_ms = timings

                        # Fase 21: Registra log de importação
                        with Timer("create_import_log", timings):
                            cur.execute(
                                """
                                INSERT INTO pm.import_log (
                                    masterplan_id, source_file, file_storage_path, file_hash,
                                    custom_field_definitions, tasks, resources, assignments,
                                    calendars, dependencies, total_time_ms, timings_ms,
                                    status, error_message, stats, created_by
                                ) VALUES (
                                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                                ) RETURNING id
                                """,
                                (
                                    masterplan_id,
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
                                        "masterplan_action": report.masterplan_action,
                                        "masterplan_name": report.masterplan_name,
                                        "masterplan_external_id": report.masterplan_external_id,
                                        "baselines_count": baseline_count,
                                        "task_baselines_count": task_baseline_count,
                                        "resource_baselines_count": resource_baseline_count,
                                        "timephased_planned_rows": timephased_planned_rows,
                                        "timephased_complete_rows": timephased_complete_rows,
                                        "timephased_assignments_with_data": timephased_assignments_with_data,
                                        "timephased_negative_values_count": timephased_negative_values_count,
                                        "optimization": {
                                            "bulk_inserts_enabled": True,
                                            "single_pass_extraction": True,
                                            "baseline_discovery_optimized": True,
                                        },
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
                                masterplan_id, source_file, file_storage_path, file_hash,
                                custom_field_definitions, tasks, resources, assignments,
                                calendars, dependencies, total_time_ms, timings_ms,
                                status, error_message, stats, created_by
                            ) VALUES (
                                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                            ) RETURNING id
                            """,
                            (
                                report.masterplan_id,
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
                                    "masterplan_action": report.masterplan_action,
                                    "masterplan_name": report.masterplan_name,
                                    "masterplan_external_id": report.masterplan_external_id,
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
        masterplan_id: int,
        definitions: List[Dict[str, Any]],
    ) -> int:
        """Importa definições de campos customizados usando bulk insert (otimizado).
        
        Returns:
            Número de definições importadas/atualizadas.
        """
        if not definitions:
            return 0

        # Prepara todas as linhas em memória
        rows: List[Tuple[Any, ...]] = []
        
        for defn in definitions:
            field_type = defn.get("field_type")
            field_class = defn.get("field_class")
            
            if not field_type or not field_class:
                continue
            
            rows.append((
                masterplan_id,
                field_type,
                field_class,
                defn.get("alias"),
                defn.get("data_type", "STRING"),
                self.created_by,
            ))
        
        if not rows:
            return 0
        
        # Bulk insert com executemany
        cur.executemany(
            """
            INSERT INTO pm.custom_field_definition (
                masterplan_id, field_type, field_class, alias, data_type, created_by
            ) VALUES (
                %s, %s, %s, %s, %s, %s
            )
            ON CONFLICT (masterplan_id, field_type, field_class)
            WHERE deleted_at IS NULL
            DO UPDATE SET
                alias = EXCLUDED.alias,
                data_type = EXCLUDED.data_type,
                updated_by = EXCLUDED.created_by,
                updated_at = CURRENT_TIMESTAMP
            """,
            rows,
        )

        return len(rows)

    def _import_calendars(
        self,
        cur,
        masterplan_id: int,
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

        # Prepara linhas de calendários para bulk insert
        calendar_rows: List[Tuple[Any, ...]] = []
        valid_external_ids: List[str] = []
        parent_updates: List[Tuple[int, str]] = []  # (calendar_id, parent_external_id)
        
        for cal in calendars:
            external_id = cal.get("external_id")
            name = cal.get("name")
            
            if not name or not external_id:
                continue
            
            calendar_rows.append((
                masterplan_id,
                external_id,
                name,
                self.created_by,
            ))
            valid_external_ids.append(external_id)
        
        if not calendar_rows:
            return 0
        
        # Bulk insert de calendários
        cur.executemany(
            """
            INSERT INTO pm.calendar (
                masterplan_id, external_id, name, created_by
            ) VALUES (
                %s, %s, %s, %s
            )
            ON CONFLICT (masterplan_id, external_id)
            WHERE deleted_at IS NULL AND external_id IS NOT NULL
            DO UPDATE SET
                name = EXCLUDED.name,
                updated_by = EXCLUDED.created_by,
                updated_at = CURRENT_TIMESTAMP
            """,
            calendar_rows,
        )
        
        # Busca todos os IDs com um único SELECT
        cur.execute(
            """
            SELECT id, external_id FROM pm.calendar
            WHERE masterplan_id = %s AND external_id = ANY(%s) AND deleted_at IS NULL
            """,
            (masterplan_id, valid_external_ids),
        )
        
        external_to_db_id: Dict[str, int] = {}
        for row in cur.fetchall():
            calendar_id, external_id = row
            if external_id:
                external_to_db_id[external_id] = calendar_id
        
        # Prepara updates de parent_calendar_id
        parent_update_rows: List[Tuple[int, int]] = []
        for cal in calendars:
            external_id = cal.get("external_id")
            parent_external_id = cal.get("parent_external_id")
            
            if not external_id or not parent_external_id:
                continue
            
            calendar_id = external_to_db_id.get(external_id)
            parent_id = external_to_db_id.get(parent_external_id)
            
            if calendar_id and parent_id:
                parent_update_rows.append((parent_id, calendar_id))
        
        # Bulk update de parent_calendar_id
        if parent_update_rows:
            cur.executemany(
                """
                UPDATE pm.calendar SET
                    parent_calendar_id = %s,
                    updated_by = %s,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
                """,
                [(parent_id, self.created_by, calendar_id) for parent_id, calendar_id in parent_update_rows],
            )

        # Prepara linhas de weekdays, working_times e exceptions
        weekday_rows: List[Tuple[Any, ...]] = []
        working_time_rows: List[Tuple[Any, ...]] = []
        exception_rows: List[Tuple[Any, ...]] = []
        calendar_ids_for_delete: List[int] = []
        
        for cal in calendars:
            external_id = cal.get("external_id")
            if not external_id:
                continue
            
            calendar_id = external_to_db_id.get(external_id)
            if not calendar_id:
                continue
            
            calendar_ids_for_delete.append(calendar_id)
            
            # Prepara weekdays
            for weekday in cal.get("weekdays", []):
                weekday_rows.append((
                    calendar_id,
                    weekday.get("day_of_week"),
                    weekday.get("working", False),
                    self.created_by,
                ))
            
            # Prepara working_times
            for wt in cal.get("working_times", []):
                if wt.get("start_time") and wt.get("end_time"):
                    working_time_rows.append((
                        calendar_id,
                        wt.get("day_of_week"),
                        wt.get("start_time"),
                        wt.get("end_time"),
                        self.created_by,
                    ))
            
            # Prepara exceptions (expandindo range de datas)
            for exc in cal.get("exceptions", []):
                from_date_str = exc.get("from_date")
                to_date_str = exc.get("to_date") or from_date_str
                is_working = exc.get("working", False)
                times = exc.get("times", [])
                
                if not from_date_str:
                    continue
                
                # Pega o primeiro horário de trabalho da exceção (se houver)
                start_time = None
                end_time = None
                if times and is_working:
                    first_time = times[0]
                    start_time = first_time.get("start_time")
                    end_time = first_time.get("end_time")
                
                # Expande range de datas (from_date até to_date)
                try:
                    from_date = datetime.strptime(from_date_str[:10], "%Y-%m-%d").date()
                    to_date = datetime.strptime(to_date_str[:10], "%Y-%m-%d").date()
                    
                    current_date = from_date
                    while current_date <= to_date:
                        exception_rows.append((
                            calendar_id,
                            current_date.isoformat(),
                            is_working,
                            start_time,
                            end_time,
                            self.created_by,
                        ))
                        current_date += timedelta(days=1)
                except (ValueError, TypeError):
                    # Fallback: só insere from_date
                    exception_rows.append((
                        calendar_id,
                        from_date_str,
                        is_working,
                        start_time,
                        end_time,
                        self.created_by,
                    ))
        
        # Delete em massa de dados antigos (weekdays, working_times, exceptions)
        if calendar_ids_for_delete:
            cur.execute(
                """
                DELETE FROM pm.calendar_weekday
                WHERE calendar_id = ANY(%s) AND deleted_at IS NULL
                """,
                (calendar_ids_for_delete,),
            )
            cur.execute(
                """
                DELETE FROM pm.calendar_working_time
                WHERE calendar_id = ANY(%s) AND deleted_at IS NULL
                """,
                (calendar_ids_for_delete,),
            )
            cur.execute(
                """
                DELETE FROM pm.calendar_exception
                WHERE calendar_id = ANY(%s) AND deleted_at IS NULL
                """,
                (calendar_ids_for_delete,),
            )
        
        # Bulk insert de weekdays
        if weekday_rows:
            cur.executemany(
                """
                INSERT INTO pm.calendar_weekday (
                    calendar_id, day_of_week, working, created_by
                ) VALUES (
                    %s, %s, %s, %s
                )
                """,
                weekday_rows,
            )
        
        # Bulk insert de working_times
        if working_time_rows:
            cur.executemany(
                """
                INSERT INTO pm.calendar_working_time (
                    calendar_id, day_of_week, start_time, end_time, created_by
                ) VALUES (
                    %s, %s, %s, %s, %s
                )
                """,
                working_time_rows,
            )
        
        # Bulk insert de exceptions
        if exception_rows:
            cur.executemany(
                """
                INSERT INTO pm.calendar_exception (
                    calendar_id, exception_date, working, start_time, end_time, created_by
                ) VALUES (
                    %s, %s, %s, %s, %s, %s
                )
                """,
                exception_rows,
            )

        return len(external_to_db_id)

    def _import_resources(
        self,
        cur,
        masterplan_id: int,
        resources: List[Dict[str, Any]],
    ) -> Tuple[int, Dict[str, int]]:
        """Importa recursos do projeto usando bulk insert (otimizado).
        
        Returns:
            Tuple com:
            - Número de recursos importados/atualizados
            - Mapa de external_id -> resource_id (do banco)
        """
        if not resources:
            return 0, {}

        # Prepara todas as linhas em memória
        rows: List[Tuple[Any, ...]] = []
        valid_external_ids: List[str] = []
        
        for res in resources:
            external_id = res.get("external_id")
            name = res.get("name")
            
            if not name or not external_id:
                continue
            
            rows.append((
                masterplan_id,
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
            ))
            valid_external_ids.append(external_id)
        
        if not rows:
            return 0, {}
        
        # Bulk insert com executemany
        chunk_size = 5000
        for i in range(0, len(rows), chunk_size):
            chunk = rows[i:i + chunk_size]
            cur.executemany(
                """
                INSERT INTO pm.resource (
                    masterplan_id, external_id, name, email, type, "group",
                    max_units, standard_rate, cost, notes, custom_fields, created_by
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
                ON CONFLICT (masterplan_id, external_id)
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
                """,
                chunk,
            )
        
        # Busca todos os IDs com um único SELECT
        cur.execute(
            """
            SELECT id, external_id FROM pm.resource
            WHERE masterplan_id = %s AND external_id = ANY(%s) AND deleted_at IS NULL
            """,
            (masterplan_id, valid_external_ids),
        )
        
        external_to_db_id: Dict[str, int] = {}
        for row in cur.fetchall():
            resource_id, external_id = row
            if external_id:
                external_to_db_id[external_id] = resource_id

        # Marca como deletados os resources que não estão mais no arquivo
        if valid_external_ids:
            cur.execute(
                """
                UPDATE pm.resource
                SET deleted_at = CURRENT_TIMESTAMP,
                    deleted_by = %s,
                    updated_at = CURRENT_TIMESTAMP
                WHERE masterplan_id = %s
                    AND deleted_at IS NULL
                    AND external_id IS NOT NULL
                    AND external_id != ALL(%s)
                """,
                (self.created_by, masterplan_id, valid_external_ids),
            )
            deleted_count = cur.rowcount
            if deleted_count > 0:
                # Restaura resources que foram deletados mas voltaram no arquivo
                cur.execute(
                    """
                    UPDATE pm.resource
                    SET deleted_at = NULL,
                        deleted_by = NULL,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE masterplan_id = %s
                        AND deleted_at IS NOT NULL
                        AND external_id = ANY(%s)
                    """,
                    (masterplan_id, valid_external_ids),
                )

        return len(external_to_db_id), external_to_db_id

    def _import_tasks(
        self,
        cur,
        masterplan_id: int,
        tasks: List[Dict[str, Any]],
    ) -> Tuple[int, Dict[str, int]]:
        """Importa tarefas do projeto usando bulk insert (otimizado).
        
        Returns:
            Tuple com:
            - Número de tarefas importadas/atualizadas
            - Mapa de external_id -> task_id (do banco)
        """
        if not tasks:
            return 0, {}

        # Prepara todas as linhas em memória
        rows: List[Tuple[Any, ...]] = []
        valid_external_ids: List[str] = []
        
        for task in tasks:
            external_id = task.get("external_id")
            name = task.get("name")
            
            if not name or not external_id:
                continue
            
            rows.append((
                masterplan_id,
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
            ))
            valid_external_ids.append(external_id)
        
        if not rows:
            return 0, {}
        
        # Bulk insert com executemany (chunking para evitar SQL muito grande)
        chunk_size = 5000
        for i in range(0, len(rows), chunk_size):
            chunk = rows[i:i + chunk_size]
            cur.executemany(
                """
                INSERT INTO pm.task (
                    masterplan_id, external_id, name, start_date, finish_date,
                    duration, work, percent_complete, priority, notes, wbs,
                    outline_level, milestone, summary, custom_fields, created_by
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
                ON CONFLICT (masterplan_id, external_id)
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
                """,
                chunk,
            )
        
        # Busca todos os IDs com um único SELECT
        cur.execute(
            """
            SELECT id, external_id FROM pm.task
            WHERE masterplan_id = %s AND external_id = ANY(%s) AND deleted_at IS NULL
            """,
            (masterplan_id, valid_external_ids),
        )
        
        external_to_db_id: Dict[str, int] = {}
        for row in cur.fetchall():
            task_id, external_id = row
            if external_id:
                external_to_db_id[external_id] = task_id

        # Marca como deletadas as tasks que não estão mais no arquivo
        if valid_external_ids:
            cur.execute(
                """
                UPDATE pm.task
                SET deleted_at = CURRENT_TIMESTAMP,
                    deleted_by = %s,
                    updated_at = CURRENT_TIMESTAMP
                WHERE masterplan_id = %s
                    AND deleted_at IS NULL
                    AND external_id IS NOT NULL
                    AND external_id != ALL(%s)
                """,
                (self.created_by, masterplan_id, valid_external_ids),
            )
            deleted_count = cur.rowcount
            if deleted_count > 0:
                # Restaura tasks que foram deletadas mas voltaram no arquivo
                cur.execute(
                    """
                    UPDATE pm.task
                    SET deleted_at = NULL,
                        deleted_by = NULL,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE masterplan_id = %s
                        AND deleted_at IS NOT NULL
                        AND external_id = ANY(%s)
                    """,
                    (masterplan_id, valid_external_ids),
                )

        return len(external_to_db_id), external_to_db_id

    def _import_assignments(
        self,
        cur,
        masterplan_id: int,
        assignments: List[Dict[str, Any]],
        task_id_map: Dict[str, int],
        resource_id_map: Dict[str, int],
    ) -> int:
        """Importa assignments usando bulk insert (otimizado).
        
        Args:
            cur: Cursor do banco
            masterplan_id: ID do projeto
            assignments: Lista de assignments extraídos do .mpp
            task_id_map: Mapa de external_id -> task_id (do banco)
            resource_id_map: Mapa de external_id -> resource_id (do banco)
        
        Returns:
            Número de assignments importados/atualizados
        """
        if not assignments:
            return 0

        # Prepara todas as linhas em memória
        rows: List[Tuple[Any, ...]] = []
        valid_external_ids: List[str] = []
        
        for assignment in assignments:
            external_id = assignment.get("external_id")
            task_external_id = assignment.get("task_external_id")
            resource_external_id = assignment.get("resource_external_id")
            
            task_id = task_id_map.get(task_external_id) if task_external_id else None
            resource_id = resource_id_map.get(resource_external_id) if resource_external_id else None
            
            if not task_id or not resource_id or not external_id:
                continue
            
            rows.append((
                masterplan_id,
                external_id,
                task_id,
                resource_id,
                assignment.get("work"),
                assignment.get("cost"),
                parse_iso_datetime(assignment.get("start")),
                parse_iso_datetime(assignment.get("finish")),
                assignment.get("units"),
                assignment.get("percent_complete", 0),
                json.dumps(assignment.get("custom_fields", {})),
                self.created_by,
            ))
            valid_external_ids.append(external_id)
        
        if not rows:
            # Se não há assignments no arquivo, marca todos como deletados
            cur.execute(
                """
                UPDATE pm.assignment
                SET deleted_at = CURRENT_TIMESTAMP,
                    deleted_by = %s,
                    updated_at = CURRENT_TIMESTAMP
                WHERE masterplan_id = %s
                    AND deleted_at IS NULL
                """,
                (self.created_by, masterplan_id),
            )
            return 0
        
        # Bulk insert com executemany
        chunk_size = 5000
        for i in range(0, len(rows), chunk_size):
            chunk = rows[i:i + chunk_size]
            cur.executemany(
                """
                INSERT INTO pm.assignment (
                    masterplan_id, external_id, task_id, resource_id,
                    work, cost, start_date, finish_date, units,
                    percent_complete, custom_fields, created_by
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
                ON CONFLICT (masterplan_id, external_id)
                WHERE deleted_at IS NULL AND external_id IS NOT NULL
                DO UPDATE SET
                    task_id = EXCLUDED.task_id,
                    resource_id = EXCLUDED.resource_id,
                    work = EXCLUDED.work,
                    cost = EXCLUDED.cost,
                    start_date = EXCLUDED.start_date,
                    finish_date = EXCLUDED.finish_date,
                    units = EXCLUDED.units,
                    percent_complete = EXCLUDED.percent_complete,
                    custom_fields = EXCLUDED.custom_fields,
                    updated_by = EXCLUDED.created_by,
                    updated_at = CURRENT_TIMESTAMP
                """,
                chunk,
            )
        
        # Marca como deletados os assignments que não estão mais no arquivo
        if valid_external_ids:
            cur.execute(
                """
                UPDATE pm.assignment
                SET deleted_at = CURRENT_TIMESTAMP,
                    deleted_by = %s,
                    updated_at = CURRENT_TIMESTAMP
                WHERE masterplan_id = %s
                    AND deleted_at IS NULL
                    AND external_id IS NOT NULL
                    AND external_id != ALL(%s)
                """,
                (self.created_by, masterplan_id, valid_external_ids),
            )
            # Restaura assignments que foram deletados mas voltaram no arquivo
            cur.execute(
                """
                UPDATE pm.assignment
                SET deleted_at = NULL,
                    deleted_by = NULL,
                    updated_at = CURRENT_TIMESTAMP
                WHERE masterplan_id = %s
                    AND deleted_at IS NOT NULL
                    AND external_id = ANY(%s)
                """,
                (masterplan_id, valid_external_ids),
            )

        return len(rows)

    def _import_dependencies(
        self,
        cur,
        masterplan_id: int,
        dependencies: List[Dict[str, Any]],
        task_id_map: Dict[str, int],
    ) -> int:
        """Importa dependências usando bulk insert (otimizado).
        
        Args:
            cur: Cursor do banco
            masterplan_id: ID do projeto
            dependencies: Lista de dependências extraídas do .mpp
            task_id_map: Mapa de external_id -> task_id (do banco)
        
        Returns:
            Número de dependências importadas/atualizadas
        """
        if not dependencies:
            return 0

        # Prepara todas as linhas em memória
        rows: List[Tuple[Any, ...]] = []
        dependency_pairs: List[Tuple[int, int]] = []  # Lista de (predecessor_id, successor_id)
        
        for dep in dependencies:
            predecessor_external_id = dep.get("predecessor_external_id")
            successor_external_id = dep.get("successor_external_id")
            
            predecessor_task_id = task_id_map.get(predecessor_external_id) if predecessor_external_id else None
            successor_task_id = task_id_map.get(successor_external_id) if successor_external_id else None
            
            if not predecessor_task_id or not successor_task_id:
                continue
            
            # Evita dependências circulares
            if predecessor_task_id == successor_task_id:
                continue
            
            rows.append((
                masterplan_id,
                predecessor_task_id,
                successor_task_id,
                dep.get("type"),
                dep.get("lag"),
                self.created_by,
            ))
            dependency_pairs.append((predecessor_task_id, successor_task_id))
        
        if not rows:
            # Se não há dependencies no arquivo, marca todas como deletadas
            cur.execute(
                """
                UPDATE pm.task_dependency
                SET deleted_at = CURRENT_TIMESTAMP,
                    deleted_by = %s,
                    updated_at = CURRENT_TIMESTAMP
                WHERE masterplan_id = %s
                    AND deleted_at IS NULL
                """,
                (self.created_by, masterplan_id),
            )
            return 0
        
        # Bulk insert com executemany
        chunk_size = 5000
        for i in range(0, len(rows), chunk_size):
            chunk = rows[i:i + chunk_size]
            cur.executemany(
                """
                INSERT INTO pm.task_dependency (
                    masterplan_id, predecessor_task_id, successor_task_id,
                    dependency_type, lag, created_by
                ) VALUES (
                    %s, %s, %s, %s, %s, %s
                )
                ON CONFLICT (predecessor_task_id, successor_task_id)
                WHERE deleted_at IS NULL
                DO UPDATE SET
                    dependency_type = EXCLUDED.dependency_type,
                    lag = EXCLUDED.lag,
                    updated_by = EXCLUDED.created_by,
                    updated_at = CURRENT_TIMESTAMP
                """,
                chunk,
            )
        
        # Marca como deletadas as dependencies que não estão mais no arquivo
        if dependency_pairs:
            # Constrói uma lista de condições para comparar os pares
            # Usa uma abordagem mais simples: marca todas e depois restaura as que estão na lista
            cur.execute(
                """
                UPDATE pm.task_dependency
                SET deleted_at = CURRENT_TIMESTAMP,
                    deleted_by = %s,
                    updated_at = CURRENT_TIMESTAMP
                WHERE masterplan_id = %s
                    AND deleted_at IS NULL
                    AND (predecessor_task_id, successor_task_id) != ALL(%s)
                """,
                (self.created_by, masterplan_id, dependency_pairs),
            )
            # Restaura dependencies que foram deletadas mas voltaram no arquivo
            cur.execute(
                """
                UPDATE pm.task_dependency
                SET deleted_at = NULL,
                    deleted_by = NULL,
                    updated_at = CURRENT_TIMESTAMP
                WHERE masterplan_id = %s
                    AND deleted_at IS NOT NULL
                    AND (predecessor_task_id, successor_task_id) = ANY(%s)
                """,
                (masterplan_id, dependency_pairs),
            )

        return len(rows)

    def _import_baselines(
        self,
        cur,
        masterplan_id: int,
        baselines_meta: List[Dict[str, Any]],
    ) -> Dict[str, int]:
        """Importa linhas de base (baselines) do projeto.
        
        Args:
            cur: Cursor do banco
            masterplan_id: ID do projeto
            baselines_meta: Lista de metadados de baseline (index, external_id, name)
        
        Returns:
            Mapa de external_id -> baseline_id (do banco)
        """
        if not baselines_meta:
            return {}

        # Prepara linhas para bulk insert
        baseline_rows: List[Tuple[Any, ...]] = []
        valid_external_ids: List[str] = []
        
        for baseline_meta in baselines_meta:
            external_id = baseline_meta.get("external_id")
            name = baseline_meta.get("name")
            
            if not external_id or not name:
                continue
            
            baseline_rows.append((
                masterplan_id,
                external_id,
                name,
                self.created_by,
            ))
            valid_external_ids.append(external_id)
        
        if not baseline_rows:
            return {}
        
        # Bulk insert de baselines
        cur.executemany(
            """
            INSERT INTO pm.baseline (
                masterplan_id, external_id, name, created_by
            ) VALUES (
                %s, %s, %s, %s
            )
            ON CONFLICT (masterplan_id, external_id)
            WHERE deleted_at IS NULL AND external_id IS NOT NULL
            DO UPDATE SET
                name = EXCLUDED.name,
                updated_by = EXCLUDED.created_by,
                updated_at = CURRENT_TIMESTAMP
            """,
            baseline_rows,
        )
        
        # Busca todos os IDs com um único SELECT
        cur.execute(
            """
            SELECT id, external_id FROM pm.baseline
            WHERE masterplan_id = %s AND external_id = ANY(%s) AND deleted_at IS NULL
            """,
            (masterplan_id, valid_external_ids),
        )
        
        external_to_db_id: Dict[str, int] = {}
        for row in cur.fetchall():
            baseline_id, external_id = row
            if external_id:
                external_to_db_id[external_id] = baseline_id

        return external_to_db_id

    def _import_task_baselines(
        self,
        cur,
        baseline_id_map: Dict[str, int],
        task_id_map: Dict[str, int],
        task_baselines: List[Dict[str, Any]],
    ) -> int:
        """Importa valores de baseline para tasks.
        
        Args:
            cur: Cursor do banco
            baseline_id_map: Mapa de external_id -> baseline_id
            task_id_map: Mapa de external_id -> task_id
            task_baselines: Lista de task baselines extraídos
        
        Returns:
            Número de task baselines importados/atualizados
        """
        if not task_baselines or not baseline_id_map:
            return 0

        # Otimização: delete em massa + bulk insert (muito mais rápido que milhares de UPSERTs)
        baseline_ids = list({bid for bid in baseline_id_map.values() if bid is not None})
        if not baseline_ids:
            return 0

        # Remove tudo das baselines deste import (hard delete)
        cur.execute(
            """
            DELETE FROM pm.task_baseline
            WHERE baseline_id = ANY(%s)
            """,
            (baseline_ids,),
        )

        rows: list[tuple[Any, ...]] = []
        for tb in task_baselines:
            task_external_id = tb.get("task_external_id")
            baseline_index = tb.get("baseline_index")
            baseline_external_id = str(baseline_index) if baseline_index is not None else None

            task_id = task_id_map.get(task_external_id) if task_external_id else None
            baseline_id = baseline_id_map.get(baseline_external_id) if baseline_external_id else None

            if not task_id or not baseline_id:
                continue

            rows.append(
                (
                    baseline_id,
                    task_id,
                    parse_iso_datetime(tb.get("start_date")),
                    parse_iso_datetime(tb.get("finish_date")),
                    tb.get("duration"),
                    tb.get("work"),
                    tb.get("cost"),
                    self.created_by,
                )
            )

        if not rows:
            return 0

        # Bulk insert com chunking
        chunk_size = 5000
        for i in range(0, len(rows), chunk_size):
            chunk = rows[i:i + chunk_size]
            cur.executemany(
                """
                INSERT INTO pm.task_baseline (
                    baseline_id, task_id, start_date, finish_date,
                    duration, work, cost, created_by
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s
                )
                """,
                chunk,
            )

        return len(rows)

    def _import_resource_baselines(
        self,
        cur,
        baseline_id_map: Dict[str, int],
        resource_id_map: Dict[str, int],
        resource_baselines: List[Dict[str, Any]],
    ) -> int:
        """Importa valores de baseline para resources.
        
        Args:
            cur: Cursor do banco
            baseline_id_map: Mapa de external_id -> baseline_id
            resource_id_map: Mapa de external_id -> resource_id
            resource_baselines: Lista de resource baselines extraídos
        
        Returns:
            Número de resource baselines importados/atualizados
        """
        if not resource_baselines or not baseline_id_map:
            return 0

        baseline_ids = list({bid for bid in baseline_id_map.values() if bid is not None})
        if not baseline_ids:
            return 0

        # Remove tudo das baselines deste import (hard delete)
        cur.execute(
            """
            DELETE FROM pm.resource_baseline
            WHERE baseline_id = ANY(%s)
            """,
            (baseline_ids,),
        )

        rows: list[tuple[Any, ...]] = []
        for rb in resource_baselines:
            resource_external_id = rb.get("resource_external_id")
            baseline_index = rb.get("baseline_index")
            baseline_external_id = str(baseline_index) if baseline_index is not None else None

            resource_id = resource_id_map.get(resource_external_id) if resource_external_id else None
            baseline_id = baseline_id_map.get(baseline_external_id) if baseline_external_id else None

            if not resource_id or not baseline_id:
                continue

            rows.append(
                (
                    baseline_id,
                    resource_id,
                    rb.get("work"),
                    rb.get("cost"),
                    self.created_by,
                )
            )

        if not rows:
            return 0

        # Bulk insert com chunking
        chunk_size = 5000
        for i in range(0, len(rows), chunk_size):
            chunk = rows[i:i + chunk_size]
            cur.executemany(
                """
                INSERT INTO pm.resource_baseline (
                    baseline_id, resource_id, work, cost, created_by
                ) VALUES (
                    %s, %s, %s, %s, %s
                )
                """,
                chunk,
            )

        return len(rows)

    def _import_assignment_timephased(
        self,
        cur,
        masterplan_id: int,
        timephased_data: List[Dict[str, Any]],
    ) -> Tuple[int, int, int]:
        """Importa dados timephased (planned e complete) de assignments.
        
        Args:
            cur: Cursor do banco
            masterplan_id: ID do projeto
            timephased_data: Lista de timephased data extraída do .mpp
        
        Returns:
            Tuple com:
            - Número de linhas planned importadas
            - Número de linhas complete importadas
            - Número de assignments com dados timephased
        """
        if not timephased_data:
            return 0, 0, 0

        # Constrói mapa de assignment_external_id -> assignment_id
        # Busca todos os assignments do projeto
        cur.execute(
            """
            SELECT id, external_id FROM pm.assignment
            WHERE masterplan_id = %s AND deleted_at IS NULL
            """,
            (masterplan_id,),
        )
        assignment_map: Dict[str, int] = {}
        for row in cur.fetchall():
            assignment_id, external_id = row
            if external_id:
                assignment_map[external_id] = assignment_id

        # Coleta assignment_ids que têm dados timephased
        assignment_ids_to_process: List[int] = []
        planned_rows_data: List[Tuple[Any, ...]] = []
        complete_rows_data: List[Tuple[Any, ...]] = []
        
        for td in timephased_data:
            assignment_external_id = td.get("assignment_external_id")
            assignment_id = assignment_map.get(assignment_external_id) if assignment_external_id else None
            
            if not assignment_id:
                continue
            
            planned_periods = td.get("planned", [])
            complete_periods = td.get("complete", [])
            
            if not planned_periods and not complete_periods:
                continue
            
            assignment_ids_to_process.append(assignment_id)
            
            # Prepara linhas planned
            for period in planned_periods:
                planned_rows_data.append((
                    assignment_id,
                    parse_iso_datetime(period.get("period_start")),
                    parse_iso_datetime(period.get("period_end")),
                    period.get("work"),
                    period.get("cost"),
                    period.get("units"),
                    self.created_by,
                ))
            
            # Prepara linhas complete
            for period in complete_periods:
                complete_rows_data.append((
                    assignment_id,
                    parse_iso_datetime(period.get("period_start")),
                    parse_iso_datetime(period.get("period_end")),
                    period.get("work"),
                    period.get("cost"),
                    period.get("units"),
                    self.created_by,
                ))
        
        if not assignment_ids_to_process:
            return 0, 0, 0
        
        # Delete físico em massa dos dados antigos
        cur.execute(
            """
            DELETE FROM pm.assignment_timephased_planned
            WHERE assignment_id = ANY(%s) AND deleted_at IS NULL
            """,
            (assignment_ids_to_process,),
        )
        
        cur.execute(
            """
            DELETE FROM pm.assignment_timephased_complete
            WHERE assignment_id = ANY(%s) AND deleted_at IS NULL
            """,
            (assignment_ids_to_process,),
        )
        
        # Bulk insert planned com chunking
        chunk_size = 10000
        for i in range(0, len(planned_rows_data), chunk_size):
            chunk = planned_rows_data[i:i + chunk_size]
            cur.executemany(
                """
                INSERT INTO pm.assignment_timephased_planned (
                    assignment_id, period_start, period_end,
                    work, cost, units, created_by
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s
                )
                """,
                chunk,
            )
        
        # Bulk insert complete com chunking
        for i in range(0, len(complete_rows_data), chunk_size):
            chunk = complete_rows_data[i:i + chunk_size]
            cur.executemany(
                """
                INSERT INTO pm.assignment_timephased_complete (
                    assignment_id, period_start, period_end,
                    work, cost, units, created_by
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s
                )
                """,
                chunk,
            )

        return len(planned_rows_data), len(complete_rows_data), len(assignment_ids_to_process)
