#!/usr/bin/env python3
"""API FastAPI para upload de arquivos .mpp e importação."""

from __future__ import annotations

import hashlib
import os
from dataclasses import dataclass
from datetime import datetime

import jwt
from fastapi import Depends, FastAPI, File, HTTPException, UploadFile
from fastapi.responses import JSONResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

try:
    from dotenv import load_dotenv
    load_dotenv(override=False)
except (ImportError, PermissionError):
    pass

from mpxj_pm.db import DBConfig
from mpxj_pm.importer import MPPImporter

# =============================================================================
# Configuração
# =============================================================================

S3_BUCKET = os.getenv("S3_BUCKET")
AWS_REGION = os.getenv("AWS_REGION") or os.getenv("AWS_DEFAULT_REGION")

# JWT Configuration
JWT_SECRET = os.getenv("JWT_SECRET")

app = FastAPI(
    title="MPXJ Importer API",
    description="API para upload e importação de arquivos Microsoft Project (.mpp)",
    version="1.0.0",
)

security = HTTPBearer()


# =============================================================================
# Auth
# =============================================================================

@dataclass
class CurrentUser:
    """Usuário autenticado extraído do JWT."""
    user_id: int
    payload: dict  # Payload completo do JWT


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> CurrentUser:
    """Extrai e valida o usuário do token JWT."""
    if not JWT_SECRET:
        raise HTTPException(
            status_code=500,
            detail="JWT_SECRET não configurado no servidor",
        )
    
    token = credentials.credentials
    
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expirado")
    except jwt.InvalidTokenError as e:
        raise HTTPException(status_code=401, detail=f"Token inválido: {e}")
    
    # Extrai o user_id do campo "sub"
    user_id_value = payload.get("sub")
    if user_id_value is None:
        raise HTTPException(
            status_code=401,
            detail="Campo 'sub' não encontrado no token",
        )
    
    try:
        user_id = int(user_id_value)
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=401,
            detail="Campo 'sub' deve ser um número inteiro",
        )
    
    return CurrentUser(user_id=user_id, payload=payload)


# =============================================================================
# Helpers
# =============================================================================

def _get_s3_client():
    import boto3
    return boto3.client("s3", region_name=AWS_REGION)


# =============================================================================
# Health Check Endpoints
# =============================================================================

@app.get("/health")
async def health_check():
    """Health check completo - verifica todos os serviços."""
    checks = {
        "api": {"status": "healthy"},
        "database": {"status": "unknown"},
        "s3": {"status": "unknown"},
    }
    overall_healthy = True
    
    # Verifica banco de dados
    try:
        import psycopg
        db_cfg = DBConfig()
        with psycopg.connect(db_cfg.to_dsn(), connect_timeout=5) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
        checks["database"]["status"] = "healthy"
    except Exception as e:
        checks["database"]["status"] = "unhealthy"
        checks["database"]["error"] = str(e)
        overall_healthy = False
    
    # Verifica S3
    if S3_BUCKET:
        try:
            s3 = _get_s3_client()
            s3.head_bucket(Bucket=S3_BUCKET)
            checks["s3"]["status"] = "healthy"
            checks["s3"]["bucket"] = S3_BUCKET
        except Exception as e:
            checks["s3"]["status"] = "unhealthy"
            checks["s3"]["error"] = str(e)
            overall_healthy = False
    else:
        checks["s3"]["status"] = "not_configured"
    
    return {
        "status": "healthy" if overall_healthy else "unhealthy",
        "timestamp": datetime.utcnow().isoformat(),
        "checks": checks,
    }


@app.get("/health/live")
async def liveness_probe():
    """Liveness probe - verifica se a API está rodando."""
    return {"status": "alive", "timestamp": datetime.utcnow().isoformat()}


@app.get("/health/ready")
async def readiness_probe():
    """Readiness probe - verifica se a API está pronta para receber requests."""
    errors = []
    
    # Verifica banco de dados
    try:
        import psycopg
        db_cfg = DBConfig()
        with psycopg.connect(db_cfg.to_dsn(), connect_timeout=5) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
    except Exception as e:
        errors.append(f"database: {e}")
    
    # Verifica S3
    if S3_BUCKET:
        try:
            s3 = _get_s3_client()
            s3.head_bucket(Bucket=S3_BUCKET)
        except Exception as e:
            errors.append(f"s3: {e}")
    else:
        errors.append("s3: S3_BUCKET not configured")
    
    if errors:
        return JSONResponse(
            status_code=503,
            content={
                "status": "not_ready",
                "timestamp": datetime.utcnow().isoformat(),
                "errors": errors,
            }
        )
    
    return {"status": "ready", "timestamp": datetime.utcnow().isoformat()}


