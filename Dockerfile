# QuestMaster AI Dockerfile
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    g++ \
    git \
    wget \
    curl \
    unzip \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

RUN groupadd -r questmaster && useradd -r -g questmaster questmaster

COPY requirements.txt pyproject.toml ./
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

RUN git clone --depth 1 --branch release-24.06.1 https://github.com/aibasel/downward.git fast-downward-24.06.1

WORKDIR /app/fast-downward-24.06.1
RUN python build.py

WORKDIR /app

COPY src/ ./src/
COPY data/ ./data/
COPY resources/ ./resources/
COPY start.sh ./
COPY README.md ./

RUN pip install --no-cache-dir -e .

RUN mkdir -p /app/data /app/resources /app/logs

RUN chmod +x /app/start.sh

RUN chown -R questmaster:questmaster /app

USER questmaster

EXPOSE 8501

HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

CMD ["./start.sh"]
