### Dockerized Advertisement Application with Roles and Authorization

- **Database**: Postgres
- **API**: FastAPI
- **Token**: JWT
- **Roles**: user, admin

- **Containers**: [db, web]  
- **Credentials**: Stored in `.env`

### 1. Starting the Containers

docker-compose up --build -d

### 2.1 Creating a User

curl -X POST "http://localhost:8000/user" -H "Content-Type: application/json" -d '{
  "username": "testuser",
  "password": "testpassword",
  "group": "user"
}'

### 2.2 Creating an Admin

curl -X POST "http://localhost:8000/user" -H "Content-Type: application/json" -d '{
  "username": "admin",
  "password": "testpassword",
  "group": "admin"
}'

### 2.3 Creating a Second User

curl -X POST "http://localhost:8000/user" -H "Content-Type: application/json" -d '{
  "username": "testuser2",
  "password": "testpassword",
  "group": "user"
}'

### 2.4 Logging in as the First User

curl -X POST "http://localhost:8000/login" -H "Content-Type: application/x-www-form-urlencoded" 
-d "username=testuser&password=testpassword"

### 2.5 Creating an Advertisement

curl -X POST "http://localhost:8000/advertisement" \
-H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
-H "Content-Type: application/json" \
-d '{
  "title": "Selling a Bicycle",
  "description": "Mountain bike in excellent condition",
  "price": 10000,
  "author": "testuser"
}'

### 2.6 Logging in as the Second User

curl -X POST "http://localhost:8000/login" -H "Content-Type: application/x-www-form-urlencoded"
-d "username=testuser2&password=testpassword"

### 2.7 Attempting to Delete Another User's Advertisement

curl -X DELETE "http://localhost:8000/advertisement/1"

You will receive a rejection.

### 2.8 Logging in as the Admin

curl -X POST "http://localhost:8000/login" -H "Content-Type: application/x-www-form-urlencoded"
-d "username=admin&password=testpassword"

### 2.9 Deleting the Advertisement

curl -X DELETE "http://localhost:8000/advertisement/1"

Success.

### 3. Viewing the Documentation:

http://localhost:8000/docs
