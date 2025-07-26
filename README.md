

# 🔐 Реферальная система с авторизацией

## 🌟 Ключевые особенности

### 🔑 Аутентификация
- **Встроенная Django-аутентификация** (сессии)
- Авторизация по номеру телефона
- Имитация SMS-верификации (4-значный код)
- Эндпоинты для входа/выхода

### 💼 Профиль пользователя
- Уникальный 6-значный инвайт-код
- Активация реферального кода
- Просмотр приглашенных пользователей

## 📚 API Документация

### Основные эндпоинты

| Метод | Путь | Описание |
|-------|------|----------|
| `POST` | `/api/v1/auth/send_code/` | Запрос кода подтверждения |
| `POST` | `/api/v1/auth/login/` | Подтверждение кода (вход) |
| `POST` | `/api/auth/logout/` | Выход из системы |
| `GET`  | `/api/v1/profile/` | Получить профиль |
| `POST` | `/api/v1/enter_code` | Активировать инвайт-код |


Также есть  /swagger  и /redoc
Для более удобного тестирования /api/v1/test/ - тут html формы для теста end points

## 🛠 Установка

```bash
docker-compose up --build
```
api доступно по адресу localhost:7777

## 🌍 Онлай версия достпна

Доступна по адресу: https://drf-referal-example-api.onrender.com/api/v1/test/

## 📦 Postman коллекция

[![Run in Postman](https://run.pstmn.io/button.svg)]([https://app.getpostman.com/run-collection/your-collection-id](https://nurmagomed.postman.co/workspace/mvvibro~98c2565e-d128-4b86-8667-86f023743248/collection/43720184-62503374-fdc8-418b-847e-619eb8012ee3?action=share&source=copy-link&creator=43720184))

