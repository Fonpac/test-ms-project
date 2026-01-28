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

import os
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
from mpxj_pm.importer import MPPImporter, ImportReport


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

    created_by = int(os.getenv("CREATED_BY", "1"))
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
    
    reports: list[ImportReport] = []
    for i, mpp_file in enumerate(mpp_files, 1):
        print(f"[{i}/{len(mpp_files)}] Importando: {mpp_file.name}")
        try:
            report = importer.import_project(
                str(mpp_file),
            )
            reports.append(report)
        except Exception as e:
            print(f"  Erro fatal: {e}")
            # Cria um report de erro
            error_report = ImportReport(
                source_file=mpp_file.name,
                success=False,
                error_message=str(e),
            )
            reports.append(error_report)
        print()

    # Resumo final
    print("\n" + "=" * 70)
    print("RESUMO DA IMPORTAÇÃO")
    print("=" * 70)
    
    success_count = 0
    for report in reports:
        status = "OK" if report.success else "ERRO"
        time_str = f"{report.total_time_seconds():.2f}s" if report.timings_ms else "N/A"
        
        if report.success:
            print(f"[{status}] {report.source_file}")
            print(f"       Masterplan: {report.masterplan_name} (ID: {report.masterplan_id})")
            print(f"       Ação: {report.masterplan_action} | Tempo: {time_str}")
            print(f"       Custom Fields: {report.custom_field_definitions}")
            success_count += 1
        else:
            print(f"[{status}] {report.source_file}")
            print(f"       Erro: {report.error_message}")
    
    print("=" * 70)
    print(f"Total: {len(reports)} | Sucesso: {success_count} | Falha: {len(reports) - success_count}")
    print("Relatórios salvos no banco de dados (tabela pm.import_log)")
    print("=" * 70)

    return 0 if success_count == len(reports) else 1


if __name__ == "__main__":
    raise SystemExit(main())
