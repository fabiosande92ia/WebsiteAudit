# Website Audit API

Uma API REST profissional construída com Python 3.12, FastAPI e SQLite para realizar auditorias automáticas a websites utilizando o Lighthouse e verificações básicas de segurança.

## Requisitos

- Python 3.12+
- Node.js e npm (para instalação global do lighthouse)
- Docker e Docker Compose (opcional)

## Instalação Local

1. Instalar dependências Python:
```bash
pip install -r requirements.txt
```

2. Instalar Lighthouse globalmente via npm:
```bash
npm install -g lighthouse
```

## Executar a aplicação

Para iniciar a API em ambiente de desenvolvimento (com reload automático):

```bash
uvicorn app.main:app --reload
```

A API ficará disponível em `http://127.0.0.1:8000`.
A documentação interativa Swagger/OpenAPI está disponível em `http://127.0.0.1:8000/docs`.

## Utilizando com Docker

Pode correr todo o projeto via Docker:

```bash
docker-compose up --build
```

## Decisões Arquiteturais

- **FastAPI**: Escolhido pela sua velocidade, validação automática com Pydantic e geração automática de documentação (Swagger).
- **SQLite + SQLAlchemy**: Utilizado para armazenamento inicial leve e flexível das auditorias e resultados. Facilita o setup local sem depender de bases de dados externas.
- **Background Tasks**: O processo de auditoria (Lighthouse + Segurança) é demorado e não deve bloquear o request do utilizador. Por isso, a API retorna um `202 Accepted` de imediato e processa a auditoria em background.
- **Estrutura de Pastas**: A aplicação foi modularizada em `api`, `services`, `models`, e `schemas` seguindo os princípios de separação de responsabilidades (SoC), tornando o código testável, mantível e escalável.

## Exemplos de chamadas (cURL)

### 1. Verificar estado da API (Health Check)
```bash
curl -X GET "http://127.0.0.1:8000/health"
```

### 2. Iniciar uma auditoria
Retorna de imediato com estado `pending`.
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/audits" \
     -H "Content-Type: application/json" \
     -d '{"url": "https://example.com"}'
```

### 3. Consultar o estado/resultado de uma auditoria específica
Substituir o `1` pelo ID retornado na criação. O `status` atualizará para `completed` ou `failed`.
```bash
curl -X GET "http://127.0.0.1:8000/api/v1/audits/1"
```

### 4. Listar todas as auditorias
```bash
curl -X GET "http://127.0.0.1:8000/api/v1/audits"
```

## Testes

Para correr os testes unitários (utilizando `pytest`):

```bash
pytest
```
