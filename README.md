### 1 Запускаем контейнеры

docker-compose up --build -d

### 2 Создание объявления

curl -X POST "http://localhost:8000/advertisements/" -H "Content-Type: application/json" -d '{
  "title": "Продам велосипед",
  "description": "Горный велосипед в отличном состоянии",
  "price": 10000,
  "author": "Иван Иванов"
}'

### 3 Получение объявления по ID:

curl -X GET "http://localhost:8000/advertisements/1"

### 4 Изменение объявления по ID:

curl -X PATCH "http://localhost:8000/advertisements/1" -H "Content-Type: application/json" -d '{
  "price": 9000
}'

### 5 Удаление объявления по ID:

curl -X DELETE "http://localhost:8000/advertisements/1"


### 6 Просмотр документации:

http://localhost:8000/docs
