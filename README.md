# FastAPI AI Starter

## Sobre o projeto

API base em Python/FastAPI para aplicacoes futuras de IA, com autenticacao, banco de dados, Docker, testes automatizados e documentacao Swagger/OpenAPI.

O projeto usa uma arquitetura em camadas para separar responsabilidades:

```text
routes -> services -> repositories -> SQLAlchemy -> PostgreSQL
```

As tabelas sao versionadas com Alembic migrations.

## Tecnologias

- Python
- FastAPI
- Pydantic
- SQLAlchemy
- Alembic
- PostgreSQL
- JWT
- Docker
- Pytest

## Funcionalidades

- Cadastro de usuario
- Login com JWT
- Rotas protegidas
- CRUD de documentos
- Documentos vinculados ao usuario autenticado
- Paginacao em listagem de documentos
- Health check da API
- Health check do banco
- Testes automatizados
- Swagger/OpenAPI

## Como rodar

Suba a API e o PostgreSQL com Docker Compose:

```powershell
docker compose up --build
```

O container da API executa automaticamente:

```powershell
alembic upgrade head
```

antes de iniciar o Uvicorn.

Este projeto expoe a API em `8001` no computador local porque a porta `8000` estava ocupada no ambiente de desenvolvimento.

```text
Host local:        http://localhost:8001
Porta no container: 8000
```

Para rodar os testes:

```powershell
pytest
```

Os testes usam SQLite em memoria para nao depender do Docker/PostgreSQL durante a execucao.

## Documentação

Swagger/OpenAPI:

```text
http://localhost:8001/docs
```

Observacao: muitos tutoriais usam `http://localhost:8000/docs`. Aqui usamos `8001` no host local para evitar conflito de porta.

Fluxo esperado no Swagger:

1. `POST /auth/register`
2. `POST /auth/login`
3. Clique em `Authorize`
4. Informe email e senha
5. `POST /documents`
6. `GET /documents`

Endpoints principais:

```text
GET  /health
GET  /health/db

POST /auth/register
POST /auth/login
GET  /auth/me

POST   /documents
GET    /documents
GET    /documents/{id}
DELETE /documents/{id}
```

`GET /documents` aceita paginacao:

```text
GET /documents?limit=20&offset=0
```

## Configuração

Copie `.env.example` para `.env` se quiser customizar a execucao local:

```text
APP_DATABASE_URL=postgresql+psycopg://fastapi_user:fastapi_password@localhost:5432/fastapi_ai_starter
APP_JWT_SECRET_KEY=replace-this-with-a-long-random-secret-key
APP_ACCESS_TOKEN_EXPIRE_MINUTES=30
```

`APP_JWT_SECRET_KEY` e obrigatoria. Em projeto real, use uma chave longa e nao commite o valor real.

## Migrations

Criar uma nova migration depois de alterar models:

```powershell
alembic revision -m "describe change"
```

Aplicar migrations pendentes:

```powershell
alembic upgrade head
```

Voltar uma migration:

```powershell
alembic downgrade -1
```
