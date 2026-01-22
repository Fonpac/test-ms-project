from __future__ import annotations

import json
import os
import signal
import sys
import tempfile
import time
from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover
    def load_dotenv(*args, **kwargs):  # type: ignore[no-redef]
        return False


from .db import DBConfig
from .importer import MPPImporter


@dataclass
class WorkerConfig:
    aws_region: str
    queue_url: str
    wait_time_seconds: int = 20
    max_number_of_messages: int = 1
    visibility_timeout: int = 300
    created_by: int = 1


def _env_int(name: str, default: int) -> int:
    v = os.getenv(name)
    if v is None or v == "":
        return default
    return int(v)


def load_worker_config() -> WorkerConfig:
    # carrega .env se existir (útil em dev/local). No ECS, normalmente virá via env vars.
    try:
        load_dotenv(override=False)
    except PermissionError:
        # Alguns ambientes bloqueiam acesso a arquivos .env.
        pass

    region = os.getenv("AWS_REGION") or os.getenv("AWS_DEFAULT_REGION")
    queue_url = os.getenv("SQS_QUEUE_URL")
    if not region:
        raise SystemExit("AWS_REGION (ou AWS_DEFAULT_REGION) não definido")
    if not queue_url:
        raise SystemExit("SQS_QUEUE_URL não definido")

    return WorkerConfig(
        aws_region=region,
        queue_url=queue_url,
        wait_time_seconds=_env_int("SQS_WAIT_TIME_SECONDS", 20),
        max_number_of_messages=_env_int("SQS_MAX_NUMBER_OF_MESSAGES", 1),
        visibility_timeout=_env_int("SQS_VISIBILITY_TIMEOUT", 300),
        created_by=_env_int("CREATED_BY", 1),
    )


def _parse_message(body: str) -> Dict[str, Any]:
    """Aceita JSON no body.

    Formatos suportados:
    - {"mpp_path": "/path/local/file.mpp"}
    - {"s3_bucket": "bucket", "s3_key": "path/file.mpp"}
    - {"s3_uri": "s3://bucket/path/file.mpp"}
    """
    try:
        data = json.loads(body)
    except Exception as e:
        raise ValueError(f"Body não é JSON válido: {e}")

    if not isinstance(data, dict):
        raise ValueError("Body JSON deve ser um objeto")

    return data


def _parse_s3_uri(uri: str) -> Tuple[str, str]:
    if not uri.startswith("s3://"):
        raise ValueError("s3_uri deve começar com s3://")
    rest = uri[len("s3://") :]
    parts = rest.split("/", 1)
    if len(parts) != 2 or not parts[0] or not parts[1]:
        raise ValueError("s3_uri inválida; esperado s3://bucket/key")
    return parts[0], parts[1]


def _resolve_mpp_to_local_path(payload: Dict[str, Any]) -> Tuple[str, Optional[str]]:
    """Retorna (local_path, source_file_name)."""
    if "mpp_path" in payload and payload["mpp_path"]:
        p = str(payload["mpp_path"])
        return p, os.path.basename(p)

    bucket = payload.get("s3_bucket")
    key = payload.get("s3_key")
    s3_uri = payload.get("s3_uri")

    if s3_uri:
        bucket, key = _parse_s3_uri(str(s3_uri))

    if bucket and key:
        try:
            import boto3
        except ImportError as e:
            raise SystemExit("boto3 não instalado. Rode: pip install -r requirements.txt") from e

        s3 = boto3.client("s3", region_name=os.getenv("AWS_REGION") or os.getenv("AWS_DEFAULT_REGION"))
        fd, tmp_path = tempfile.mkstemp(suffix=".mpp")
        os.close(fd)
        s3.download_file(str(bucket), str(key), tmp_path)
        return tmp_path, os.path.basename(str(key))

    raise ValueError("Mensagem precisa conter mpp_path ou (s3_bucket+s3_key) ou s3_uri")


class GracefulShutdown:
    def __init__(self):
        self._stop = False

    @property
    def stop(self) -> bool:
        return self._stop

    def _handler(self, signum, frame):  # noqa: ARG002
        self._stop = True

    def install(self) -> None:
        signal.signal(signal.SIGTERM, self._handler)
        signal.signal(signal.SIGINT, self._handler)


def run_worker() -> int:
    cfg = load_worker_config()

    db_cfg = DBConfig()  # pega DATABASE_URL/.env automaticamente
    importer = MPPImporter(db_cfg, created_by=cfg.created_by)

    try:
        import boto3
    except ImportError as e:
        raise SystemExit("boto3 não instalado. Rode: pip install -r requirements.txt") from e

    sqs = boto3.client("sqs", region_name=cfg.aws_region)

    shutdown = GracefulShutdown()
    shutdown.install()

    print(
        f"SQS worker iniciado | queue={cfg.queue_url} | region={cfg.aws_region} | wait={cfg.wait_time_seconds}s | vis={cfg.visibility_timeout}s"
    )

    while not shutdown.stop:
        resp = sqs.receive_message(
            QueueUrl=cfg.queue_url,
            MaxNumberOfMessages=cfg.max_number_of_messages,
            WaitTimeSeconds=cfg.wait_time_seconds,
            VisibilityTimeout=cfg.visibility_timeout,
        )

        msgs = resp.get("Messages", [])
        if not msgs:
            continue

        for msg in msgs:
            receipt = msg.get("ReceiptHandle")
            body = msg.get("Body") or ""
            tmp_path = None
            try:
                payload = _parse_message(body)
                local_path, source_file = _resolve_mpp_to_local_path(payload)
                tmp_path = local_path if local_path.startswith("/tmp/") else None

                result = importer.import_project(local_path, source_file=source_file)
                print(f"Import OK | {result}")

                if receipt:
                    sqs.delete_message(QueueUrl=cfg.queue_url, ReceiptHandle=receipt)

            except Exception as e:
                # Não apaga a mensagem. Ela vai reaparecer após visibility_timeout e poderá ir para DLQ.
                print(f"Erro ao processar mensagem: {e}", file=sys.stderr)

            finally:
                if tmp_path and os.path.exists(tmp_path):
                    try:
                        os.remove(tmp_path)
                    except Exception:
                        pass

        # evita loop muito apertado quando recebe msg em batch
        time.sleep(0.1)

    print("SQS worker finalizado (shutdown solicitado)")
    return 0
