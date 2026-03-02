# ComplianceIQ — production-style Docker image
FROM python:3.12-slim

WORKDIR /app

# Copy project (context is project root per docker-compose)
COPY . .

# Install dependencies from complianceiq/
RUN pip install --no-cache-dir -r complianceiq/requirements.txt

WORKDIR /app/complianceiq

EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
