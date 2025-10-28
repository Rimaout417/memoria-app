# Python 3.13.5 を使用
FROM python:3.13-slim

WORKDIR /app

# psycopg[binary] はビルド不要だが、他の依存でCコンパイルが必要になることがあるため minimal toolsetを入れておく
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]