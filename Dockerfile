# Вихідний образ
FROM python:3.11-slim

# Оновлення та встановлення залежностей
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    dos2unix \
    && rm -rf /var/lib/apt/lists/*

# Робоча директорія
WORKDIR /app

# Копіюємо requirements
COPY requirements.txt /app/

# Встановлюємо Python залежності
RUN pip install --no-cache-dir -r requirements.txt

# Копіюємо весь проект
COPY . /app/

# Конвертуємо line endings та робимо скрипт виконуваним
RUN dos2unix /app/docker-entrypoint.sh && \
    chmod +x /app/docker-entrypoint.sh

# Порт
EXPOSE 8000

# Команда старту
CMD ["/app/docker-entrypoint.sh"]
