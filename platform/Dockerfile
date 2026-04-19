FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV OTREE_ADMIN_PASSWORD=${OTREE_ADMIN_PASSWORD:-carbonsim}
ENV OTREE_PRODUCTION=1
ENV SECRET_KEY=${SECRET_KEY:-changeme-in-production}

EXPOSE 8000

CMD ["otree", "prodserver1of2"]