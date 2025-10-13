"""
Configuration settings for Fraud Detection Dashboard
"""

import os
from pathlib import Path

# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent
BACKEND_ROOT = Path(__file__).parent

# Data directories
DATA_DIR = PROJECT_ROOT / 'data'
INPUT_DIR = DATA_DIR / 'input'
OUTPUT_DIR = DATA_DIR / 'output'

# Create directories if they don't exist
INPUT_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Database configuration
DATABASE_PATH = OUTPUT_DIR / 'fraud_detection.db'

# Input data files
EXTERNAL_FRAUD_SCORES_FILE = INPUT_DIR / 'external_fraud_scores.csv'
CLAIM_FRAUD_RULES_FILE = INPUT_DIR / 'claim_fraud_rules.csv'

# API configuration
API_HOST = '0.0.0.0'
API_PORT = 5000
API_DEBUG = True

# CORS configuration
CORS_ORIGINS = ['http://localhost:3000', 'http://localhost:5173']

# Data processing configuration
NER_METHOD = 'spacy'  # 'spacy' or 'huggingface'
K_CLIQUE_SIZE = 3  # Minimum clique size for community detection

# Scoring weights
SOCIAL_NETWORK_WEIGHT = 0.6
EXTERNAL_FRAUD_WEIGHT = 0.4

# Centrality weights for social network score
DEGREE_CENTRALITY_WEIGHT = 0.4
BETWEENNESS_CENTRALITY_WEIGHT = 0.3
EIGENVECTOR_CENTRALITY_WEIGHT = 0.3

# Investigation status options
VALID_STATUSES = [
    'Not Reviewed',
    'Under Investigation',
    'Bad Actor',
    'Cleared'
]

# Logging configuration
LOG_LEVEL = 'INFO'
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'