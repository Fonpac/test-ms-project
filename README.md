## Importador MPP → PostgreSQL (pm)

API REST para upload e importação de arquivos **Microsoft Project (.mpp)** para PostgreSQL.

### Requisitos

- **Java** (necessário para MPXJ/JPype)
- **Python** + dependências (`requirements.txt`)
- **PostgreSQL** com `pm.sql` aplicado
- **AWS S3** para armazenamento dos arquivos

### Setup rápido (local)

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Variáveis via `.env`

- Copie `.env.template` para `.env` e ajuste.
- Local/dev: o código carrega `.env` automaticamente (se existir).
- ECS: normalmente você injeta variáveis via Task Definition/Secrets.

**Variáveis obrigatórias:**

| Variável | Descrição |
|----------|-----------|
| `PGHOST` | Host do PostgreSQL |
| `PGPORT` | Porta do PostgreSQL (default: 5432) |
| `PGDATABASE` | Nome do banco de dados |
| `PGUSER` | Usuário do banco |
| `PGPASSWORD` | Senha do banco |
| `AWS_REGION` | Região AWS (ex: us-east-1) |
| `S3_BUCKET` | Bucket S3 para armazenar arquivos .mpp |
| `JWT_SECRET` | Secret para validar tokens JWT |

**Variáveis opcionais:**

| Variável | Default | Descrição |
|----------|---------|-----------|
| `API_HOST` | `0.0.0.0` | Host da API |
| `API_PORT` | `8000` | Porta da API |
| `POSTGRES_TLS_CERT` | - | Caminho para certificado TLS/SSL do PostgreSQL (ex: `./global-bundle.pem`) |

### Importar um arquivo local (teste)

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

cp .env.template .env
# edite PGHOST/PGPORT/PGDATABASE/PGUSER/PGPASSWORD
python scripts/test_import_local.py example.mpp
```

---

## API REST

### Iniciar a API

```bash
cp .env.template .env
# Configure as variáveis (incluindo JWT_SECRET)

python api.py
# ou
uvicorn api:app --host 0.0.0.0 --port 8000
```

### Autenticação

A API requer autenticação via **Bearer token JWT** (algoritmo HS256) em todos os endpoints (exceto health checks).

O token JWT deve conter o `id` do usuário:

```json
{
  "id": 3,
  "name": "João",
  "email": "joao@constructin.com.br",
  "iat": 1769777373,
  "exp": 1769780973
}
```

O `id` extraído do token é usado como `created_by` e `updated_by` nas operações.

### Endpoints

| Método | Endpoint | Auth | Descrição |
|--------|----------|------|-----------|
| GET | `/health` | ❌ | Health check completo (DB + S3) |
| GET | `/health/live` | ❌ | Liveness probe (API rodando) |
| GET | `/health/ready` | ❌ | Readiness probe (DB + S3 disponíveis) |
| POST | `/upload` | ✅ | Upload de arquivo .mpp → S3 + importação |

### Criar Masterplan (Upload)

```bash
curl -X POST "http://localhost:8000/upload" \
  -H "Authorization: Bearer SEU_TOKEN_JWT" \
  -F "file=@projeto.mpp"
```

### Resposta

```json
{
  "success": true,
  "masterplan_id": 1,
  "masterplan_name": "Meu Masterplan",
  "masterplan_action": "created",
  "import_log_id": 42,
  "s3_uri": "s3://meu-bucket/imports/1/20260128_120000_projeto.mpp",
  "s3_bucket": "meu-bucket",
  "s3_key": "imports/1/20260128_120000_projeto.mpp",
  "file_hash": "a1b2c3d4e5f6...",
  "filename": "projeto.mpp",
  "size_bytes": 1234567,
  "tasks": 150,
  "resources": 20,
  "assignments": 300,
  "calendars": 3,
  "dependencies": 100,
  "total_time_seconds": 5.23
}
```

### Armazenamento e Histórico de Versões

O arquivo é salvo no S3 em `imports/{masterplan_id}/{timestamp}_{filename}`.

Cada importação cria um registro na tabela `pm.import_log` contendo:
- `file_storage_path`: URI do arquivo no S3
- `file_hash`: Hash SHA256 do arquivo (para verificar integridade/duplicatas)
- Contagens de entidades importadas (tasks, resources, etc.)
- Timings de cada fase da importação

Quando houver **updates futuros**, novas versões serão salvas no mesmo prefixo do S3 (`imports/{masterplan_id}/`), permitindo manter o histórico completo de todos os arquivos importados para aquele masterplan.

### Documentação interativa

Acesse `http://localhost:8000/docs` para a documentação Swagger/OpenAPI.

---

## Banco de Dados

Rode `pm.sql` no PostgreSQL para criar o schema e tabelas:

```bash
psql -h localhost -U usuario -d banco -f pm.sql
```

---

## Docker

Build:

```bash
docker build -t mpp-importer:latest .
```

Run:

```bash
docker run --rm -p 8000:8000 --env-file .env mpp-importer:latest
```

### No ECS

- Configure: `PGHOST`, `PGPORT`, `PGDATABASE`, `PGUSER`, `PGPASSWORD`, `AWS_REGION`, `S3_BUCKET`
- Exponha a porta 8000 no ALB/Target Group
- Use IAM roles para acesso ao S3
