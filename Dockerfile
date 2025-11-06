# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY pyproject.toml ./
COPY src ./src

# Install Python dependencies
RUN pip install --no-cache-dir -e .

# Expose port (not strictly necessary for agents, but useful for debugging)
EXPOSE 8080

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Run the agent
CMD ["python", "-m", "livekit.agents.cli", "start", "src.ivy_homes_agent.agent"]