# =============================================================================
# Upload/Import Endpoints
# =============================================================================


@app.post("/upload")
async def upload_mpp(
    file: UploadFile = File(..., description="Arquivo .mpp para upload"),
    current_user: CurrentUser = Depends(get_current_user),
):
    """
    Upload de arquivo .mpp, importação e salvamento no S3.
    
    Requer autenticação via Bearer token JWT.
    
    Fluxo:
    1. Valida e calcula hash do arquivo
    2. Importa o arquivo no banco de dados
    3. Salva o arquivo no S3 em `imports/{masterplan_id}/{arquivo}`
    4. Atualiza o import_log com o path do S3 e hash
    
    - **file**: Arquivo .mpp (obrigatório)
    
    Retorna:
    - masterplan_id: ID do masterplan criado
    - s3_uri: URI do arquivo no S3
    - file_hash: Hash SHA256 do arquivo
    - import_log_id: ID do log de importação
    """
    import tempfile
    
    # Validações
    if not file.filename:
        raise HTTPException(status_code=400, detail="Nome do arquivo não fornecido")
    
    if not file.filename.lower().endswith(".mpp"):
        raise HTTPException(status_code=400, detail="Apenas arquivos .mpp são aceitos")
    
    if not S3_BUCKET:
        raise HTTPException(status_code=500, detail="S3_BUCKET não configurado")
    
    # Lê o conteúdo do arquivo
    try:
        content = await file.read()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erro ao ler arquivo: {e}")
    
    if len(content) == 0:
        raise HTTPException(status_code=400, detail="Arquivo vazio")
    
    # Calcula hash SHA256 do arquivo
    file_hash = hashlib.sha256(content).hexdigest()
    
    # Gera S3 key antecipadamente (usando hash como prefixo temporário)
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    safe_name = "".join(c if c.isalnum() or c in ".-_" else "_" for c in file.filename)
    
    # Salva temporariamente para processar
    fd, tmp_path = tempfile.mkstemp(suffix=".mpp")
    try:
        os.write(fd, content)
        os.close(fd)
        
        # Importa no banco de dados (sem o s3_uri ainda)
        db_cfg = DBConfig()
        importer = MPPImporter(db_cfg, created_by=current_user.user_id)
        result = importer.import_project(
            tmp_path,
            source_file=file.filename,
            file_hash=file_hash,
        )
        
        if not result.success:
            raise HTTPException(
                status_code=500,
                detail=f"Erro na importação: {result.error_message}",
            )
        
        masterplan_id = result.masterplan_id
        import_log_id = result.import_log_id
        
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
    
    # Salva no S3 com o path imports/{masterplan_id}/{filename}
    s3_key = f"imports/{masterplan_id}/{timestamp}_{safe_name}"
    s3_uri = f"s3://{S3_BUCKET}/{s3_key}"
    
    try:
        s3 = _get_s3_client()
        s3.put_object(
            Bucket=S3_BUCKET,
            Key=s3_key,
            Body=content,
            ContentType="application/vnd.ms-project",
            Metadata={
                "original-filename": file.filename,
                "masterplan-id": str(masterplan_id),
                "import-log-id": str(import_log_id),
                "file-hash": file_hash,
                "uploaded-at": datetime.utcnow().isoformat(),
            },
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao salvar no S3: {e}")
    
    # Atualiza o import_log com o path do S3
    try:
        import psycopg
        with psycopg.connect(db_cfg.to_dsn()) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE pm.import_log
                    SET file_storage_path = %s
                    WHERE id = %s
                    """,
                    (s3_uri, import_log_id),
                )
                conn.commit()
    except Exception as e:
        # Não falha o request se não conseguir atualizar, mas loga
        print(f"Aviso: Erro ao atualizar import_log com S3 path: {e}")
    
    return {
        "success": True,
        "masterplan_id": masterplan_id,
        "masterplan_name": result.masterplan_name,
        "masterplan_action": result.masterplan_action,
        "import_log_id": import_log_id,
        "s3_uri": s3_uri,
        "s3_bucket": S3_BUCKET,
        "s3_key": s3_key,
        "file_hash": file_hash,
        "filename": file.filename,
        "size_bytes": len(content),
        "tasks": result.tasks,
        "resources": result.resources,
        "assignments": result.assignments,
        "calendars": result.calendars,
        "dependencies": result.dependencies,
        "total_time_seconds": result.total_time_seconds(),
    }






# =============================================================================
# Main
# =============================================================================

if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8000"))
    
    uvicorn.run(app, host=host, port=port)
