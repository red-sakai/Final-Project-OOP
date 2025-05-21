import os
import datetime
import pandas as pd
from sqlalchemy import create_engine, Column, Integer, String, Date, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session

Base = declarative_base()

class Employee(Base):
    __tablename__ = 'employees'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    employee_id = Column(Integer, unique=True)
    first_name = Column(String)
    last_name = Column(String)
    full_name = Column(String)
    gender = Column(String)
    age = Column(Integer)
    birthdate = Column(String)
    contact_number = Column(String)
    email = Column(String)
    department = Column(String)
    role = Column(String)
    hire_date = Column(String)
    license_number = Column(String)
    license_expiry = Column(String)
    assigned_vehicle = Column(Integer)
    status = Column(String, default='Active')

class EmployeeDatabase:
    def __init__(self, db_path="employees.db"):
        self.db_path = db_path
        self.engine = create_engine(f'sqlite:///{db_path}')
        self.session_factory = sessionmaker(bind=self.engine)
        self.Session = scoped_session(self.session_factory)
        self.initialize_database()
        
    def connect(self):
        return self.Session()
        
    def disconnect(self):
        self.Session.remove()
            
    def initialize_database(self):
        Base.metadata.create_all(self.engine)
        
        # Check if data already exists
        session = self.connect()
        count = session.query(Employee).count()
        if count == 0:
            self.populate_from_csv()
        self.disconnect()
        
    def populate_from_csv(self):
        csv_path = os.path.join('hexahaul_db', 'hh_employee_biography.csv')
        
        # Check if the CSV file exists
        if not os.path.exists(csv_path):
            # If CSV file is not found, use default data
            self.populate_initial_data()
            return
            
        # Read data from CSV file using pandas
        try:
            df = pd.read_csv(csv_path)
            session = self.connect()
            
            # Map CSV columns to our database schema
            for _, row in df.iterrows():
                # Determine role and department based on ID
                employee_id = row['Employee Id']
                if employee_id >= 201 and employee_id <= 240:
                    role = "Driver"
                    department = "Operations"
                elif employee_id >= 150 and employee_id <= 200:
                    role = "Dispatcher"
                    department = "Logistics"
                elif employee_id >= 100 and employee_id <= 149:
                    role = "Manager"
                    department = "Management"
                else:
                    role = "Admin"
                    department = "Admin"
                
                # Generate email from name
                email = f"{row['First Name'].lower()}.{row['Last Name'].lower()}@hexahaul.com"
                
                # Calculate hire date (use a random date in the past 5 years)
                # In a real application, this would be actual data
                hire_date = "2020-01-01"
                
                # Create new Employee object
                employee = Employee(
                    employee_id=employee_id,
                    first_name=row['First Name'],
                    last_name=row['Last Name'],
                    full_name=f"{row['First Name']} {row['Last Name']}",
                    gender=row['Gender'],
                    age=row['Age'],
                    birthdate=row['Birthdate'],
                    contact_number=row['Contact Number'],
                    email=email,
                    department=department,
                    role=role,
                    hire_date=hire_date,
                    license_number=None if role != "Driver" else f"LIC-{employee_id}",
                    license_expiry=None if role != "Driver" else "2025-12-31",
                    assigned_vehicle=None if role != "Driver" else employee_id,
                    status="Active"
                )
                session.add(employee)
            
            session.commit()
            self.disconnect()
        except Exception as e:
            print(f"Error loading data from CSV: {e}")
            # Fallback to default data if CSV loading fails
            self.populate_initial_data()
    
    def populate_initial_data(self):
        session = self.connect()
        
        # Sample employees
        employees = [
            Employee(employee_id=201, first_name="John", last_name="Doe", full_name="John Doe", 
                     gender="Male", age=35, birthdate="1988-05-15", contact_number="9123456789",
                     email="john.doe@hexahaul.com", department="Operations", role="Driver",
                     hire_date="2020-01-01", license_number="LIC-201", license_expiry="2025-12-31",
                     assigned_vehicle=1, status="Active"),
            Employee(employee_id=150, first_name="Jane", last_name="Smith", full_name="Jane Smith", 
                     gender="Female", age=28, birthdate="1995-08-20", contact_number="9198765432",
                     email="jane.smith@hexahaul.com", department="Logistics", role="Dispatcher",
                     hire_date="2019-03-15", license_number=None, license_expiry=None,
                     assigned_vehicle=None, status="Active"),
            Employee(employee_id=100, first_name="Michael", last_name="Johnson", full_name="Michael Johnson", 
                     gender="Male", age=42, birthdate="1981-12-03", contact_number="9187654321",
                     email="michael.johnson@hexahaul.com", department="Management", role="Manager",
                     hire_date="2018-06-10", license_number=None, license_expiry=None,
                     assigned_vehicle=None, status="Active")
        ]
        
        for employee in employees:
            session.add(employee)
        
        session.commit()
        self.disconnect()
    
    def get_all_employees(self):
        session = self.connect()
        employees = session.query(Employee).all()
        self.disconnect()
        return employees
        
    def get_employees_by_role(self, role):
        session = self.connect()
        employees = session.query(Employee).filter_by(role=role).all()
        self.disconnect()
        return employees
        
    def get_employee_by_id(self, employee_id):
        session = self.connect()
        employee = session.query(Employee).filter_by(id=employee_id).first()
        self.disconnect()
        return employee
        
    def update_employee(self, employee_id, **kwargs):
        session = self.connect()
        employee = session.query(Employee).filter_by(id=employee_id).first()
        
        if employee:
            for key, value in kwargs.items():
                if hasattr(employee, key):
                    setattr(employee, key, value)
            
            # Update full_name if first_name or last_name was changed
            if 'first_name' in kwargs or 'last_name' in kwargs:
                employee.full_name = f"{employee.first_name} {employee.last_name}"
            
            session.commit()
        
        self.disconnect()
        
    def delete_employee(self, employee_id):
        session = self.connect()
        employee = session.query(Employee).filter_by(id=employee_id).first()
        
        if employee:
            session.delete(employee)
            session.commit()
        
        self.disconnect()
        
    def add_employee(self, **kwargs):
        session = self.connect()
        
        # Update full_name if not provided
        if 'first_name' in kwargs and 'last_name' in kwargs and 'full_name' not in kwargs:
            kwargs['full_name'] = f"{kwargs['first_name']} {kwargs['last_name']}"
        
        employee = Employee(**kwargs)
        session.add(employee)
        session.commit()
        
        # Get the ID of the newly created employee
        employee_id = employee.id
        
        self.disconnect()
        return employee_id
