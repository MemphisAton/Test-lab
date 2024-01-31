
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY tests/ tests/
COPY alembic/ alembic/
COPY alembic.ini .
COPY main.py .
COPY crud.py .
COPY database.py .
COPY models.py .
COPY schemas.py .
COPY config.py .
COPY .env .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
