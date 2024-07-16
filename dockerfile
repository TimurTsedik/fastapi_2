# Используем официальный образ Python в качестве базового
FROM python:3.11

# Устанавливаем рабочую директорию
WORKDIR /code

# Копируем файлы requirements.txt в контейнер
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь код приложения в контейнер
COPY . .

# Открываем порт 8000 для доступа к приложению
EXPOSE 8000

# Команда для запуска приложения с задержкой
CMD ["sh", "-c", "sleep 20 && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
