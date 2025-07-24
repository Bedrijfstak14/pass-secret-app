FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Geen chmod nodig
# RUN chmod +x start.sh  ← deze mag weg

CMD ["sh", "start.sh"]
