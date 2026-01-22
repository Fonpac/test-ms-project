#!/usr/bin/env python3
"""Teste local: importa arquivos .mpp do disco lendo variáveis do .env.

Uso:
  python scripts/test_import_local.py              # Importa todos os .mpp do repo
  python scripts/test_import_local.py example.mpp  # Importa arquivo específico

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


def find_mpp_files(repo_root: Path) -> list[Path]:
    """Encontra todos os arquivos .mpp no repositório."""
    mpp_files = []
    for mpp_file in repo_root.rglob("*.mpp"):
        if mpp_file.is_file():
            mpp_files.append(mpp_file)
    return sorted(mpp_files)


def main() -> int:
    try:
        load_dotenv(override=False)
    except PermissionError:
        # Em alguns ambientes (ex: sandbox/CI) arquivos .env podem ser bloqueados.
        pass

    created_by = int(__import__("os").getenv("CREATED_BY", "1"))
    importer = MPPImporter(DBConfig(), created_by=created_by)

    if len(sys.argv) >= 2:
        mpp_file = Path(sys.argv[1])
        if not mpp_file.exists():
            print(f"Erro: Arquivo não encontrado: {mpp_file}")
            return 1
        mpp_files = [mpp_file]
    else:
        mpp_files = find_mpp_files(REPO_ROOT)
        if not mpp_files:
            print("Nenhum arquivo .mpp encontrado no repositório.")
            return 0
        print(f"Encontrados {len(mpp_files)} arquivo(s) .mpp:")
        for mpp_file in mpp_files:
            print(f"  - {mpp_file}")

    print("\nIniciando importação...\n")
    
    results = []
    for i, mpp_file in enumerate(mpp_files, 1):
        print(f"[{i}/{len(mpp_files)}] Importando: {mpp_file.name}")
        try:
            result = importer.import_project(str(mpp_file))
            results.append((mpp_file.name, result, None))
            print(f"  ✓ Concluído: project_id={result.get('project_id')}, import_batch_id={result.get('import_batch_id')}")
        except Exception as e:
            results.append((mpp_file.name, None, str(e)))
            print(f"  ✗ Erro: {e}")
        print()

    print("\n" + "="*60)
    print("Resumo da importação:")
    print("="*60)
    for name, result, error in results:
        if error:
            print(f"✗ {name}: ERRO - {error}")
        else:
            print(f"✓ {name}: project_id={result.get('project_id')}, import_batch_id={result.get('import_batch_id')}")

    failed = sum(1 for _, _, error in results if error)
    if failed > 0:
        print(f"\n⚠ {failed} arquivo(s) falharam na importação.")
        return 1

    print(f"\n✓ Todos os {len(results)} arquivo(s) foram importados com sucesso!")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
