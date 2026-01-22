from __future__ import annotations

import json
import os
import uuid
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
        project_external_id = info.get("id")
        
        if not project_external_id:
            project_external_id = str(uuid.uuid4())
            print(f"Generated external_id: {project_external_id}")
        
        source_file = source_file or os.path.basename(mpp_path)

        print(f"Project name: {project_name}")
        print(f"Project external_id: {project_external_id}")
        print(f"Source file: {source_file}")
        print(f"Info: {info}")

        with self._connect() as conn:
            with conn.cursor() as cur:
                with conn.transaction():
                    cur.execute(
                        """
                        SELECT id, name, start_date, finish_date, author, company, comments,
                               creation_date, last_saved
                        FROM pm.project
                        WHERE external_id = %s AND deleted_at IS NULL
                        LIMIT 1
                        """,
                        (project_external_id,),
                    )
                    row = cur.fetchone()
                    project_id = row[0] if row else None
                    
                    if project_id:
                        old_values = {
                            "name": row[1],
                            "start_date": row[2].isoformat() if row[2] else None,
                            "finish_date": row[3].isoformat() if row[3] else None,
                            "author": row[4],
                            "company": row[5],
                            "comments": row[6],
                            "creation_date": row[7].isoformat() if row[7] else None,
                            "last_saved": row[8].isoformat() if row[8] else None,
                        }
                        
                        new_values = {
                            "name": project_name,
                            "start_date": parse_iso_datetime(info.get("start_date")),
                            "finish_date": parse_iso_datetime(info.get("finish_date")),
                            "author": info.get("author"),
                            "company": info.get("company"),
                            "comments": info.get("comments"),
                            "creation_date": parse_iso_datetime(info.get("creation_date")),
                            "last_saved": parse_iso_datetime(info.get("last_saved")),
                        }
                        
                        changes = {}
                        for key in old_values.keys():
                            old_val = old_values[key]
                            new_val = new_values[key]
                            if old_val != new_val and (old_val is not None or new_val is not None):
                                changes[key] = {
                                    "old": old_val,
                                    "new": new_val,
                                }
                        
                        cur.execute(
                            """
                            UPDATE pm.project SET
                                name = COALESCE(%s, name),
                                external_id = %s,
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
                                project_external_id,
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
                        
                        history_note = None
                        if changes:
                            history_note = f"Updated: {json.dumps(changes, ensure_ascii=False)}"
                        
                        cur.execute(
                            """
                            INSERT INTO pm.import_batch (
                                project_id, source_file, import_status, created_by
                            ) VALUES (
                                %s, %s, %s, %s
                            ) RETURNING id
                            """,
                            (
                                project_id,
                                f"{source_file} - {history_note}" if history_note else source_file,
                                "completed",
                                self.created_by,
                            ),
                        )
                        import_batch_id = cur.fetchone()[0]
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
