import pandas as pd
import numpy as np
from sqlalchemy import create_engine, Column, Integer, String, Float, Date, BigInteger, ForeignKey, text, BigInteger, Identity, func 
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime, date
import warnings
import sys
import random
import os
import traceback 
from pathlib import Path
from dotenv import load_dotenv

# Suppress specific warnings
warnings.filterwarnings('ignore')

# Create SQLAlchemy base
Base = declarative_base()

# Load environment variables from .env
load_dotenv()

# Use values from .env
connection = {
    'host': os.getenv('MYSQL_HOST'),
    'port': int(os.getenv('MYSQL_PORT', 25060)),  # Default to 25060 if not set
    'username': os.getenv('MYSQL_USER'),
    'password': os.getenv('MYSQL_PASSWORD'),
    'database': os.getenv('MYSQL_DATABASE')
}

# Create engine using those values
engine = create_engine(
    f"mysql+mysqldb://{connection['username']}:{connection['password']}@{connection['host']}:{connection['port']}/{connection['database']}",
    echo=False
)
Session = sessionmaker(bind=engine)
session = Session()
