import pandas as pd
import numpy as np
from sqlalchemy import create_engine, Column, Integer, String, Float, Date, BigInteger, ForeignKey, text, BigInteger, Identity, func 
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime, date
import warnings
import sys

# Suppress specific warnings
warnings.filterwarnings('ignore')

# Create SQLAlchemy base
Base = declarative_base()

# Database configuration
connection = {
    'host': 'localhost', 
    'port': 3306,
    'username': 'your_username', # Input mysql username (eg. root)
    'password': 'your_password', # Input mysql password
    'database': 'schema_name' # Input mysql schema/database
}

engine = create_engine(f"mysql+mysqlconnector://{connection['username']}:{connection['password']}@{connection['host']}/{connection['database']}", echo=False)

Session = sessionmaker(bind=engine)
session = Session()
