## Importador MPP → PostgreSQL (pm)

Este projeto roda em **ECS** consumindo mensagens de uma **fila SQS** e importando arquivos **Microsoft Project (.mpp)** para Postgres usando o schema/funções de `pm.sql`.

### Requisitos

- **Java** (necessário para MPXJ/JPype)
- **Python** + dependências (`requirements.txt`)
- **PostgreSQL** com `pm.sql` aplicado

### Setup rápido (local)

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Variáveis via `.env`

- Copie `.env.example` para `.env` e ajuste.
- Local/dev: o código carrega `.env` automaticamente (se existir).
- ECS: normalmente você injeta variáveis via Task Definition/Secrets; o `.env` é só para testes.

### Importar um arquivo local (teste)

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# edite PGHOST/PGPORT/PGDATABASE/PGUSER/PGPASSWORD
python scripts/test_import_local.py example.mpp
```
### ECS + SQS Worker

O entrypoint para ECS é `worker.py`:

- Faz long-poll no SQS
- Importa no Postgres
- Apaga a mensagem **apenas** se importar com sucesso
- Se falhar, não apaga (para retry / DLQ)

Rodar local (simulando ECS):

```bash
cp .env.example .env
# edite PGHOST/PGPORT/PGDATABASE/PGUSER/PGPASSWORD, AWS_REGION e SQS_QUEUE_URL
python worker.py
```

### Payload da mensagem (JSON)

- Arquivo local:

```json
{ "mpp_path": "/data/projetos/exemplo.mpp" }
```

- Arquivo no S3:

```json
{ "s3_bucket": "meu-bucket", "s3_key": "imports/exemplo.mpp" }
```

ou

```json
{ "s3_uri": "s3://meu-bucket/imports/exemplo.mpp" }
```

### Banco

- Rode `pm.sql` no Postgres para criar o schema/tabelas/funções.


## Docker

Build:

```bash
docker build -t mpp-importer:latest .
```

Run local (com `.env`):

```bash
docker run --rm --env-file .env mpp-importer:latest
```

No ECS:
- Use o `CMD` padrão (`python worker.py`) ou configure o Command/Entrypoint no Task Definition.
- Passe `PGHOST`, `PGPORT`, `PGDATABASE`, `PGUSER`, `PGPASSWORD`, `AWS_REGION`, `SQS_QUEUE_URL` via env/secrets.
