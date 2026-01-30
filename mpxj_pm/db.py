from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Optional


def parse_iso_datetime(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except Exception:
        return None


def coerce_int(value: Any) -> Optional[int]:
    if value is None:
        return None
    try:
        return int(value)
    except Exception:
        return None


def coerce_float(value: Any) -> Optional[float]:
    if value is None:
        return None
    try:
        return float(value)
    except Exception:
        return None


@dataclass
class DBConfig:
    """Config de conexão com Postgres (variáveis separadas).

    Fonte padrão:
    - PGHOST, PGPORT, PGDATABASE, PGUSER, PGPASSWORD
    - POSTGRES_TLS_CERT (opcional): caminho para certificado TLS/SSL

    Você também pode sobrescrever via atributos do DBConfig.
    """

    host: Optional[str] = None
    port: Optional[int] = None
    database: Optional[str] = None
    user: Optional[str] = None
    password: Optional[str] = None
    ssl_cert: Optional[str] = None

    def to_dsn(self) -> str:
        host = self.host or os.getenv("PGHOST") or "localhost"
        port = self.port or coerce_int(os.getenv("PGPORT")) or 5432
        dbname = self.database or os.getenv("PGDATABASE")
        user = self.user or os.getenv("PGUSER")
        password = self.password or os.getenv("PGPASSWORD")
        ssl_cert = self.ssl_cert or os.getenv("POSTGRES_TLS_CERT")

        missing = [k for k, v in {"PGDATABASE": dbname, "PGUSER": user}.items() if not v]
        if missing:
            raise SystemExit(
                "Configuração de banco incompleta. Defina PGDATABASE e PGUSER (e opcionalmente PGHOST/PGPORT/PGPASSWORD)."
            )

        parts = [f"host={host}", f"port={port}", f"dbname={dbname}", f"user={user}"]
        if password:
            parts.append(f"password={password}")
        
        # Configuração SSL/TLS se certificado fornecido
        if ssl_cert:
            parts.append("sslmode=require")
            parts.append(f"sslrootcert={ssl_cert}")
        
        return " ".join(parts)
