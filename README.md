### Докеризированное приложение для объявлений
  
  DB: Postgres
  API: FastAPI

  контейнеры: [db, web]  
  credentials stored in .env

### 1 Запускаем контейнеры

docker-compose up --build -d

### 2.1 Создание юзера

curl -X POST "http://localhost:8000/user" -H "Content-Type: application/json" -d '{
  "username": "testuser",
  "password": "testpassword",
  "group": "user"
}'

### 2.2 Создание админа

curl -X POST "http://localhost:8000/user" -H "Content-Type: application/json" -d '{
  "username": "admin",
  "password": "testpassword",
  "group": "admin"
}'

### 2.3 Создание второго юзера

curl -X POST "http://localhost:8000/user" -H "Content-Type: application/json" -d '{
  "username": "testuser2",
  "password": "testpassword",
  "group": "user"
}'

### 2.4 Логинимся юзером

curl -X POST "http://localhost:8000/login" -H "Content-Type: application/json" -d '{
  "username": "testuser",
  "password": "testpassword"
}'

### 2.5 Создание объявления

curl -X POST "http://localhost:8000/advertisement" \
-H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
-H "Content-Type: application/json" \
-d '{
  "title": "Продам велосипед",
  "description": "Горный велосипед в отличном состоянии",
  "price": 10000,
  "author": "testuser"
}'

### 2.6 Логинимся юзером2

curl -X POST "http://localhost:8000/login" -H "Content-Type: application/json" -d '{
  "username": "testuser2",
  "password": "testpassword"
}'

### 2.7 Попытка удалить объявление другого юзера

curl -X DELETE "http://localhost:8000/advertisement/1"

Получаем отказ

### 2.8 Логинимся админом

curl -X POST "http://localhost:8000/login" -H "Content-Type: application/json" -d '{
  "username": "admin",
  "password": "testpassword"
}'

### 2.9 Удаляем объявление

curl -X DELETE "http://localhost:8000/advertisement/1"

Успех

### 3 Просмотр документации:

http://localhost:8000/docs
