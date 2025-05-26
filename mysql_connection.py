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
emp_connection = {
    'host': 'localhost', 
    'port': 3306,
    'username': 'your_username', # Input mysql username (eg. root)
    'password': 'your_password', # Input mysql password
    'database': 'schema_name' # Input mysql schema/database
}

emp_engine = create_engine(f"mysql+mysqlconnector://{emp_connection['username']}:{emp_connection['password']}@{emp_connection['host']}/{emp_connection['database']}", echo=False)

emp_Session = sessionmaker(bind=emp_engine)
emp_session = emp_Session()
