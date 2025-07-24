FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Kopieer je hele app (inclusief templates, static, .env, etc.)
COPY . .

# Zet Flask in productieconfig (optioneel)
ENV FLASK_ENV=production

# Start de app
CMD ["python", "app.py"]