FROM python:3.11-slim

WORKDIR /app

ENV PYTHONPATH=/app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

ENV PYTHONUNBUFFERED 1

CMD ["python3", "-m", "fish.main"]

