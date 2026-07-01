# Асинхронный микросервис для эмулирования процессинга платежей

## Оглавление

- [Функционал](#функционал)
- [Технологии](#технологии)
- [Структура проекта](#структура-проекта)
- [Использование проекта](#использование-проекта)
- [Примеры запросов и ответов](#примеры-запросов-и-ответов)

---

## Функционал

### Платежи
 - Создание платежа
 - Получение информации о платеже по UUID
 - Получение уведомления об обработке платежа через webhook
---

## Технологии

- **Backend:** FastAPI
- **База данных:** PostgreSQL, SQLAlchemy, alembic, asyncpg
- **Очереди:** RabbitMQ, FastStream
- **Контейнеризация:** Docker, docker-compose
- **Запуск:** uvicorn
- **Форматтер:** black

---

## Структура проекта

```
migrations/
src/
  api/
  core/
  models/
  repositories/
  schemas/
  services/
  utils/
  consumer.py
  publisher.py
  main.py
.env
.dockerignore
alembic.ini
docker-compose.yml
Dockerfile
README.md
pyproject.toml
```

---

## Использование проекта
### 1. Скачать проект
```bash
git clone https://github.com/koliadav1/payment-processing
```
### 2. Перейти в директорию проекта
```bash
cd <your-path-to-project>/payment-processing-<version>
```
### 3. Создать .env.prod файл с секретными переменными, пример: .env.example файл
### 4. Запустить контейнеры Docker
```bash
docker-compose up --build
```

### 5. Приложение будет доступно по адресу:
- API: http://localhost:8000/
- Документация: http://localhost:8000/docs
- RabbitMQ панель: http://localhost:15672

---

## Примеры запросов и ответов
### Создание платежа
- Запрос
```curl
curl -X 'POST' \
  'http://localhost:8000/api/v1/payments/' \
  -H 'accept: application/json' \
  -H 'Idempotency-Key: <idempotency-key>' \
  -H 'X-API-Key: <X-API-Key>' \
  -H 'Content-Type: application/json' \
  -d '{
  "amount": 10000,
  "currency": "rub",
  "description": "some description",
  "payment_metadata": {
    "additionalProp1": {}
  },
  "webhook_url": "https://webhook_example.com/"
}'
```
- Ответ
```json
{
  "id": "39906226-0064-4253-94ef-76f9a05917c5",
  "status": "pending",
  "created_at": "2026-07-01T12:29:31.997416Z"
}
```
- Ошибка
```json
{
  "detail": [
    {
      "msg": "Wrong X-API-Key, Forbidden",
      "type": "ForbiddenError"
    }
  ]
}
```

### Получение информации о платеже
- Запрос
```curl
curl -X 'GET' \
  'http://localhost:8000/api/v1/payments/<payment-id>' \
  -H 'accept: application/json' \
  -H 'X-API-Key: <X-API-Key>'
```
- Ответ
```json
{
  "id": "ec2b337b-dab6-4b04-9308-2d7d5f3461e9",
  "status": "succeeded",
  "created_at": "2026-07-01T12:36:07.406601Z",
  "amount": "112313.00",
  "currency": "rub",
  "description": "asdasd",
  "payment_metadata": {
    "additionalProp1": {}
  },
  "webhook_url": "https://example.com/",
  "processed_at": "2026-07-01T12:36:12.017203Z"
}
```
- Ошибка
```json
{
  "detail": [
    {
      "msg": "Wrong X-API-Key, Forbidden",
      "type": "ForbiddenError"
    }
  ]
}
```