FROM python:3.11-slim

WORKDIR /app

# Install system deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl unzip gcc && \
    rm -rf /var/lib/apt/lists/*

# Install Node.js (required by Reflex for frontend build)
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs && \
    npm install -g bun

# Install Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app
COPY . .

# Initialize Reflex (creates .web directory + compiles frontend)
RUN reflex init
RUN reflex export --frontend-only --no-zip

# Expose ports
EXPOSE 3000 8000

# Run in production mode
CMD ["reflex", "run", "--env", "prod"]
