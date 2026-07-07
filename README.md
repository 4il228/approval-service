# approval-service

Backend-сервис согласования контента. Принимает заявки на согласование перед публикацией и фиксирует итоговое решение.

## Локальный запуск

### Через Docker (рекомендуется)

```bash
docker compose up --build
```

Сервис будет доступен на `http://localhost:8000`.

### Без Docker

1. Установить зависимости:

```bash
pip install -r requirements.txt
```

2. Настроить переменную окружения:

```bash
export DATABASE_URL=sqlite+aiosqlite:///./approval.db
```

3. Запустить миграции:

```bash
alembic upgrade head
```

4. Запустить сервер:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Проверка работоспособности

```bash
curl http://localhost:8000/health
curl http://localhost:8000/ready
```

## Запуск тестов

```bash
pip install -r requirements-dev.txt
pytest
```

## Авторизация (Auth Stub)

Сервис использует заголовок `X-Auth-Mock` для имитации авторизации. Формат — JSON:

```json
{
  "user_id": "usr_123",
  "workspace_id": "ws_1",
  "permissions": ["approval:read", "approval:create", "approval:decide", "approval:cancel"]
}
```

### Доступные действия (permissions)

| Permission | Описание |
|------------|----------|
| `approval:read` | Чтение заявок |
| `approval:create` | Создание заявок |
| `approval:decide` | Approve / Reject |
| `approval:cancel` | Cancel заявки |

### Пример запроса

```bash
curl -X POST http://localhost:8000/api/v1/workspaces/ws_1/approval-requests \
  -H "Content-Type: application/json" \
  -H "X-Auth-Mock: {\"user_id\": \"usr_123\", \"workspace_id\": \"ws_1\", \"permissions\": [\"approval:create\"]}" \
  -d '{
    "source_type": "publication",
    "source_id": "pub_001",
    "title": "Instagram reel draft",
    "description": "Needs final approval",
    "reviewer_user_ids": ["usr_1", "usr_2"]
  }'
```

## API Endpoints

| Метод | Путь | Описание | Требуемое право |
|-------|------|----------|-----------------|
| `GET` | `/health` | Проверка здоровья сервиса | - |
| `GET` | `/ready` | Проверка готовности сервиса | - |
| `POST` | `/api/v1/workspaces/{workspace_id}/approval-requests` | Создание заявки | `approval:create` |
| `GET` | `/api/v1/workspaces/{workspace_id}/approval-requests` | Список заявок | `approval:read` |
| `GET` | `/api/v1/workspaces/{workspace_id}/approval-requests/{request_id}` | Получение заявки | `approval:read` |
| `POST` | `.../{request_id}/approve` | Согласование заявки | `approval:decide` |
| `POST` | `.../{request_id}/reject` | Отклонение заявки | `approval:decide` |
| `POST` | `.../{request_id}/cancel` | Отмена заявки | `approval:cancel` |

## Стек

- Python 3.11 + FastAPI
- SQLite (aiosqlite)
- SQLAlchemy 2.0 + Alembic
- Docker + Docker Compose
- pytest + pytest-asyncio
