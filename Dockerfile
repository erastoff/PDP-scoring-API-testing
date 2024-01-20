# Используем базовый образ Python 3.10
FROM python:3.10

# Устанавливаем рабочую директорию в /app
WORKDIR .

# Копируем зависимости
COPY requirements.txt .
COPY scoring.py .
COPY test.py .
COPY store.py .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код в контейнер
COPY . .

# Указываем команду для запуска приложения
CMD ["python", "api.py"]