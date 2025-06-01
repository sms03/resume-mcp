FROM python:3.10-slim

WORKDIR /app

# Install UV package manager
RUN pip install uv

# Copy requirements file
COPY requirements.txt .

# Install dependencies using UV
RUN uv pip install --system -r requirements.txt

# Copy the application code
COPY src/ ./src/

# Create necessary directories
RUN mkdir -p data logs

# Set environment variables
ENV PYTHONPATH=/app
ENV RESUME_MCP_HOST=0.0.0.0
ENV RESUME_MCP_PORT=8080

# Expose port
EXPOSE 8080

# Run the application
CMD ["python", "src/main.py"]
