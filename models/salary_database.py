import os
import pandas as pd
import sqlalchemy as sa
from sqlalchemy import create_engine, Column, Integer, String, Float, Date, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('salary_database')

Base = declarative_base()

class EmployeeSalary(Base):
    __tablename__ = 'employee_salaries'
    
    id = Column(Integer, primary_key=True)
    employee_id = Column(Integer)
    job_title = Column(String)
    department = Column(String)
    salary_yearly = Column(Float)
    salary_monthly = Column(Float)
    hire_date = Column(String)
    years_of_experience = Column(Integer)
    years_of_experience_company = Column(Float)
    performance_rating = Column(Integer)
    bonus_amount = Column(Float)
    total_compensation = Column(Float)
    
    def to_dict(self):
        return {
            'id': self.id,
            'employee_id': self.employee_id,
            'job_title': self.job_title,
            'department': self.department,
            'salary_yearly': self.salary_yearly,
            'salary_monthly': self.salary_monthly,
            'hire_date': self.hire_date,
            'years_of_experience': self.years_of_experience,
            'years_of_experience_company': self.years_of_experience_company,
            'performance_rating': self.performance_rating,
            'bonus_amount': self.bonus_amount,
            'total_compensation': self.total_compensation
        }

class SalaryDatabase:
    def __init__(self, db_path=None):
        # Use a specific database file if none provided
        if db_path is None:
            db_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'database')
            os.makedirs(db_dir, exist_ok=True)
            db_path = os.path.join(db_dir, 'salary.db')
            logger.info(f"Using default database path: {db_path}")
        
        # Create database directory if it doesn't exist
        os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)
        
        # Use absolute path for SQLite connection with explicit URI for better diagnostics
        db_uri = f'sqlite:///{os.path.abspath(db_path)}'
        logger.info(f"Connecting to database with URI: {db_uri}")
        
        try:
            self.engine = create_engine(db_uri, echo=True)
            
            # Create tables explicitly
            logger.info("Creating database tables...")
            Base.metadata.create_all(self.engine)
            logger.info("Tables created successfully")
            
            self.Session = sessionmaker(bind=self.engine)
            
            # Check if tables were created properly
            inspector = sa.inspect(self.engine)
            tables = inspector.get_table_names()
            logger.info(f"Tables in database: {tables}")
            
            if 'employee_salaries' not in tables:
                logger.error("employee_salaries table was not created!")
            
            # Check if we need to load data from CSV
            self.load_from_csv()
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            raise
    
    def connect(self):
        return self.Session()
    
    def disconnect(self, session=None):
        if session:
            session.close()
    
    def load_from_csv(self):
        try:
            # Find the CSV file in hexahaul_db directory
            script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            csv_path = os.path.join(script_dir, 'hexahaul_db', 'hh_employee_salary.csv')
            
            if not os.path.exists(csv_path):
                logger.error(f"CSV file not found: {csv_path}")
                return
            
            logger.info(f"Found CSV file at: {csv_path}")
            
            # Read the CSV file
            df = pd.read_csv(csv_path)
            logger.info(f"CSV loaded with {len(df)} rows")
            
            # Clean column names
            df.columns = [col.strip('"').lower().replace(' ', '_') for col in df.columns]
            logger.info(f"Columns after cleaning: {df.columns.tolist()}")
            
            # Check if data already exists
            session = self.connect()
            try:
                existing_count = session.query(EmployeeSalary).count()
                logger.info(f"Found {existing_count} existing records in database")
                
                if existing_count == 0:
                    logger.info(f"Loading salary data from CSV: {csv_path}")
                    # Convert DataFrame to list of dictionaries
                    records = df.to_dict('records')
                    
                    # Insert records into the database
                    for i, record in enumerate(records):
                        try:
                            # Handle any missing values
                            if pd.isna(record.get('department')):
                                record['department'] = None
                            
                            # Fix column name for years_of_experience_company
                            company_exp_key = 'years_of_experience_(company)'
                            if company_exp_key in record:
                                years_company = record[company_exp_key]
                            else:
                                logger.warning(f"Missing years_of_experience_(company) in record {i}")
                                years_company = 0.0
                            
                            # Create and add employee salary record
                            salary = EmployeeSalary(
                                employee_id=int(record['employee_id']),
                                job_title=record['job_title'],
                                department=record['department'],
                                salary_yearly=float(record['salary_yearly']),
                                salary_monthly=float(record['salary_monthly']),
                                hire_date=record['hire_date'],
                                years_of_experience=int(record['years_of_experience']),
                                years_of_experience_company=float(years_company),
                                performance_rating=int(record['performance_rating']),
                                bonus_amount=float(record['bonus_amount']),
                                total_compensation=float(record['total_compensation'])
                            )
                            session.add(salary)
                            
                            # Commit in batches to avoid memory issues
                            if i % 50 == 0:
                                session.commit()
                                logger.info(f"Committed batch of records (up to {i})")
                                
                        except Exception as e:
                            logger.error(f"Error processing record {i}: {e}")
                            logger.error(f"Record data: {record}")
                    
                    # Final commit
                    session.commit()
                    logger.info(f"Loaded {len(records)} salary records from CSV")
                    
                    # Verify data was loaded
                    count_after = session.query(EmployeeSalary).count()
                    logger.info(f"After loading, database has {count_after} records")
                else:
                    logger.info(f"Database already contains {existing_count} salary records")
            except Exception as e:
                logger.error(f"Error querying or loading data: {e}")
                session.rollback()
                raise
            finally:
                session.close()
        except Exception as e:
            logger.error(f"Error loading CSV data: {e}")
            raise
    
    def get_all_salaries(self):
        session = self.connect()
        try:
            salaries = session.query(EmployeeSalary).all()
            return salaries
        finally:
            self.disconnect(session)
    
    def get_salary_by_id(self, employee_id):
        session = self.connect()
        try:
            salary = session.query(EmployeeSalary).filter_by(employee_id=employee_id).first()
            return salary
        finally:
            self.disconnect(session)
    
    def add_salary(self, **kwargs):
        session = self.connect()
        try:
            new_salary = EmployeeSalary(**kwargs)
            session.add(new_salary)
            session.commit()
            return new_salary
        finally:
            self.disconnect(session)
    
    def update_salary(self, employee_id, **kwargs):
        session = self.connect()
        try:
            salary = session.query(EmployeeSalary).filter_by(employee_id=employee_id).first()
            if salary:
                for key, value in kwargs.items():
                    if hasattr(salary, key):
                        setattr(salary, key, value)
                session.commit()
                return True
            return False
        finally:
            self.disconnect(session)
    
    def delete_salary(self, employee_id):
        session = self.connect()
        try:
            salary = session.query(EmployeeSalary).filter_by(employee_id=employee_id).first()
            if salary:
                session.delete(salary)
                session.commit()
                return True
            return False
        finally:
            self.disconnect(session)
    
    def get_department_stats(self):
        """Get salary statistics by department"""
        session = self.connect()
        try:
            # Get all salaries
            salaries = session.query(EmployeeSalary).all()
            
            # Group by department
            departments = {}
            for salary in salaries:
                dept = salary.department if salary.department else "Other"
                if dept not in departments:
                    departments[dept] = {
                        'count': 0,
                        'total_salary': 0,
                        'total_bonus': 0
                    }
                departments[dept]['count'] += 1
                departments[dept]['total_salary'] += salary.salary_yearly
                departments[dept]['total_bonus'] += salary.bonus_amount
            
            # Calculate averages
            for dept in departments:
                count = departments[dept]['count']
                departments[dept]['avg_salary'] = departments[dept]['total_salary'] / count
                departments[dept]['avg_bonus'] = departments[dept]['total_bonus'] / count
            
            return departments
        finally:
            self.disconnect(session)
    
    def get_performance_stats(self):
        """Get salary statistics by performance rating"""
        session = self.connect()
        try:
            # Get all salaries
            salaries = session.query(EmployeeSalary).all()
            
            # Group by performance rating
            ratings = {}
            for salary in salaries:
                rating = salary.performance_rating
                if rating not in ratings:
                    ratings[rating] = {
                        'count': 0,
                        'total_salary': 0,
                        'total_bonus': 0
                    }
                ratings[rating]['count'] += 1
                ratings[rating]['total_salary'] += salary.salary_yearly
                ratings[rating]['total_bonus'] += salary.bonus_amount
            
            # Calculate averages
            for rating in ratings:
                count = ratings[rating]['count']
                ratings[rating]['avg_salary'] = ratings[rating]['total_salary'] / count
                ratings[rating]['avg_bonus'] = ratings[rating]['total_bonus'] / count
            
            return ratings
        finally:
            self.disconnect(session)
