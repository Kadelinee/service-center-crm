
# ServiceCenter CRM

Навчальний вебзастосунок для автоматизації роботи сервісного центру з ремонту техніки.

## Технології

**Backend:**
- Python 3.13
- Django 5.2
- Django REST Framework
- PostgreSQL
- django-cors-headers

**Frontend:**
- Vue.js
- Vite
- JavaScript
- HTML, CSS

## Функціональні можливості

- Перегляд статистики сервісного центру
- Управління клієнтами (CRUD)
- Перегляд каталогу послуг
- Створення замовлень
- Зміна статусів замовлень
- Збереження зв'язків між замовленнями та послугами
- Валідація даних
- Автентифікація та контроль доступу
- Адаптивний користувацький інтерфейс
- Взаємодія через REST API

## Структура проєкту

- `service-center-backend/` — серверна частина Django
- `service-center-frontend/` — клієнтська частина Vue.js

## Основні API-ендпоінти

- `/api/clients/` — клієнти
- `/api/services/` — послуги
- `/api/orders/` — замовлення
- `/api/order-services/` — послуги в замовленнях

## Запуск проєкту

Для роботи необхідні Python, Node.js і PostgreSQL.

### Backend

```bash
cd service-center-backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Створити локальний файл `.env` зі змінною
`DJANGO_SECRET_KEY` і налаштувати підключення
до PostgreSQL відповідно до `config/settings.py`.

Після підготовки бази даних:

```bash
python manage.py runserver
```

### Frontend

```bash
cd service-center-frontend
npm install
npm run dev
```

Вебзастосунок доступний за адресою:
http://localhost:5173/

## Призначення

Проєкт розроблено в межах лабораторних робіт
із дисципліни «Професійна практика програмної інженерії».
