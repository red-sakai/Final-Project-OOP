import os
import pandas as pd
from sqlalchemy import create_engine, Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import hashlib
import secrets
import werkzeug.security

# Create a SQLite database for the application
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_PATH = os.path.join(BASE_DIR, 'hexahaul_db', 'hh_admins.csv')
DB_PATH = os.path.join(BASE_DIR, 'hexahaul_db', 'hexahaul.db')

# Create SQLAlchemy engine
engine = create_engine(f'sqlite:///{DB_PATH}', echo=False)
Base = declarative_base()

# Define Admin model
class Admin(Base):
    __tablename__ = 'admins'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    admin_fname = Column(String(50), nullable=False)
    admin_lname = Column(String(50), nullable=False)
    admin_username = Column(String(50), unique=True, nullable=False)
    admin_password = Column(String(255), nullable=False)
    
    def __repr__(self):
        return f"Admin(id={self.id}, username={self.admin_username})"
    
    @classmethod
    def authenticate(cls, session, username, password):
        """Authenticate an admin by username and password"""
        admin = session.query(cls).filter_by(admin_username=username).first()
        
        if admin:
            # For plain text passwords in CSV
            if admin.admin_password == password:
                return admin
                
            # For hashed passwords (future implementation)
            # if werkzeug.security.check_password_hash(admin.admin_password, password):
            #     return admin
                
        return None
    
    @classmethod
    def create_default_admin(cls, session):
        """Create a default admin if no admins exist"""
        admin_count = session.query(cls).count()
        if admin_count == 0:
            default_admin = cls(
                admin_fname="Default",
                admin_lname="Admin",
                admin_username="admin",
                admin_password="admin123"
            )
            session.add(default_admin)
            session.commit()
            print("Created default admin account")
            return default_admin
        return None
    
    @staticmethod
    def create(session, username, password, fname="Default", lname="Admin", otp_authentication=False):
        """Factory method to create an Admin with the correct parameters"""
        admin = Admin(
            admin_fname=fname,
            admin_lname=lname,
            admin_username=username,
            admin_password=password
        )
        session.add(admin)
        session.commit()
        return admin
    
    @classmethod
    def get_by_username(cls, session, username):
        """Get admin by username"""
        return session.query(cls).filter_by(admin_username=username).first()
        
    @classmethod
    def load_from_csv(cls, session):
        """Load admin data from CSV file"""
        if not os.path.exists(CSV_PATH):
            print(f"CSV file not found: {CSV_PATH}")
            return False
            
        try:
            # Read CSV file
            df = pd.read_csv(CSV_PATH, comment='/')
            
            # Check if admins table has data
            existing_count = session.query(cls).count()
            if existing_count > 0:
                print(f"Admin table already has {existing_count} records.")
                return True
                
            # Insert data from CSV
            for _, row in df.iterrows():
                admin = cls(
                    admin_fname=row['admin_fname'],
                    admin_lname=row['admin_lname'],
                    admin_username=row['admin_username'],
                    admin_password=row['admin_password']
                )
                session.add(admin)
                
            session.commit()
            print(f"Successfully loaded {len(df)} admin records from CSV.")
            return True
            
        except Exception as e:
            session.rollback()
            print(f"Error loading admin data from CSV: {e}")
            return False

# Create tables
Base.metadata.create_all(engine)

# Create session
Session = sessionmaker(bind=engine)

def init_admin_db():
    """Initialize admin database by loading data from CSV"""
    session = Session()
    success = Admin.load_from_csv(session)
    session.close()
    return success

def get_db_session():
    """Get a new database session"""
    return Session()

def get_default_admin():
    """Get or create a default admin account"""
    session = Session()
    try:
        admin = session.query(Admin).filter_by(admin_username="admin").first()
        if not admin:
            admin = Admin.create_default_admin(session)
        return admin
    finally:
        session.close()
