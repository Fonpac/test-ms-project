from __future__ import annotations

import os
from typing import Any, Dict, Optional

from .db import DBConfig, parse_iso_datetime
from .mpp import MPPReader


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

    def import_project(self, mpp_path: str, source_file: Optional[str] = None) -> Dict[str, Any]:
        reader = MPPReader(mpp_path)
        reader.read()

        info = reader.get_project_info()

        project_name = info.get("name") or os.path.basename(mpp_path)
        source_file = source_file or os.path.basename(mpp_path)

        print(project_name, source_file)
        print(info)

        with self._connect() as conn:
            with conn.cursor() as cur:
                with conn.transaction():
                    cur.execute(
                        """
                        INSERT INTO pm.project (
                            name, start_date, finish_date, author, company, comments,
                            creation_date, last_saved, created_by
                        ) VALUES (
                            %s, %s, %s, %s, %s, %s, %s, %s, %s
                        ) RETURNING id
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
                        ),
                    )
                    project_id = cur.fetchone()[0]

                    cur.execute(
                        """
                        INSERT INTO pm.import_batch (
                            project_id, source_file, import_status, created_by
                        ) VALUES (
                            %s, %s, %s, %s
                        ) RETURNING id
                        """,
                        (project_id, source_file, "completed", self.created_by),
                    )
                    
                    import_batch_id = cur.fetchone()[0]

        return {
            "project_id": project_id,
            "import_batch_id": import_batch_id,
        }
