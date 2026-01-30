# Coleção Postman - MPP Importer API

Este diretório contém a coleção Postman para testar a API MPP Importer.

## Arquivos

- `MPP_Importer.postman_collection.json` - Coleção com todos os endpoints da API
- `MPP_Importer.postman_environment.json` - Ambiente com variáveis de configuração

## Como importar no Postman

1. Abra o Postman
2. Clique em **Import** (canto superior esquerdo)
3. Selecione os dois arquivos:
   - `MPP_Importer.postman_collection.json`
   - `MPP_Importer.postman_environment.json`
4. Clique em **Import**

## Configuração

### Variáveis de Ambiente

Após importar, configure as variáveis no ambiente **MPP Importer - Local**:

| Variável | Descrição | Exemplo |
|----------|-----------|---------|
| `base_url` | URL base da API | `http://localhost:8000` |
| `jwt_token` | Token JWT para autenticação | `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...` |

### Como obter um Token JWT

O token JWT deve ser gerado por seu sistema de autenticação. O token deve conter:

```json
{
  "id": 3,  // user_id (número inteiro)
  "name": "João",
  "email": "joao@constructin.com.br",
  "iat": 1769777373,  // timestamp de criação
  "exp": 1769780973  // timestamp de expiração
}
```

**Exemplo de geração de token (Python):**

```python
import jwt
import datetime

JWT_SECRET = "seu-secret-aqui"
user_id = 3
name = "João"
email = "joao@constructin.com.br"
now = datetime.datetime.utcnow()
exp = now + datetime.timedelta(hours=1)

token = jwt.encode(
    {
        "id": user_id,
        "name": name,
        "email": email,
        "iat": int(now.timestamp()),
        "exp": int(exp.timestamp())
    },
    JWT_SECRET,
    algorithm="HS256"
)

print(token)
```

## Endpoints Disponíveis

### Health Checks (sem autenticação)

1. **Health Check Completo** - `GET /health`
   - Verifica status da API, banco de dados e S3

2. **Liveness Probe** - `GET /health/live`
   - Verifica se a API está rodando

3. **Readiness Probe** - `GET /health/ready`
   - Verifica se a API está pronta (DB + S3 disponíveis)

### Upload (requer autenticação)

1. **Upload Arquivo MPP** - `POST /upload`
   - Faz upload de arquivo .mpp
   - Requer: Bearer token JWT no header Authorization
   - Body: form-data com campo `file` contendo o arquivo .mpp

## Como usar

1. **Selecione o ambiente**: No canto superior direito, selecione **MPP Importer - Local**

2. **Configure o token JWT**:
   - Abra o ambiente **MPP Importer - Local**
   - Cole seu token JWT na variável `jwt_token`
   - Salve o ambiente

3. **Teste os endpoints**:
   - **Health Checks**: Podem ser testados sem autenticação
   - **Upload**: 
     - Selecione a requisição "Upload Arquivo MPP"
     - Clique em "Body" → "form-data"
     - No campo "file", selecione "File" e escolha um arquivo .mpp
     - Clique em "Send"

## Exemplos de Resposta

### Upload bem-sucedido

```json
{
  "success": true,
  "masterplan_id": 1,
  "masterplan_name": "Meu Masterplan",
  "masterplan_action": "created",
  "import_log_id": 42,
  "s3_uri": "s3://meu-bucket/imports/1/20260130_120000_projeto.mpp",
  "s3_bucket": "meu-bucket",
  "s3_key": "imports/1/20260130_120000_projeto.mpp",
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

### Erros comuns

- **400 Bad Request**: Arquivo não fornecido ou não é .mpp
- **401 Unauthorized**: Token inválido ou expirado
- **500 Internal Server Error**: Erro na importação ou ao salvar no S3

## Dicas

- Use o ambiente para alternar entre diferentes ambientes (local, dev, prod)
- Os tokens JWT expiram - atualize o token quando necessário
- A coleção inclui exemplos de respostas para facilitar o entendimento
- Você pode adicionar testes automatizados nas abas "Tests" de cada requisição