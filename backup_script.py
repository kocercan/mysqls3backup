import os
import subprocess
import boto3
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging

# Generate a timestamp for the backup file
timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
# Set up logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'backup_{timestamp}.log'),
        logging.StreamHandler()  # Log to standard output
    ]
)

# Environment variables
MYSQL_HOST = os.getenv('MYSQL_HOST')
MYSQL_USER = os.getenv('MYSQL_USER')
MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD')
MYSQL_DATABASE = os.getenv('MYSQL_DATABASE')

AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_S3_BUCKET = os.getenv('AWS_S3_BUCKET')
AWS_S3_REGION = os.getenv('AWS_S3_REGION', 'us-east-1')  # Default to us-east-1 if not provided

SMTP_SERVER = os.getenv('SMTP_SERVER')
SMTP_PORT = int(os.getenv('SMTP_PORT', 587))  # Default to 587 if not provided
SMTP_USER = os.getenv('SMTP_USER')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')
SMTP_SENDER = os.getenv('SMTP_SENDER')
SMTP_RECIPIENT = os.getenv('SMTP_RECIPIENT')

backup_file = f"{MYSQL_DATABASE}_{timestamp}.sql"
log_file = f"backup_{timestamp}.log"

def send_email(subject, body):
    msg = MIMEMultipart()
    msg['From'] = SMTP_SENDER
    msg['To'] = SMTP_RECIPIENT
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.sendmail(SMTP_SENDER, SMTP_RECIPIENT, msg.as_string())
        server.quit()
        logging.info("Email notification sent successfully")
    except Exception as e:
        logging.error(f"Error sending email: {e}")

# Dump the MySQL database to a file
try:
    subprocess.run([
        'mysqldump',
        f'--host={MYSQL_HOST}',
        f'--user={MYSQL_USER}',
        f'--password={MYSQL_PASSWORD}',
        '--routines',
        '--triggers',
        '--databases',
        '--default-character-set=utf8mb4',
        '--skip-add-locks',
        '--lock-tables=false',
        '--events',
        MYSQL_DATABASE,
        f'--result-file={backup_file}'
    ], check=True, capture_output=True)
    logging.info(f"Database dump successful: {backup_file}")
except subprocess.CalledProcessError as e:
    error_message = f"Error code: {e.returncode}, stderr: {e.stderr.decode('utf-8')}"
    logging.error(f"Error dumping database: {error_message}")
    send_email(f"Backup Failed: {MYSQL_DATABASE}", f"Error dumping database: {error_message}")
    exit(1)
except Exception as e:
    error_message = f"Unexpected error: {e}"
    logging.error(f"Error dumping database: {error_message}")
    send_email(f"Backup Failed: {MYSQL_DATABASE}", f"Error dumping database: {error_message}")
    exit(1)

# Upload the backup file to S3
try:
    s3 = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY, region_name=AWS_S3_REGION)
    s3.upload_file(backup_file, AWS_S3_BUCKET, backup_file)
    logging.info(f"Backup file uploaded to S3: {AWS_S3_BUCKET}/{backup_file}")
except Exception as e:
    error_message = f"Error uploading to S3: {e}"
    logging.error(f"Error uploading to S3: {error_message}")
    send_email(f"Backup Failed: {MYSQL_DATABASE}", f"Error uploading to S3: {error_message}")
    exit(1)

# Clean up the local backup file
try:
    os.remove(backup_file)
    logging.info(f"Local backup file removed: {backup_file}")
except Exception as e:
    error_message = f"Error cleaning up local backup file: {e}"
    logging.error(f"Error cleaning up local backup file: {error_message}")

# Clean up the local log file
try:
    os.remove(log_file)
    logging.info(f"Local log file removed: {log_file}")
except Exception as e:
    error_message = f"Error cleaning up local log file: {e}"
    logging.error(f"Error cleaning up local log file: {error_message}")

logging.info(f"Backup of {MYSQL_DATABASE} completed and uploaded to s3 bucket {AWS_S3_BUCKET}/{backup_file}")
send_email(f"Backup Successful: {MYSQL_DATABASE}", f"Backup of {MYSQL_DATABASE} completed and uploaded to s3 bucket {AWS_S3_BUCKET}/{backup_file}")
