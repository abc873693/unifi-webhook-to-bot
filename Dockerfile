FROM python:3.11-slim

WORKDIR /app

COPY main.py /app/main.py

RUN pip install --no-cache-dir fastapi uvicorn python-telegram-bot requests PyJWT

RUN mkdir -p /app/output

VOLUME ["/app/output"]

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
