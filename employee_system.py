"""
Employee Management System - Clean Structure
===========================================

This module provides a comprehensive employee management system with
database operations for employee biography, salary, and vehicle information.
Uses a traditional procedural approach without lambda functions or menu handlers.
"""

from datetime import datetime
from mysql_connection import *
import pandas as pd


# ==============================================================================
# DATABASE MODELS
# ==============================================================================

class EmployeeBiography(Base):
    """
    Database model for employee biography information.
    
    Stores personal details including name, age, gender, birthdate, and contact info.
    Has one-to-one relationships with salary and vehicle information.
    """
    
    __tablename__ = "hh_employee_biography"

    # Primary key and basic information columns
    emp_id = Column("Employee Id", Integer, primary_key=True, nullable=False)
    fname = Column("First Name", String(100), nullable=False)
    lname = Column("Last Name", String(100), nullable=False)
    gender = Column("Gender", String(10), nullable=False)
    age = Column("Age", Integer, nullable=False)
    birthdate = Column("birth_date", Date, nullable=False)
    contact_num = Column("Contact Number", BigInteger, nullable=False)

    # Define relationships to other tables
    salary_info = relationship(
        'EmployeeSalary', 
        back_populates='employee', 
        uselist=False, 
        cascade="all, delete-orphan"
    )
    vehicle_info = relationship(
        'EmployeeVehicle', 
        back_populates='employee', 
        uselist=False, 
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Employee Biography: id={self.emp_id}, name={self.fname} {self.lname}>"


class EmployeeSalary(Base):
    """
    Database model for employee salary and job information.
    
    Contains job title, department, compensation details, and performance ratings.
    Links to employee biography through foreign key relationship.
    """
    
    __tablename__ = "hh_employee_salary"

    # Primary key and foreign key reference
    emp_id = Column(
        "Employee Id", 
        Integer, 
        ForeignKey("hh_employee_biography.Employee Id"), 
        primary_key=True, 
        nullable=False
    )
    
    # Job and department information
    job_title = Column("Job Title", String(100), nullable=False)
    department = Column("Department", String(100), nullable=False)
    hire_date = Column("hire_date", Date, nullable=False)
    
    # Experience tracking columns
    years_exp = Column("Years of Experience", Integer, nullable=False)
    years_exp_comp = Column("Years of Experience (company)", Float, nullable=False)
    
    # Compensation structure columns
    yearly_sal = Column("salary_yearly", Float, nullable=False)
    monthly_sal = Column("salary_monthly", Float, nullable=False)
    bonus = Column("bonus_amount", Float, nullable=False)
    compensation = Column("Total Compensation", Float, nullable=False)
    
    # Performance evaluation column
    rating = Column("Performance Rating", Integer, nullable=True)

    # Relationship back to employee biography
    employee = relationship('EmployeeBiography', back_populates='salary_info', uselist=False)

    def __repr__(self):
        return f"<Employee Salary: id={self.emp_id}, job_title={self.job_title}, salary={self.yearly_sal}>"


class EmployeeVehicle(Base):
    """
    Database model for employee vehicle information.
    
    Stores vehicle details including make, model, year, mileage, and weight capacity.
    Only applicable to employees with delivery driver roles.
    """
    
    __tablename__ = "hh_vehicle"

    # Primary key and foreign key reference
    emp_id = Column(
        "Employee Id", 
        Integer, 
        ForeignKey("hh_employee_biography.Employee Id"), 
        primary_key=True, 
        nullable=False
    )
    
    # Vehicle specification columns
    unit_name = Column("unit_name", String(100), nullable=False)
    unit_brand = Column("unit_brand", String(100), nullable=False)
    year = Column("year", Integer, nullable=False)
    km_driven = Column("km_driven", Integer, nullable=False)
    
    # Weight capacity specification columns
    min_weight = Column("min_weight", Float, nullable=False)
    max_weight = Column("max_weight", Float, nullable=False)

    # Relationship back to employee biography
    employee = relationship('EmployeeBiography', back_populates='vehicle_info', uselist=False)

    def __repr__(self):
        return f"<Vehicle Driver: id={self.emp_id}, unit={self.unit_name}>"


# ==============================================================================
# CONFIGURATION CONSTANTS
# ==============================================================================

# Predefined vehicle weight capacities mapping
VEHICLE_WEIGHT_MAP = {
    'Honda Civic': (25, 350),
    'MG 5': (25, 350),
    'Toyota Vios': (20, 300),
    'Yamaha Mio Sporty': (0.1, 20),
    'Yamaha NMAX': (25, 80),
    'Honda Click 125i': (0.1, 25),
    'Mitsubishi Fuso Fighter': (3000, 7000),
    'Hino 700 Series Dump Truck': (7000, 15000),
    'Isuzu ELF NHR 55': (350, 3000),
}

# Performance rating validation range
PERFORMANCE_RATING_RANGE = (1, 5)

# Standard date format for user inputs
DATE_FORMAT = "%Y-%m-%d"

# Age validation range for employees
MIN_EMPLOYEE_AGE = 16
MAX_EMPLOYEE_AGE = 70

# Contact number validation range
MIN_CONTACT_NUMBER = 1000000000
MAX_CONTACT_NUMBER = 99999999999


# ==============================================================================
# UTILITY FUNCTIONS
# ==============================================================================

def get_valid_date(prompt="Enter date (YYYY-MM-DD): "):
    """
    Prompt user for a valid date input and return a date object.
    
    Args:
        prompt (str): Custom prompt message for date input
        
    Returns:
        datetime.date: Validated date object
        
    Raises:
        ValueError: If date format is invalid (handled internally with retry)
    """
    while True:
        try:
            date_str = input(prompt).strip()
            return datetime.strptime(date_str, DATE_FORMAT).date()
        except ValueError:
            print(f"Invalid format. Please use {DATE_FORMAT} format.")


def get_valid_integer(prompt, min_val=None, max_val=None):
    """
    Prompt user for a valid integer input with optional range validation.
    
    Args:
        prompt (str): Prompt message for integer input
        min_val (int, optional): Minimum allowed value
        max_val (int, optional): Maximum allowed value
        
    Returns:
        int: Validated integer value
        
    Raises:
        ValueError: If input is not a valid integer (handled internally with retry)
    """
    while True:
        try:
            value = int(input(prompt))
            # Validate minimum value if specified
            if min_val is not None and value < min_val:
                print(f"Value must be at least {min_val}.")
                continue
            # Validate maximum value if specified
            if max_val is not None and value > max_val:
                print(f"Value must be at most {max_val}.")
                continue
            return value
        except ValueError:
            print("Please enter a valid integer.")


def get_valid_float(prompt, min_val=None):
    """
    Prompt user for a valid float input with optional minimum validation.
    
    Args:
        prompt (str): Prompt message for float input
        min_val (float, optional): Minimum allowed value
        
    Returns:
        float: Validated float value
        
    Raises:
        ValueError: If input is not a valid float (handled internally with retry)
    """
    while True:
        try:
            value = float(input(prompt))
            # Validate minimum value if specified
            if min_val is not None and value < min_val:
                print(f"Value must be at least {min_val}.")
                continue
            return value
        except ValueError:
            print("Please enter a valid number.")


def calculate_monthly_salary(yearly_salary):
    """
    Calculate monthly salary from yearly salary amount.
    
    Args:
        yearly_salary (float): Annual salary amount
        
    Returns:
        float: Monthly salary rounded to 2 decimal places
    """
    return round(yearly_salary / 12, 2)


def calculate_total_compensation(yearly_salary, bonus):
    """
    Calculate total compensation from yearly salary and bonus amount.
    
    Args:
        yearly_salary (float): Annual salary amount
        bonus (float): Bonus amount
        
    Returns:
        float: Total compensation rounded to 2 decimal places
    """
    return round(yearly_salary + bonus, 2)


def validate_gender_input():
    """
    Prompt user for valid gender input with validation.
    
    Returns:
        str: Validated gender value ('Male' or 'Female')
    """
    while True:
        gender = input("Gender (Male/Female): ").strip().title()
        if gender in ['Male', 'Female']:
            return gender
        print("Please enter 'Male' or 'Female'.")


def validate_vehicle_unit():
    """
    Prompt user for valid vehicle unit with validation against available options.
    
    Returns:
        str: Validated vehicle unit name
    """
    # Display available vehicle options to user
    print("Available vehicles:")
    for i, vehicle in enumerate(VEHICLE_WEIGHT_MAP.keys(), 1):
        print(f"{i}. {vehicle}")
    
    while True:
        unit_name = input("Vehicle unit name: ").strip().title()
        if unit_name in VEHICLE_WEIGHT_MAP:
            return unit_name
        print(f"Vehicle '{unit_name}' not found in available options.")


# ==============================================================================
# DATA INPUT COLLECTION FUNCTIONS
# ==============================================================================

def get_employee_biography_data():
    """
    Collect employee biography information from user input.
    
    Prompts user for personal information including name, gender, age,
    birthdate, and contact number with appropriate validation.
    
    Returns:
        dict: Dictionary containing validated biography data
    """
    print("\nEnter Employee Biography Information:")
    print("-" * 40)
    
    # Collect basic personal information
    fname = input("First name: ").strip().title()
    lname = input("Last name: ").strip().title()
    
    # Validate gender input
    gender = validate_gender_input()
    
    # Collect and validate age within acceptable range
    age = get_valid_integer("Age: ", min_val=MIN_EMPLOYEE_AGE, max_val=MAX_EMPLOYEE_AGE)
    
    # Collect and validate birthdate
    birthdate = get_valid_date("Birthdate (YYYY-MM-DD): ")
    
    # Collect and validate contact number within range
    contact_num = get_valid_integer(
        "Contact number: ", 
        min_val=MIN_CONTACT_NUMBER, 
        max_val=MAX_CONTACT_NUMBER
    )

    # Return structured biography data
    return {
        'fname': fname,
        'lname': lname,
        'gender': gender,
        'age': age,
        'birthdate': birthdate,
        'contact_num': contact_num
    }


def get_employee_salary_data():
    """
    Collect employee salary and job information from user input.
    
    Prompts user for job details, compensation information, and performance
    ratings with appropriate validation and automatic calculations.
    
    Returns:
        dict: Dictionary containing validated salary and job data
    """
    print("\nEnter Employee Salary Information:")
    print("-" * 40)
    
    # Collect job and department information
    job_title = input("Job title: ").strip().title()
    department = input("Department: ").strip().title()
    
    # Collect and validate salary information
    yearly_salary = get_valid_float("Yearly salary: ", min_val=0)
    monthly_salary = calculate_monthly_salary(yearly_salary)
    
    # Collect hire date
    hire_date = get_valid_date("Hire date (YYYY-MM-DD): ")
    
    # Collect experience information
    years_exp = get_valid_integer("Total years of experience: ", min_val=0)
    years_exp_comp = get_valid_float("Years of experience in company: ", min_val=0)
    
    # Collect and validate performance rating
    rating = get_valid_integer(
        f"Performance rating ({PERFORMANCE_RATING_RANGE[0]}-{PERFORMANCE_RATING_RANGE[1]}): ",
        min_val=PERFORMANCE_RATING_RANGE[0],
        max_val=PERFORMANCE_RATING_RANGE[1]
    )
    
    # Collect bonus information and calculate total compensation
    bonus_amount = get_valid_float("Bonus amount: ", min_val=0)
    total_compensation = calculate_total_compensation(yearly_salary, bonus_amount)

    # Return structured salary data
    return {
        'job_title': job_title,
        'department': department,
        'yearly_sal': yearly_salary,
        'monthly_sal': monthly_salary,
        'hire_date': hire_date,
        'years_exp': years_exp,
        'years_exp_comp': years_exp_comp,
        'rating': rating,
        'bonus': bonus_amount,
        'compensation': total_compensation
    }


def get_employee_vehicle_data(job_title):
    """
    Collect employee vehicle information from user input if applicable.
    
    Only collects vehicle information for delivery driver positions.
    Validates vehicle selection against predefined options.
    
    Args:
        job_title (str): Employee's job title to determine if vehicle data needed
        
    Returns:
        dict or None: Dictionary containing vehicle data if applicable, None otherwise
    """
    # Only collect vehicle data for delivery drivers
    if job_title.lower() != "delivery driver":
        return None

    print("\nEnter Employee Vehicle Information:")
    print("-" * 40)
    
    # Validate and collect vehicle unit information
    unit_name = validate_vehicle_unit()
    unit_brand = input("Unit brand: ").strip().title()
    
    # Collect vehicle specifications
    current_year = datetime.now().year
    year = get_valid_integer("Vehicle year: ", min_val=1990, max_val=current_year + 1)
    km_driven = get_valid_integer("Kilometers driven: ", min_val=0)
    
    # Get predefined weight capacity for selected vehicle
    min_weight, max_weight = VEHICLE_WEIGHT_MAP[unit_name]

    # Return structured vehicle data
    return {
        'unit_name': unit_name,
        'unit_brand': unit_brand,
        'year': year,
        'km_driven': km_driven,
        'min_weight': min_weight,
        'max_weight': max_weight
    }


def get_complete_employee_data():
    """
    Collect all employee data including biography, salary, and vehicle information.
    
    Orchestrates the collection of all employee information by calling
    individual data collection functions in sequence.
    
    Returns:
        tuple: (bio_data, salary_data, vehicle_data) or (None, None, None) on error
    """
    try:
        # Collect biography information
        bio_data = get_employee_biography_data()
        
        # Collect salary and job information
        salary_data = get_employee_salary_data()
        
        # Collect vehicle information if applicable
        vehicle_data = get_employee_vehicle_data(salary_data['job_title'])
        
        return bio_data, salary_data, vehicle_data
        
    except (ValueError, KeyboardInterrupt) as e:
        print(f"Data input cancelled or invalid: {e}")
        return None, None, None


def get_existing_employee_update_data():
    """
    Get existing employee data for update operations.
    
    Prompts user for employee ID, validates existence, and collects
    updated information for the specified employee.
    
    Returns:
        tuple: (bio_data, salary_data, vehicle_data) or (None, None, None) on cancellation
    """
    while True:
        # Prompt for employee ID to update
        employee_id = get_valid_integer("Enter Employee ID: ", min_val=1)
        
        # Check if employee exists in database
        emp = session.query(EmployeeBiography).filter_by(emp_id=employee_id).first()
        
        if not emp:
            print("Employee not found. Please try again.")
            continue

        # Display existing employee information for confirmation
        print(f"\nFound employee: {emp}")
        confirm = input("Update this employee? (Y/N): ").strip().lower()

        if confirm == 'y':
            # Collect updated employee data
            bio_data, salary_data, vehicle_data = get_complete_employee_data()
            if bio_data is not None:
                # Add employee ID to biography data for update reference
                bio_data['employee_id'] = employee_id
            return bio_data, salary_data, vehicle_data
        else:
            # User cancelled the update operation
            return None, None, None


# ==============================================================================
# MAIN EMPLOYEE MANAGEMENT CLASS
# ==============================================================================

class EmployeeManagement:
    """
    Main class for managing employee records and database operations.
    
    Provides methods for creating, reading, updating, and deleting employee
    records with proper transaction management and error handling.
    """
    
    def __init__(self):
        """Initialize the employee management system with database session."""
        self.session = session

    def add_complete_employee_record(self, bio_data, salary_data, vehicle_data):
        """
        Add or update a complete employee record in the database.
        
        Determines whether to create a new employee or update existing based
        on presence of employee_id in bio_data. Handles database transactions
        with proper rollback on errors.
        
        Args:
            bio_data (dict): Employee biography information
            salary_data (dict): Employee salary and job information
            vehicle_data (dict or None): Vehicle information if applicable
            
        Raises:
            Exception: Database operation errors are re-raised after rollback
        """
        session = self.session
        
        try:
            # Check if this is an update operation
            employee_id = bio_data.get('employee_id')
            
            if employee_id is not None:
                # Look for existing employee record
                existing_bio = session.query(EmployeeBiography).filter_by(emp_id=employee_id).first()
            else:
                existing_bio = None

            if existing_bio:
                # Update existing employee record
                self._update_existing_employee(session, employee_id, bio_data, salary_data, vehicle_data)
                print(f"Updated employee record for ID: {employee_id}")
            else:
                # Create new employee record
                bio_data.pop('employee_id', None)  # Remove ID for new record
                new_employee_id = self._create_new_employee(session, bio_data, salary_data, vehicle_data)
                print(f"Added new employee record with ID: {new_employee_id}")
            
            # Commit the database transaction
            session.commit()
            
        except Exception as e:
            # Rollback transaction on any error
            session.rollback()
            print(f"Error managing employee record: {e}")
            raise
        finally:
            # Always close the session
            session.close()

    def _create_new_employee(self, session, bio_data, salary_data, vehicle_data):
        """
        Create a new employee record with auto-generated ID.
        
        Generates next available employee ID and creates records in all
        related tables (biography, salary, and vehicle if applicable).
        
        Args:
            session: Database session for transaction
            bio_data (dict): Employee biography information
            salary_data (dict): Employee salary information
            vehicle_data (dict or None): Vehicle information if applicable
            
        Returns:
            int: New employee ID that was assigned
        """
        # Generate next available employee ID
        latest_id = session.query(func.max(EmployeeBiography.emp_id)).scalar() or 0
        new_employee_id = latest_id + 1

        # Create employee biography record
        bio_data['emp_id'] = new_employee_id
        biography = EmployeeBiography(**bio_data)
        session.add(biography)

        # Create employee salary record
        salary_data['emp_id'] = new_employee_id
        salary = EmployeeSalary(**salary_data)
        session.add(salary)

        # Create vehicle record if vehicle data provided
        if vehicle_data is not None:
            vehicle_data['emp_id'] = new_employee_id
            vehicle = EmployeeVehicle(**vehicle_data)
            session.add(vehicle)

        return new_employee_id

    def _update_existing_employee(self, session, employee_id, bio_data, salary_data, vehicle_data):
        """
        Update an existing employee record across all related tables.
        
        Updates biography information and creates or updates salary and
        vehicle records as needed.
        
        Args:
            session: Database session for transaction
            employee_id (int): ID of employee to update
            bio_data (dict): Updated biography information
            salary_data (dict): Updated salary information
            vehicle_data (dict or None): Updated vehicle information if applicable
        """
        # Update employee biography record
        biography = session.query(EmployeeBiography).filter_by(emp_id=employee_id).first()
        for key, value in bio_data.items():
            if key != 'employee_id':  # Skip the ID field
                setattr(biography, key, value)
        
        # Update or create salary record
        salary = session.query(EmployeeSalary).filter_by(emp_id=employee_id).first()
        if salary:
            # Update existing salary record
            for key, value in salary_data.items():
                setattr(salary, key, value)
        else:
            # Create new salary record
            salary_data['emp_id'] = employee_id
            new_salary = EmployeeSalary(**salary_data)
            session.add(new_salary)
        
        # Update or create vehicle record if vehicle data provided
        if vehicle_data is not None:
            vehicle = session.query(EmployeeVehicle).filter_by(emp_id=employee_id).first()
            if vehicle:
                # Update existing vehicle record
                for key, value in vehicle_data.items():
                    setattr(vehicle, key, value)
            else:
                # Create new vehicle record
                vehicle_data['emp_id'] = employee_id
                new_vehicle = EmployeeVehicle(**vehicle_data)
                session.add(new_vehicle)

    def delete_employee_record(self, employee_id):
        """
        Delete an employee record and all related information.
        
        Removes employee from database including biography, salary, and vehicle
        records. Uses cascade delete to ensure referential integrity.
        
        Args:
            employee_id (int): ID of employee to delete
            
        Raises:
            Exception: Database operation errors are re-raised after rollback
        """
        session = self.session
        
        try:
            # Find employee biography record
            biography = session.query(EmployeeBiography).filter_by(emp_id=employee_id).first()
            
            if biography:
                # Delete employee and cascade to related records
                session.delete(biography)
                session.commit()
                print(f"Deleted employee {employee_id} and all related records")
            else:
                print(f"Employee {employee_id} not found")
                
        except Exception as e:
            # Rollback transaction on error
            session.rollback()
            print(f"Error deleting employee: {e}")
            raise
        finally:
            # Always close the session
            session.close()

    def get_all_employee_complete_info(self):
        """
        Retrieve complete information for all employees.
        
        Joins employee biography and salary tables to provide comprehensive
        employee information in a single result set.
        
        Returns:
            pandas.DataFrame: Complete employee information or empty DataFrame on error
        """
        try:
            # SQL query to join biography and salary information
            query = """
            SELECT 
                b.`Employee Id`,
                CONCAT(b.`First Name`, ' ', b.`Last Name`) as `Full Name`,
                b.Gender,
                b.Age,
                b.birth_date as `Birth Date`,
                b.`Contact Number`,
                s.`Job Title`,
                s.Department,
                s.salary_yearly as `Yearly Salary`,
                s.salary_monthly as `Monthly Salary`,
                s.hire_date as `Hire Date`,
                s.`Years of Experience`,
                s.`Years of Experience (company)` as `Company Experience`,
                s.`Performance Rating`,
                s.bonus_amount as `Bonus Amount`,
                s.`Total Compensation`
            FROM hh_employee_biography b
            INNER JOIN hh_employee_salary s ON b.`Employee Id` = s.`Employee Id`
            ORDER BY b.`Employee Id`
            """
            
            return pd.read_sql(query, con=engine)
            
        except Exception as e:
            print(f"Error retrieving employee data: {e}")
            return pd.DataFrame()

    def get_employees_by_job_title(self, job_title="Delivery Driver"):
        """
        Retrieve employees filtered by job title.
        
        Returns different column sets based on job title - delivery drivers
        include vehicle information while other roles do not.
        
        Args:
            job_title (str): Job title to filter by (default: "Delivery Driver")
            
        Returns:
            pandas.DataFrame: Filtered employee information or empty DataFrame on error
        """
        try:
            if job_title.lower() == "delivery driver":
                # Include vehicle information for delivery drivers
                query = """
                SELECT 
                    b.`Employee Id`,
                    CONCAT(b.`First Name`, ' ', b.`Last Name`) as `Full Name`,
                    b.Gender,
                    b.Age,
                    s.`Job Title`,
                    s.Department,
                    s.salary_yearly as `Yearly Salary`,
                    v.unit_name as `Vehicle Unit`,
                    v.unit_brand as `Vehicle Brand`
                FROM hh_employee_biography b
                INNER JOIN hh_employee_salary s ON b.`Employee Id` = s.`Employee Id`
                LEFT JOIN hh_vehicle v ON b.`Employee Id` = v.`Employee Id`
                WHERE s.`Job Title` = %s
                ORDER BY b.`Employee Id`
                """
            else:
                # Standard information for non-delivery roles
                query = """
                SELECT 
                    b.`Employee Id`,
                    CONCAT(b.`First Name`, ' ', b.`Last Name`) as `Full Name`,
                    b.Gender,
                    b.Age,
                    s.`Job Title`,
                    s.Department,
                    s.salary_yearly as `Yearly Salary`
                FROM hh_employee_biography b
                INNER JOIN hh_employee_salary s ON b.`Employee Id` = s.`Employee Id`
                WHERE s.`Job Title` = %s
                ORDER BY b.`Employee Id`
                """

            return pd.read_sql(query, con=engine, params=[(job_title,)])

        except Exception as e:
            print(f"Error retrieving employees by job title: {e}")
            return pd.DataFrame()

    def get_employee_by_id(self, employee_id):
        """
        Retrieve detailed information for a specific employee by ID.
        
        Joins biography and salary tables to provide complete employee
        profile information.
        
        Args:
            employee_id (int): Employee ID to search for
            
        Returns:
            pandas.DataFrame: Employee information or empty DataFrame if not found/error
        """
        try:
            # SQL query to get complete employee information by ID
            query = """
            SELECT 
                b.*,
                s.`Job Title`, s.Department, s.salary_yearly, s.salary_monthly,
                s.hire_date, s.`Years of Experience`, s.`Years of Experience (company)`,
                s.`Performance Rating`, s.bonus_amount, s.`Total Compensation`
            FROM hh_employee_biography b
            INNER JOIN hh_employee_salary s ON b.`Employee Id` = s.`Employee Id`
            WHERE b.`Employee Id` = %s
            """
            
            return pd.read_sql(query, con=engine, params=[(employee_id,)])
            
        except Exception as e:
            print(f"Error retrieving employee {employee_id}: {e}")
            return pd.DataFrame()

    def get_vehicle_statistics(self):
        """
        Retrieve statistical information about company vehicles.
        
        Calculates aggregate statistics including counts, averages, and ranges
        for vehicle data to provide fleet overview.
        
        Returns:
            pandas.DataFrame: Vehicle statistics or empty DataFrame on error
        """
        try:
            # SQL query to calculate vehicle statistics
            query = """
            SELECT 
                COUNT(*) as `Total Vehicles`,
                ROUND(AVG(year), 0) as `Average Vehicle Year`,
                ROUND(AVG(km_driven), 0) as `Average KM Driven`,
                MIN(km_driven) as `Minimum KM Driven`,
                MAX(km_driven) as `Maximum KM Driven`,
                ROUND(AVG(max_weight - min_weight), 2) as `Average Weight Capacity`
            FROM hh_vehicle
            """
            
            return pd.read_sql(query, con=engine)
            
        except Exception as e:
            print(f"Error retrieving vehicle statistics: {e}")
            return pd.DataFrame()


# ==============================================================================
# USER INTERFACE FUNCTIONS
# ==============================================================================

def display_menu():
    """
    Display the main application menu with available options.
    
    Shows numbered menu options for all available system functions
    with clear descriptions of each operation.
    """
    print("\n" + "=" * 60)
    print("EMPLOYEE MANAGEMENT SYSTEM")
    print("=" * 60)
    print("1. Manage Employee Records")
    print("2. View All Employees")
    print("3. View Employees by Job Title")
    print("4. Search Employee by ID")
    print("5. View Vehicle Statistics")
    print("6. Delete Employee Record")
    print("7. Exit")
    print("-" * 60)


def handle_manage_employees(manager):
    """
    Handle employee management operations menu.
    
    Provides submenu for adding new employees or updating existing
    employee records with complete data validation.
    
    Args:
        manager (EmployeeManagement): Instance of employee management system
    """
    print("\nManage Employee Records:")
    print("1. Add New Employee")
    print("2. Update Existing Employee")
    
    choice = input("Select option (1-2): ").strip()

    if choice == '1':
        # Add new employee workflow
        bio_data, salary_data, vehicle_data = get_complete_employee_data()
        if bio_data and salary_data:
            manager.add_complete_employee_record(bio_data, salary_data, vehicle_data)
    elif choice == '2':
        # Update existing employee workflow
        bio_data, salary_data, vehicle_data = get_existing_employee_update_data()
        if bio_data and salary_data:
            manager.add_complete_employee_record(bio_data, salary_data, vehicle_data)
    else:
        print("Invalid option.")


def handle_view_all_employees(manager):
    """
    Retrieves and displays comprehensive employee information including
    biography, salary, and job details in tabular format.
    
    Args:
        manager (EmployeeManagement): Instance of employee management system
    """
    print("\nAll Employees:")
    employees_df = manager.get_all_employee_complete_info()
    
    if not employees_df.empty:
        print(employees_df.to_string(index=False))
    else:
        print("No employee records found.")


def handle_view_employees_by_job_title(manager):
    """
    Handle viewing employees filtered by job title.
    
    Prompts user for a job title and retrieves employees matching that title,
    displaying their information in a tabular format.
    
    Args:
        manager (EmployeeManagement): Instance of employee management system
    """
    job_title = input("Enter Job Title (default: Delivery Driver): ").strip() or "Delivery Driver"
    employees_df = manager.get_employees_by_job_title(job_title)
    
    if not employees_df.empty:
        print(employees_df.to_string(index=False))
    else:
        print(f"No employees found for job title: {job_title}")


def handle_search_employee_by_id(manager):
    """
    Handle searching for an employee by their ID.
    
    Prompts user for an employee ID and retrieves the corresponding employee
    information, displaying it in a readable format.
    
    Args:
        manager (EmployeeManagement): Instance of employee management system
    """
    employee_id = get_valid_integer("Enter Employee ID: ", min_val=1)
    employee_df = manager.get_employee_by_id(employee_id)
    
    if not employee_df.empty:
        print(employee_df.to_string(index=False))
    else:
        print(f"No employee found with ID: {employee_id}")


def handle_view_vehicle_statistics(manager):
    """
    Handle viewing statistics about company vehicles.
    
    Retrieves and displays aggregate statistics related to the company's
    vehicle fleet, including counts, averages, and ranges.
    
    Args:
        manager (EmployeeManagement): Instance of employee management system
    """
    vehicle_stats_df = manager.get_vehicle_statistics()
    
    if not vehicle_stats_df.empty:
        print(vehicle_stats_df.to_string(index=False))
    else:
        print("No vehicle statistics available.")


def handle_delete_employee_record(manager):
    """
    Handle deleting an employee record.
    
    Prompts user for an employee ID and deletes the corresponding employee
    record from the database, including all related information.
    
    Args:
        manager (EmployeeManagement): Instance of employee management system
    """
    employee_id = get_valid_integer("Enter Employee ID to delete: ", min_val=1)
    confirm = input(f"Are you sure you want to delete employee ID {employee_id}? (Y/N): ").strip().lower()
    
    if confirm == 'y':
        try:
            manager.delete_employee_record(employee_id)
        except Exception as e:
            print(f"Error deleting employee: {e}")
    else:
        print("Deletion cancelled.")


def main():
    """
    Main function to run the Employee Management System.
    
    Initializes the employee management system and provides a loop for
    user interaction through the menu options.
    """
    manager = EmployeeManagement()
    
    while True:
        display_menu()
        choice = input("Select an option (1-7): ").strip()
        
        if choice == '1':
            handle_manage_employees(manager)
        elif choice == '2':
            handle_view_all_employees(manager)
        elif choice == '3':
            handle_view_employees_by_job_title(manager)
        elif choice == '4':
            handle_search_employee_by_id(manager)
        elif choice == '5':
            handle_view_vehicle_statistics(manager)
        elif choice == '6':
            handle_delete_employee_record(manager)
        elif choice == '7':
            print("Exiting the Employee Management System. Goodbye!")
            break
        else:
            print("Invalid option. Please try again.")


if __name__ == "__main__":
    main()
