import os
import pandas as pd
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from abc import ABC, abstractmethod

Base = declarative_base()

class UserLogin(Base):
    __tablename__ = 'user_logins'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(Integer, nullable=False)
    customer_fname = Column(String(50), nullable=False)
    customer_lname = Column(String(50), nullable=False)
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(100), nullable=False)
    
    def __repr__(self):
        return f"<UserLogin(username='{self.username}', customer_id={self.customer_id})>"

# Create database engine
db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'hexahaul_db', 'hexahaul.db')
engine = create_engine(f'sqlite:///{db_path}')

# Create session factory
Session = sessionmaker(bind=engine)

# Define abstract base class for data managers
class DataManager(ABC):
    @abstractmethod
    def initialize_database(self):
        pass
    
    @abstractmethod
    def load_data(self):
        pass

# Define a user manager class that implements the DataManager interface
class UserLoginManager(DataManager):
    def __init__(self, engine, session_factory):
        self.engine = engine
        self.Session = session_factory
        
    def initialize_database(self):
        """Initialize the database tables"""
        Base.metadata.create_all(self.engine)
        
    def load_data(self):
        """Load user data from CSV into the database"""
        # Get the path to the CSV file
        csv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'hexahaul_db', 'hh_user-login.csv')
        
        # Read the CSV file using pandas
        df = pd.read_csv(csv_path)
        
        # Create a session
        session = self.Session()
        
        try:
            # Check if data already exists
            if session.query(UserLogin).count() == 0:
                # Insert data from dataframe into database
                for _, row in df.iterrows():
                    user = UserLogin(
                        customer_id=row['Customer Id'],
                        customer_fname=row['Customer Fname'],
                        customer_lname=row['Customer Lname'],
                        username=row['Username'],
                        password=row['Password']
                    )
                    session.add(user)
                
                # Commit the changes
                session.commit()
                print(f"Successfully loaded {len(df)} users from CSV")
            else:
                print("User data already exists in the database")
        except Exception as e:
            session.rollback()
            print(f"Error loading user data: {e}")
        finally:
            session.close()
    
    def authenticate_user(self, username, password):
        """Authenticate a user based on username and password"""
        session = self.Session()
        try:
            # Query the user by username
            user = session.query(UserLogin).filter(UserLogin.username == username).first()
            
            # Check if user exists and password matches
            if user and user.password == password:
                return user
            return None
        except Exception as e:
            print(f"Authentication error: {e}")
            return None
        finally:
            session.close()
            
    def get_user_by_id(self, customer_id):
        """Get a user by their customer ID"""
        session = self.Session()
        try:
            return session.query(UserLogin).filter(UserLogin.customer_id == customer_id).first()
        except Exception as e:
            print(f"Error getting user: {e}")
            return None
        finally:
            session.close()
            
    def update_password(self, username, new_password):
        """Update a user's password"""
        session = self.Session()
        try:
            user = session.query(UserLogin).filter(UserLogin.username == username).first()
            if user:
                user.password = new_password
                session.commit()
                return True
            return False
        except Exception as e:
            session.rollback()
            print(f"Error updating password: {e}")
            return False
        finally:
            session.close()

# Create a singleton instance of the user manager
user_manager = UserLoginManager(engine, Session)

# Functions for backward compatibility
def init_db():
    user_manager.initialize_database()

def load_users_from_csv():
    user_manager.load_data()

def authenticate_user(username, password):
    return user_manager.authenticate_user(username, password)