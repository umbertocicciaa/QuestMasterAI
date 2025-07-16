# QuestMaster AI Dockerfile
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    g++ \
    git \
    wget \
    curl \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Create non-root user
RUN groupadd -r questmaster && useradd -r -g questmaster questmaster

# Copy requirements first for better caching
COPY requirements.txt pyproject.toml ./
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Download and build Fast Downward
RUN git clone --depth 1 --branch release-24.06.1 https://github.com/aibasel/downward.git fast-downward-24.06.1

# Build Fast Downward
WORKDIR /app/fast-downward-24.06.1
RUN python build.py

# Switch back to app directory
WORKDIR /app

# Copy application code
COPY src/ ./src/
COPY data/ ./data/
COPY resources/ ./resources/
COPY README.md ./

# Install the application
RUN pip install --no-cache-dir -e .

# Create necessary directories
RUN mkdir -p /app/data /app/resources /app/logs

# Change ownership to questmaster user
RUN chown -R questmaster:questmaster /app

# Switch to non-root user
USER questmaster

# Expose Streamlit port
EXPOSE 8501

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Default command
CMD ["python", "-m", "questmaster.cli", "run"]
