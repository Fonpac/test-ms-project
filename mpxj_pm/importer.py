from __future__ import annotations

import os
from typing import Any, Dict, Optional

from .db import DBConfig, coerce_float, coerce_int, parse_iso_datetime
from .mpp import MPPReader


def _list_pm_overloads(cur, proname: str) -> list[str]:
    """Lista assinaturas existentes no schema pm para ajudar debug."""
    try:
        cur.execute(
            """
            SELECT oid::regprocedure::text
            FROM pg_proc
            WHERE pronamespace = 'pm'::regnamespace
              AND proname = %s
            ORDER BY 1
            """,
            (proname,),
        )
        return [r[0] for r in cur.fetchall()]
    except Exception:
        return []


def _try_call_fetchone(cur, sql_variants: list[str], params: tuple[Any, ...], proname: str):
    last_exc: Exception | None = None

    for sql in sql_variants:
        try:
            cur.execute(sql, params)
            return cur.fetchone()[0]
        except Exception as e:
            last_exc = e
            # tenta próxima variante apenas para UndefinedFunction; outros erros devem subir
            try:
                from psycopg import errors as pg_errors

                if not isinstance(e, pg_errors.UndefinedFunction):
                    raise
            except Exception:
                # se psycopg errors não disponível ou não é UndefinedFunction, re-raise
                raise

    overloads = _list_pm_overloads(cur, proname)
    msg = [
        f"Não foi possível chamar pm.{proname} com nenhuma assinatura esperada.",
        "- Confirme que você aplicou o pm.sql no MESMO banco/DB usado pela aplicação.",
    ]
    if overloads:
        msg.append("Assinaturas encontradas no banco:")
        msg.extend([f"  - {o}" for o in overloads])
    else:
        msg.append("Nenhuma assinatura encontrada em pg_proc para esse nome no schema pm.")

    raise SystemExit("\n".join(msg)) from last_exc


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
        tasks = reader.get_tasks()
        resources = reader.get_resources()
        assignments = reader.get_assignments()
        dependencies = reader.get_dependencies()
        calendars = reader.get_calendars()

        project_name = info.get("name") or os.path.basename(mpp_path)
        source_file = source_file or os.path.basename(mpp_path)

        print(project_name, source_file)
        print(info)

        inserted_task_ids: Dict[str, int] = {}
        inserted_resource_ids: Dict[str, int] = {}
        inserted_calendar_ids: Dict[str, int] = {}

        with self._connect() as conn:
            with conn.cursor() as cur:
                with conn.transaction():
                    project_id = _try_call_fetchone(
                        cur,
                        [
                            # assinatura conforme pm.sql (timestamp sem TZ)
                            "SELECT pm.upsert_project(%s::varchar,%s::timestamp,%s::timestamp,%s::varchar,%s::varchar,%s::text,%s::timestamp,%s::timestamp,%s::int4)",
                            # fallback se o banco estiver usando timestamptz
                            "SELECT pm.upsert_project(%s::varchar,%s::timestamptz,%s::timestamptz,%s::varchar,%s::varchar,%s::text,%s::timestamptz,%s::timestamptz,%s::int4)",
                            # fallback mais permissivo (text)
                            "SELECT pm.upsert_project(%s::text,%s::timestamptz,%s::timestamptz,%s::text,%s::text,%s::text,%s::timestamptz,%s::timestamptz,%s::int4)",
                        ],
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
                        proname="upsert_project",
                    )

                    cur.execute(
                        "SELECT pm.create_import_batch(%s::int4,%s::varchar,%s::varchar,%s::int4)",
                        (project_id, source_file, "completed", self.created_by),
                    )
                    
                    import_batch_id = cur.fetchone()[0]

                    # calendários (2-pass para parent)
                    pending = list(calendars)
                    safety = 0

                    conn.commit()
                    # while pending and safety < 10:
                    #     safety += 1
                    #     next_pending = []
                    #     progressed = False
                    #     for cal in pending:
                    #         ext_id = cal.get("id")
                    #         name = cal.get("name")
                    #         if not ext_id or not name:
                    #             continue

                    #         parent_ext_id = cal.get("parent_id")
                    #         parent_db_id = (
                    #             inserted_calendar_ids.get(str(parent_ext_id)) if parent_ext_id else None
                    #         )
                    #         if parent_ext_id and parent_db_id is None:
                    #             next_pending.append(cal)
                    #             continue

                    #         cur.execute(
                    #             "SELECT pm.insert_calendar(%s::int4,%s::int4,%s::varchar,%s::varchar,%s::int4,%s::int4)",
                    #             (
                    #                 project_id,
                    #                 import_batch_id,
                    #                 str(ext_id),
                    #                 name,
                    #                 parent_db_id,
                    #                 self.created_by,
                    #             ),
                    #         )
                    #         inserted_calendar_ids[str(ext_id)] = cur.fetchone()[0]
                    #         progressed = True

                    #     if not progressed:
                    #         for cal in next_pending:
                    #             ext_id = cal.get("id")
                    #             name = cal.get("name")
                    #             if not ext_id or not name:
                    #                 continue
                    #             cur.execute(
                    #                 "SELECT pm.insert_calendar(%s::int4,%s::int4,%s::varchar,%s::varchar,%s::int4,%s::int4)",
                    #                 (
                    #                     project_id,
                    #                     import_batch_id,
                    #                     str(ext_id),
                    #                     name,
                    #                     None,
                    #                     self.created_by,
                    #                 ),
                    #             )
                    #             inserted_calendar_ids[str(ext_id)] = cur.fetchone()[0]
                    #         next_pending = []

                    #     pending = next_pending

                    # tasks_imported = 0
                    # for t in tasks:
                    #     ext_id = t.get("id")
                    #     name = t.get("name") or (f"Task {ext_id}" if ext_id else "Task")

                    #     cur.execute(
                    #         "SELECT pm.insert_task(%s::int4,%s::int4,%s::varchar,%s::varchar,%s::timestamp,%s::timestamp,%s::numeric,%s::numeric,%s::int4,%s::int4,%s::text,%s::varchar,%s::int4,%s::bool,%s::bool,%s::int4)",
                    #         (
                    #             project_id,
                    #             import_batch_id,
                    #             str(ext_id) if ext_id is not None else None,
                    #             name,
                    #             parse_iso_datetime(t.get("start")),
                    #             parse_iso_datetime(t.get("finish")),
                    #             coerce_float(t.get("duration")),
                    #             coerce_float(t.get("work")),
                    #             coerce_int(t.get("percent_complete")) or 0,
                    #             coerce_int(t.get("priority")),
                    #             t.get("notes"),
                    #             t.get("wbs"),
                    #             coerce_int(t.get("outline_level")) or 0,
                    #             bool(t.get("milestone")) if t.get("milestone") is not None else False,
                    #             bool(t.get("summary")) if t.get("summary") is not None else False,
                    #             self.created_by,
                    #         ),
                    #     )
                    #     task_id = cur.fetchone()[0]
                    #     if ext_id is not None:
                    #         inserted_task_ids[str(ext_id)] = task_id
                    #     tasks_imported += 1

                    # resources_imported = 0
                    # for r in resources:
                    #     ext_id = r.get("id")
                    #     name = r.get("name") or (f"Resource {ext_id}" if ext_id else "Resource")

                    #     cur.execute(
                    #         "SELECT pm.insert_resource(%s::int4,%s::int4,%s::varchar,%s::varchar,%s::varchar,%s::varchar,%s::varchar,%s::numeric,%s::numeric,%s::numeric,%s::text,%s::int4)",
                    #         (
                    #             project_id,
                    #             import_batch_id,
                    #             str(ext_id) if ext_id is not None else None,
                    #             name,
                    #             r.get("email"),
                    #             r.get("type"),
                    #             r.get("group"),
                    #             coerce_float(r.get("max_units")),
                    #             coerce_float(r.get("standard_rate")),
                    #             coerce_float(r.get("cost")),
                    #             r.get("notes"),
                    #             self.created_by,
                    #         ),
                    #     )
                    #     resource_id = cur.fetchone()[0]
                    #     if ext_id is not None:
                    #         inserted_resource_ids[str(ext_id)] = resource_id
                    #     resources_imported += 1

                    # assignments_imported = 0
                    # for a in assignments:
                    #     t_ext = a.get("task_id")
                    #     r_ext = a.get("resource_id")
                    #     if t_ext is None or r_ext is None:
                    #         continue

                    #     t_db = inserted_task_ids.get(str(t_ext))
                    #     r_db = inserted_resource_ids.get(str(r_ext))

                    #     if t_db is None:
                    #         cur.execute(
                    #             "SELECT pm.get_task_id_by_external_id(%s::int4,%s::varchar,%s::int4)",
                    #             (project_id, str(t_ext), import_batch_id),
                    #         )
                    #         row = cur.fetchone()
                    #         t_db = row[0] if row else None

                    #     if r_db is None:
                    #         cur.execute(
                    #             "SELECT pm.get_resource_id_by_external_id(%s::int4,%s::varchar,%s::int4)",
                    #             (project_id, str(r_ext), import_batch_id),
                    #         )
                    #         row = cur.fetchone()
                    #         r_db = row[0] if row else None

                    #     if t_db is None or r_db is None:
                    #         continue

                    #     cur.execute(
                    #         "SELECT pm.insert_assignment(%s::int4,%s::int4,%s::int4,%s::int4,%s::numeric,%s::numeric,%s::timestamp,%s::timestamp,%s::numeric,%s::int4,%s::int4)",
                    #         (
                    #             project_id,
                    #             import_batch_id,
                    #             t_db,
                    #             r_db,
                    #             coerce_float(a.get("work")),
                    #             coerce_float(a.get("cost")),
                    #             parse_iso_datetime(a.get("start")),
                    #             parse_iso_datetime(a.get("finish")),
                    #             coerce_float(a.get("units")),
                    #             coerce_int(a.get("percent_complete")) or 0,
                    #             self.created_by,
                    #         ),
                    #     )
                    #     _ = cur.fetchone()[0]
                    #     assignments_imported += 1

                    # dependencies_imported = 0
                    # for d in dependencies:
                    #     pred_ext = d.get("predecessor_id")
                    #     succ_ext = d.get("successor_id")
                    #     if pred_ext is None or succ_ext is None:
                    #         continue

                    #     pred_db = inserted_task_ids.get(str(pred_ext))
                    #     succ_db = inserted_task_ids.get(str(succ_ext))

                    #     if pred_db is None:
                    #         cur.execute(
                    #             "SELECT pm.get_task_id_by_external_id(%s::int4,%s::varchar,%s::int4)",
                    #             (project_id, str(pred_ext), import_batch_id),
                    #         )
                    #         row = cur.fetchone()
                    #         pred_db = row[0] if row else None

                    #     if succ_db is None:
                    #         cur.execute(
                    #             "SELECT pm.get_task_id_by_external_id(%s::int4,%s::varchar,%s::int4)",
                    #             (project_id, str(succ_ext), import_batch_id),
                    #         )
                    #         row = cur.fetchone()
                    #         succ_db = row[0] if row else None

                    #     if pred_db is None or succ_db is None:
                    #         continue

                    #     cur.execute(
                    #         "SELECT pm.insert_task_dependency(%s::int4,%s::int4,%s::int4,%s::int4,%s::varchar,%s::numeric,%s::int4)",
                    #         (
                    #             project_id,
                    #             import_batch_id,
                    #             pred_db,
                    #             succ_db,
                    #             d.get("type"),
                    #             coerce_float(d.get("lag")),
                    #             self.created_by,
                    #         ),
                    #     )
                    #     _ = cur.fetchone()[0]
                    #     dependencies_imported += 1

        return {
            "project_id": project_id,
            "import_batch_id": import_batch_id,
            "tasks_imported": tasks_imported,
            "resources_imported": resources_imported,
            "assignments_imported": assignments_imported,
            "dependencies_imported": dependencies_imported,
            "calendars_imported": len(inserted_calendar_ids),
        }
