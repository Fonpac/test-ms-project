#!/usr/bin/env python3
"""Teste local: importa um arquivo .mpp do disco lendo variáveis do .env.

Uso:
  python scripts/test_import_local.py example.mpp

Requer:
- variáveis de banco (DATABASE_URL ou PG*)
- schema pm aplicado no Postgres

Obs: se `python-dotenv` estiver instalado, ele carrega automaticamente o `.env`.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Quando executado como arquivo (python scripts/xxx.py), o Python não inclui a raiz do repo no sys.path.
REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover
    def load_dotenv(*args, **kwargs):  # type: ignore[no-redef]
        return False

from mpxj_pm.db import DBConfig
from mpxj_pm.importer import MPPImporter


def main() -> int:
    if len(sys.argv) < 2:
        print("Uso: python scripts/test_import_local.py <arquivo.mpp>")
        return 2

    try:
        load_dotenv(override=False)
    except PermissionError:
        # Em alguns ambientes (ex: sandbox/CI) arquivos .env podem ser bloqueados.
        pass


    mpp_file = sys.argv[1]
    created_by = int(__import__("os").getenv("CREATED_BY", "1"))

    importer = MPPImporter(DBConfig(), created_by=created_by)
    result = importer.import_project(mpp_file)

    print("Import concluído:")
    for k, v in result.items():
        print(f"- {k}: {v}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
