# MySQL Backup to S3 with Email Notifications

This repository contains a Kubernetes CronJob that automates the backup of a MySQL database and uploads the backup to an AWS S3 bucket. Additionally, it sends email notifications upon successful or failed backup operations.

## Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Configuration](#configuration)
- [Deployment](#deployment)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)

## Overview

The application consists of the following components:

- **Dockerfile**: A Dockerfile to build the backup script container.
- **backup_script.py**: A Python script that performs the MySQL database dump, uploads the backup to S3, and sends email notifications.
- **configmap.yaml**: A Kubernetes ConfigMap that stores non-sensitive configuration data.
- **secrets.yaml**: A Kubernetes Secret that stores sensitive data such as credentials.
- **cronjob.yaml**: A Kubernetes CronJob that schedules the backup operation.

## Prerequisites

Before deploying this application, ensure you have the following:

- A Kubernetes cluster (e.g., Minikube, GKE, EKS).
- `kubectl` installed and configured to interact with your Kubernetes cluster.
- An AWS account with an S3 bucket created.
- A MySQL database to back up.
- SMTP server credentials for sending email notifications.

## Configuration

### ConfigMap (`configmap.yaml`)

The `configmap.yaml` file contains non-sensitive configuration data such as MySQL host, database name, S3 bucket details, and SMTP server details.

### Secrets (`secrets.yaml`)

The `secrets.yaml` file contains sensitive data such as MySQL credentials, AWS access keys, and SMTP credentials.

### CronJob (`cronjob.yaml`)

The `cronjob.yaml` file defines the CronJob that schedules the backup operation. It specifies the schedule, environment variables, and resource limits.

## Deployment

1. **Build the Docker Image**:
   ```bash
   docker build -t <your-dockerhub-username>/mysqls3backup:latest .
   ```

2. **Push the Docker Image**:
   ```bash
   docker push <your-dockerhub-username>/mysqls3backup:latest
   ```

3. **Deploy ConfigMap and Secrets**:
   ```bash
   kubectl apply -f configmap.yaml
   kubectl apply -f secrets.yaml
   ```

4. **Deploy CronJob**:
   ```bash
   kubectl apply -f cronjob.yaml
   ```

## Usage

- The CronJob is scheduled to run at 2 AM every day. You can modify the schedule in the `cronjob.yaml` file.
- The backup script will dump the MySQL database, upload the backup to the specified S3 bucket, and send an email notification.
- Logs and local backup files are cleaned up after the operation.

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
