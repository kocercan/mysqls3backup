FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    default-mysql-client \
    libmariadb-dev \
    libssl-dev \
    gcc \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --no-cache-dir \
    boto3 \
    mysqlclient \
    cryptography

# Copy the backup script
COPY backup_script.py /app/backup_script.py

# Set the working directory
WORKDIR /app

# Command to run the script
CMD ["python", "backup_script.py"]
