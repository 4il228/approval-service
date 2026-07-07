```markdown
# SPEC.md

## 1. Описание сервиса
* [cite_start]**Название:** approval-service[cite: 4].
* [cite_start]**Назначение:** Сервис согласования контента[cite: 4].
* [cite_start]**Основная задача:** Разработать backend-сервис, который принимает заявки на согласование контента перед публикацией и фиксирует итоговое решение[cite: 5].

## 2. Контекст и архитектурные границы
* [cite_start]В продукте уже существуют публикации, сценарии, готовые материалы, пользователи и рабочие пространства[cite: 7].
* [cite_start]Необходимо сделать отдельный сервис исключительно для процесса согласования[cite: 7].
* [cite_start]Все внешние сущности должны передаваться только как идентификаторы[cite: 8].
* [cite_start]Реализовывать соседние сервисы не нужно[cite: 8].
* [cite_start]Frontend, реальные внешние сервисы, секреты, токены, медиафайлы и credentials добавлять не нужно[cite: 68].

## 3. Основные сценарии
Сервис должен реализовывать следующие сценарии:
* [cite_start]Создать заявку на согласование[cite: 10].
* [cite_start]Получить список заявок в workspace[cite: 11].
* [cite_start]Получить одну заявку[cite: 12].
* [cite_start]Согласовать, отклонить или отменить заявку[cite: 13].

## 4. Модели данных (Payloads)
### 4.1. Создание заявки
Поля при создании заявки:
* [cite_start]`sourceType`: Допустимые значения — `publication`, `scenario`, `edit` или `external`[cite: 22].
* [cite_start]`sourceId`: Внешний идентификатор контента[cite: 18, 22].
* [cite_start]`title`: Строковое название (пример: `"Instagram reel draft"`)[cite: 19].
* [cite_start]`description`: Строковое описание (пример: `"Needs final approval"`)[cite: 20].
* [cite_start]`reviewerUserIds`: Массив внешних идентификаторов пользователей (пример: `["usr_1", "usr_2"]`)[cite: 21, 22].

### 4.2. Решения
* [cite_start]**Approve:** Требует передачи комментария (пример: `{ "comment": "Approved" }`)[cite: 24].
* [cite_start]**Reject:** Требует передачи причины (пример: `{ "reason": "Brand tone is wrong" }`)[cite: 25].
* [cite_start]**Cancel:** Требует передачи причины (пример: `{ "reason": "Draft was removed" }`)[cite: 26, 27].

## 5. Минимальный HTTP API
Системные эндпоинты:
* [cite_start]`GET /health`[cite: 29].
* [cite_start]`GET /ready`[cite: 30].

Эндпоинты бизнес-логики:
* [cite_start]`POST /api/v1/workspaces/{workspace_id}/approval-requests`[cite: 31].
* [cite_start]`GET /api/v1/workspaces/{workspace_id}/approval-requests`[cite: 32].
* [cite_start]`GET /api/v1/workspaces/{workspace_id}/approval-requests/{request_id}`[cite: 33].
* [cite_start]`POST /api/v1/workspaces/{workspace_id}/approval-requests/{request_id}/approve`[cite: 34].
* [cite_start]`POST /api/v1/workspaces/{workspace_id}/approval-requests/{request_id}/reject`[cite: 34].
* [cite_start]`POST /api/v1/workspaces/{workspace_id}/approval-requests/{request_id}/cancel`[cite: 34].

## 6. Ограничения (Constraints)
* [cite_start]Данные одного workspace не должны быть доступны из другого workspace[cite: 36].
* [cite_start]Повтор одного и того же клиентского запроса не должен создавать дубли[cite: 37].
* [cite_start]После финального решения заявка не должна переходить в другое финальное состояние[cite: 38].
* [cite_start]Каждое успешное изменение должно оставлять след, по которому понятно, кто и что изменил[cite: 39].
* [cite_start]Сервис должен быть готов к последующей интеграции с другими сервисами через события[cite: 40].
* [cite_start]В публичные ответы, логи и события не должны попадать секреты, токены, email, storage keys, signed URLs, provider URLs или сырые provider payloads[cite: 41].

## 7. Авторизация (Auth)
* [cite_start]Для локального запуска достаточно использовать auth-заглушку[cite: 43].
* [cite_start]Формат auth-заглушки выбирается самостоятельно и должен быть описан в `README`[cite: 43].
* [cite_start]Запрос должен содержать: `workspace`, пользователя и список действий[cite: 43].

**Доступные действия:**
* [cite_start]`approval:read` — требуется для чтения заявок[cite: 46, 48].
* [cite_start]`approval:create` — требуется для создания заявки[cite: 49, 50].
* [cite_start]`approval:decide` — требуется для действий approve/reject[cite: 51, 52].
* [cite_start]`approval:cancel` — требуется для действия cancel[cite: 53, 54].

## 8. Технические требования
* [cite_start]**Язык и фреймворк:** Предпочтительно Python + FastAPI (допустим другой backend stack, если его легко запустить локально)[cite: 56].
* [cite_start]**База данных:** PostgreSQL или SQLite для локального запуска[cite: 57].
* [cite_start]**Миграции:** Обязательно наличие миграций базы данных[cite: 58].
* [cite_start]**Инфраструктура:** Обязательно наличие `Dockerfile` и `docker-compose.yml`[cite: 59].
* [cite_start]**Тестирование:** Обязательно наличие автоматических тестов[cite: 60].
* [cite_start]**Документация запуска:** Наличие `README` с командами запуска и тестов[cite: 61].

## 9. Состав поставки (Что приложить)
* [cite_start]Решение должно быть выложено в Git-репозиторий, ссылка прикрепляется в Google Form[cite: 63].
* [cite_start]Исходный код сервиса[cite: 64].
* [cite_start]Миграции и тесты[cite: 65].
* [cite_start]`README.md`[cite: 66].
* [cite_start]Короткий `DESIGN.md`, включающий: модель данных, границы сервиса, обработку повторов, события/интеграции, известные компромиссы[cite: 67].

```