# ECS container: Python + Java (MPXJ via JPype)
FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    JAVA_TOOL_OPTIONS="-Djava.awt.headless=true"

# Java runtime for MPXJ
RUN apt-get update \
  && apt-get install -y --no-install-recommends openjdk-17-jre-headless ca-certificates \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python deps
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# App code
COPY mpxj_pm ./mpxj_pm
COPY api.py ./
COPY scripts ./scripts
COPY pm.sql README.md .env.template ./

# Expose API port
EXPOSE 8000

# Run API
CMD ["python", "api.py"]
