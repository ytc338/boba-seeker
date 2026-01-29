FROM python:3.12-slim

WORKDIR /app

# Install dependencies (with BuildKit cache)
# Install dependencies (with BuildKit cache)
COPY requirements.txt .
RUN pip install uv && \
    uv pip install --system -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd --create-home appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
