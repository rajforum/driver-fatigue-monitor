import os

# Project directory and sub-directory paths
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))

APP_DIR = os.path.join(PROJECT_DIR, 'app')
DATASET_MODEL_DIR = os.path.join(PROJECT_DIR, 'dataset-model')
CONFIG_DIR = os.path.join(PROJECT_DIR, 'config')
LOGS_DIR = os.path.join(PROJECT_DIR, 'logs')

# Define the path to the SSL files
SSL_CERT_PATH = os.path.join(PROJECT_DIR, 'ssl', 'certificate.pem')
SSL_KEY_PATH = os.path.join(PROJECT_DIR, 'ssl', 'private.pem')