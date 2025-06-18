from mysql_connection import *


# ==============================================================================
# DATABASE MODELS
# ==============================================================================

class EmployeeBiography(Base):
    """Database model for employee biography information."""
    
    __tablename__ = "hh_employee_biography"

    emp_id = Column("employee_id", Integer, primary_key=True, nullable=False) 
    fname = Column("first_name", String(100), nullable=False)
    lname = Column("last_name", String(100), nullable=False) 
    gender = Column("gender", String(10), nullable=False)  
    age = Column("age", Integer, nullable=False) 
    birthdate = Column("birth_date", Date, nullable=False)
    contact_num = Column("contact_number", BigInteger, nullable=False) 
    job_title = Column("job_title", String(100), nullable=False) 
    department = Column("department", String(100), nullable=False)

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
        return f"<Employee Biography: id={self.emp_id}, name={self.fname} {self.lname}, job={self.job_title}>"


class EmployeeSalary(Base):
    """Database model for employee salary and job information."""
    
    __tablename__ = "hh_employee_salary"

    emp_id = Column("employee_id", Integer, ForeignKey("hh_employee_biography.employee_id"), primary_key=True, nullable=False)
    job_title = Column("job_title", String(100), nullable=False) 
    department = Column("department", String(100), nullable=False) 
    hire_date = Column("hire_date", Date, nullable=False)
    years_exp = Column("years_experience", Integer, nullable=False)  
    years_exp_comp = Column("years_experience_company", Float, nullable=False)
    yearly_sal = Column("salary_yearly", Float, nullable=False)
    monthly_sal = Column("salary_monthly", Float, nullable=False)
    bonus = Column("bonus_amount", Float, nullable=False)
    compensation = Column("total_compensation", Float, nullable=False)
    rating = Column("performance_rating", Integer, nullable=True)  

    employee = relationship('EmployeeBiography', back_populates='salary_info', uselist=False)

    def __repr__(self):
        return f"<Employee Salary: id={self.emp_id}, job_title={self.job_title}, salary={self.yearly_sal}>"


class EmployeeVehicle(Base):
    """Database model for employee vehicle information."""
    
    __tablename__ = "hh_vehicle"

    emp_id = Column("employee_id", Integer, ForeignKey("hh_employee_biography.employee_id"), primary_key=True, nullable=False)
    unit_name = Column("unit_name", String(100), nullable=False)
    unit_brand = Column("unit_brand", String(100), nullable=False)
    year = Column("year", Integer, nullable=False)
    km_driven = Column("km_driven", Integer, nullable=False)
    min_weight = Column("min_weight", Float, nullable=False)
    max_weight = Column("max_weight", Float, nullable=False)

    employee = relationship('EmployeeBiography', back_populates='vehicle_info', uselist=False)

    def __repr__(self):
        return f"<Vehicle Driver: id={self.emp_id}, unit={self.unit_name}>"


# ==============================================================================
# CONFIGURATION CONSTANTS
# ==============================================================================

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

PERFORMANCE_RATING_RANGE = (1, 5)
DATE_FORMAT = "%Y-%m-%d"
MIN_EMPLOYEE_AGE = 16
MAX_EMPLOYEE_AGE = 70
MIN_CONTACT_NUMBER = 1000000000
MAX_CONTACT_NUMBER = 99999999999


# ==============================================================================
# UTILITY FUNCTIONS
# ==============================================================================

def get_valid_date(prompt="Enter date (YYYY-MM-DD): "):
    while True:
        try:
            date_str = input(prompt).strip()
            return datetime.strptime(date_str, DATE_FORMAT).date()
        except ValueError:
            print(f"Invalid format. Please use {DATE_FORMAT} format.")


def calculate_age(birthdate):
    """Calculate age from birthdate to current date."""
    today = datetime.now().date()
    age = today.year - birthdate.year
    
    # Adjust if birthday hasn't occurred this year yet
    if today.month < birthdate.month or (today.month == birthdate.month and today.day < birthdate.day):
        age -= 1
    
    return age


def validate_birthdate_and_age():
    """Get birthdate and validate the calculated age is within acceptable range."""
    while True:
        birthdate = get_valid_date("Birthdate (YYYY-MM-DD): ")
        calculated_age = calculate_age(birthdate)
        
        if calculated_age < MIN_EMPLOYEE_AGE:
            print(f"Employee must be at least {MIN_EMPLOYEE_AGE} years old. Calculated age: {calculated_age}")
            continue
        elif calculated_age > MAX_EMPLOYEE_AGE:
            print(f"Employee must be at most {MAX_EMPLOYEE_AGE} years old. Calculated age: {calculated_age}")
            continue
        
        print(f"Calculated age: {calculated_age} years")
        return birthdate, calculated_age


def get_valid_integer(prompt, min_val=None, max_val=None):
    while True:
        try:
            value = int(input(prompt))
            if min_val is not None and value < min_val:
                print(f"Value must be at least {min_val}.")
                continue
            if max_val is not None and value > max_val:
                print(f"Value must be at most {max_val}.")
                continue
            return value
        except ValueError:
            print("Please enter a valid integer.")


def get_valid_float(prompt, min_val=None):
    while True:
        try:
            value = float(input(prompt))
            if min_val is not None and value < min_val:
                print(f"Value must be at least {min_val}.")
                continue
            return value
        except ValueError:
            print("Please enter a valid number.")


def calculate_monthly_salary(yearly_salary):
    return round(yearly_salary / 12, 2)


def calculate_total_compensation(yearly_salary, bonus):
    return round(yearly_salary + bonus, 2)


def validate_gender_input():
    while True:
        gender = input("Gender (Male/Female): ").strip().title()
        if gender in ['Male', 'Female']:
            return gender
        print("Please enter 'Male' or 'Female'.")


def validate_vehicle_unit():
    print("Available vehicles:")
    for i, vehicle in enumerate(VEHICLE_WEIGHT_MAP.keys(), 1):
        print(f"{i}. {vehicle}")
    
    while True:
        unit_name = input("Vehicle unit name: ").strip().title()
        if unit_name == 'Mg 5':
                unit_name = 'MG 5'
        if unit_name == 'Isuzu Elf Nhr 55':
                unit_name = 'Isuzu ELF NHR 55'
        if unit_name == 'Yamaha Nmax':
                unit_name = 'Yamaha NMAX'
        if unit_name == 'Honda Click 125I':
                unit_name = 'Honda Click 125i'
        if unit_name in VEHICLE_WEIGHT_MAP:
            return unit_name
        print(f"Vehicle '{unit_name}' not found in available options.")


# ==============================================================================
# DATA INPUT COLLECTION FUNCTIONS
# ==============================================================================

def get_employee_biography_data():
    print("\nEnter Employee Biography Information:")
    print("-" * 40)
    
    fname = input("First name: ").strip().title()
    lname = input("Last name: ").strip().title()
    gender = validate_gender_input()
    
    # Get birthdate and automatically calculate age
    birthdate, age = validate_birthdate_and_age()
    
    contact_num = get_valid_integer(
        "Contact number: ", 
        min_val=MIN_CONTACT_NUMBER, 
        max_val=MAX_CONTACT_NUMBER
    )
    
    # Get job information (now part of biography)
    job_title = input("Job title: ").strip().title()
    department = input("Department: ").strip().title()

    return {
        'fname': fname,
        'lname': lname,
        'gender': gender,
        'age': age,
        'birthdate': birthdate,
        'contact_num': contact_num,
        'job_title': job_title,
        'department': department
    }


def get_employee_salary_data():
    print("\nEnter Employee Salary Information:")
    print("-" * 40)
    
    yearly_salary = get_valid_float("Yearly salary: ", min_val=0)
    monthly_salary = calculate_monthly_salary(yearly_salary)
    hire_date = get_valid_date("Hire date (YYYY-MM-DD): ")
    years_exp = get_valid_integer("Total years of experience: ", min_val=0)
    years_exp_comp = get_valid_float("Years of experience in company: ", min_val=0)
    rating = get_valid_integer(
        f"Performance rating ({PERFORMANCE_RATING_RANGE[0]}-{PERFORMANCE_RATING_RANGE[1]}): ",
        min_val=PERFORMANCE_RATING_RANGE[0],
        max_val=PERFORMANCE_RATING_RANGE[1]
    )
    bonus_amount = get_valid_float("Bonus amount: ", min_val=0)
    total_compensation = calculate_total_compensation(yearly_salary, bonus_amount)

    return {
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
    if job_title.lower() != "delivery driver":
        return None

    print("\nEnter Employee Vehicle Information:")
    print("-" * 40)
    
    unit_name = validate_vehicle_unit()
    unit_brand = input("Unit brand: ").strip().title()
    current_year = datetime.now().year
    year = get_valid_integer("Vehicle year: ", min_val=1990, max_val=current_year + 1)
    km_driven = get_valid_integer("Kilometers driven: ", min_val=0)
    min_weight, max_weight = VEHICLE_WEIGHT_MAP[unit_name]

    return {
        'unit_name': unit_name,
        'unit_brand': unit_brand,
        'year': year,
        'km_driven': km_driven,
        'min_weight': min_weight,
        'max_weight': max_weight
    }


def get_complete_employee_data():
    try:
        bio_data = get_employee_biography_data()
        salary_data = get_employee_salary_data()
        
        # Add job_title and department to salary_data to maintain synchronization
        salary_data['job_title'] = bio_data['job_title']
        salary_data['department'] = bio_data['department']
        
        vehicle_data = get_employee_vehicle_data(bio_data['job_title'])
        return bio_data, salary_data, vehicle_data
    except (ValueError, KeyboardInterrupt) as e:
        print(f"Data input cancelled or invalid: {e}")
        return None, None, None


def get_existing_employee_update_data():
    while True:
        employee_id = get_valid_integer("Enter Employee ID: ", min_val=1)
        emp = session.query(EmployeeBiography).filter_by(emp_id=employee_id).first()
        
        if not emp:
            print("Employee not found. Please try again.")
            continue

        print(f"\nFound employee: {emp}")
        confirm = input("Update this employee? (Y/N): ").strip().lower()

        if confirm == 'y':
            bio_data, salary_data, vehicle_data = get_complete_employee_data()
            if bio_data is not None:
                bio_data['employee_id'] = employee_id
            return bio_data, salary_data, vehicle_data
        else:
            return None, None, None


# ==============================================================================
# MAIN EMPLOYEE MANAGEMENT CLASS
# ==============================================================================

class EmployeeManagement:
    def __init__(self):
        self.session = session

    def _delete_from_csv(self, file_path, emp_id, key='Employee Id'):
        try:
            if not os.path.exists(file_path):
                print(f"CSV file {file_path} does not exist, skipping deletion.")
                return
                
            # Read the CSV file
            df = pd.read_csv(file_path)
            
            # Check if the key column exists
            if key not in df.columns:
                print(f"Column '{key}' not found in {file_path}. Available columns: {list(df.columns)}")
                return
            
            # Check if the employee ID exists in the file
            if emp_id not in df[key].values:
                print(f"Employee ID {emp_id} not found in {file_path}")
                return
            
            # Filter out the record with matching employee ID
            original_count = len(df)
            df = df[df[key] != emp_id]
            new_count = len(df)
            
            # Save the updated dataframe
            df.to_csv(file_path, index=False)
            print(f"Successfully removed employee {emp_id} from {file_path} ({original_count} -> {new_count} records)")
            
        except Exception as e:
            print(f"Error deleting from CSV file {file_path}: {e}")
            traceback.print_exc()

    def _write_to_csv(self, bio_data, salary_data, vehicle_data, is_update):
        """Write data to CSV files with proper field name mapping."""
        
        # Updated bio_mapping to include job_title and department
        bio_mapping = {
            'emp_id': 'Employee Id',
            'fname': 'First Name',
            'lname': 'Last Name',
            'gender': 'Gender',
            'age': 'Age',
            'birthdate': 'birth_date',
            'contact_num': 'Contact Number',
            'job_title': 'Job Title',
            'department': 'Department'
        }

        salary_mapping = {
            'emp_id': 'Employee Id',
            'job_title': 'Job Title',
            'department': 'Department',
            'yearly_sal': 'salary_yearly',
            'monthly_sal': 'salary_monthly',
            'hire_date': 'hire_date',
            'years_exp': 'Years of Experience',
            'years_exp_comp': 'Years of Experience (company)',
            'rating': 'Performance Rating',
            'bonus': 'bonus_amount',
            'compensation': 'Total Compensation'
        }

        vehicle_mapping = {
            'emp_id': 'Employee Id',
            'unit_name': 'unit_name',
            'unit_brand': 'unit_brand',
            'year': 'year',
            'km_driven': 'km_driven',
            'min_weight': 'min_weight',
            'max_weight': 'max_weight'
        }

        def transform_data(data, mapping):
            if data is None:
                return None
            
            transformed = {}
            for internal_key, value in data.items():
                csv_key = mapping.get(internal_key, internal_key)
                transformed[csv_key] = value
            
            return transformed

        bio_data_csv = transform_data(bio_data, bio_mapping)
        salary_data_csv = transform_data(salary_data, salary_mapping)
        vehicle_data_csv = transform_data(vehicle_data, vehicle_mapping) if vehicle_data else None

        self._update_csv_file('hexahaul_db/hh_employee_biography.csv', bio_data_csv, is_update, key='Employee Id')
        self._update_csv_file('hexahaul_db/hh_employee_salary.csv', salary_data_csv, is_update, key='Employee Id')
        if vehicle_data_csv:
            self._update_csv_file('hexahaul_db/hh_vehicle.csv', vehicle_data_csv, is_update, key='Employee Id')

    def _update_csv_file(self, file_path, data_dict, is_update, key='Employee Id'):
        """Update CSV file with proper error handling."""
        import os
        import pandas as pd
        
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        if data_dict is None:
            print(f"Warning: No data provided for {file_path}")
            return

        if key not in data_dict:
            print(f"Error: '{key}' is missing from data_dict: {data_dict}")
            raise ValueError(f"'{key}' is required in data_dict for CSV update")

        try:
            if os.path.exists(file_path):
                df = pd.read_csv(file_path)
                if is_update:
                    df = df[df[key] != data_dict[key]]
                df = pd.concat([df, pd.DataFrame([data_dict])], ignore_index=True)
            else:
                df = pd.DataFrame([data_dict])

            df.to_csv(file_path, index=False)
            
        except Exception as e:
            print(f"Error updating CSV file {file_path}: {e}")
            raise

    def add_complete_employee_record(self, bio_data, salary_data, vehicle_data):
        session = self.session

        try:
            employee_id = bio_data.get('employee_id')
            if employee_id is not None:
                existing_bio = session.query(EmployeeBiography).filter_by(emp_id=employee_id).first()
            else:
                existing_bio = None

            if existing_bio:
                self._update_existing_employee(session, employee_id, bio_data, salary_data, vehicle_data)
                print(f"Updated employee record for ID: {employee_id}")
                is_update = True
                bio_data['emp_id'] = employee_id
                salary_data['emp_id'] = employee_id
                if vehicle_data:
                    vehicle_data['emp_id'] = employee_id
            else:
                bio_data.pop('employee_id', None)
                new_employee_id = self._create_new_employee(session, bio_data, salary_data, vehicle_data)
                print(f"Added new employee record with ID: {new_employee_id}")
                is_update = False

            session.commit()
            self._write_to_csv(bio_data, salary_data, vehicle_data, is_update)

        except Exception as e:
            session.rollback()
            print(f"Error managing employee record: {e}")
            raise
        finally:
            session.close()

    def _create_new_employee(self, session, bio_data, salary_data, vehicle_data):
        latest_id = session.query(func.max(EmployeeBiography.emp_id)).scalar() or 0
        new_employee_id = latest_id + 1

        bio_data['emp_id'] = new_employee_id
        biography = EmployeeBiography(**bio_data)
        session.add(biography)

        salary_data['emp_id'] = new_employee_id
        # Ensure job_title and department are synced in salary data
        salary_data['job_title'] = bio_data['job_title']
        salary_data['department'] = bio_data['department']
        salary = EmployeeSalary(**salary_data)
        session.add(salary)

        if vehicle_data is not None:
            vehicle_data['emp_id'] = new_employee_id
            vehicle = EmployeeVehicle(**vehicle_data)
            session.add(vehicle)

        return new_employee_id

    def _update_existing_employee(self, session, employee_id, bio_data, salary_data, vehicle_data):
        try:
            # Update employee biography record
            biography = session.query(EmployeeBiography).filter_by(emp_id=employee_id).first()
            
            if not biography:
                raise ValueError(f"Employee with ID {employee_id} not found")
            
            # Update biography fields
            for key, value in bio_data.items():
                if key not in ['emp_id', 'employee_id']:
                    if hasattr(biography, key):
                        setattr(biography, key, value)
            
            # Update or create salary record
            salary = session.query(EmployeeSalary).filter_by(emp_id=employee_id).first()
            if salary:
                for key, value in salary_data.items():
                    if key != 'emp_id':
                        if hasattr(salary, key):
                            setattr(salary, key, value)
                # Ensure job_title and department are synced
                salary.job_title = bio_data['job_title']
                salary.department = bio_data['department']
            else:
                salary_data_copy = salary_data.copy()
                salary_data_copy['emp_id'] = employee_id
                # Ensure job_title and department are synced
                salary_data_copy['job_title'] = bio_data['job_title']
                salary_data_copy['department'] = bio_data['department']
                new_salary = EmployeeSalary(**salary_data_copy)
                session.add(new_salary)
            
            # Handle vehicle record
            existing_vehicle = session.query(EmployeeVehicle).filter_by(emp_id=employee_id).first()
            
            if vehicle_data is not None:
                # Vehicle data provided - update or create vehicle record
                if existing_vehicle:
                    for key, value in vehicle_data.items():
                        if key != 'emp_id':
                            if hasattr(existing_vehicle, key):
                                setattr(existing_vehicle, key, value)
                else:
                    vehicle_data_copy = vehicle_data.copy()
                    vehicle_data_copy['emp_id'] = employee_id
                    new_vehicle = EmployeeVehicle(**vehicle_data_copy)
                    session.add(new_vehicle)
            else:
                # No vehicle data provided - remove existing vehicle record if present
                if existing_vehicle:
                    # Delete from database first
                    session.delete(existing_vehicle)
                    session.flush()  # Ensure database deletion happens
                    print(f"Removed vehicle record for employee {employee_id} from database")
                    
                    # Now delete from CSV 
                    try:
                        self._delete_from_csv('hexahaul_db/hh_vehicle.csv', employee_id, key='Employee Id')
                    except Exception as csv_error:
                        print(f"Warning: Could not remove vehicle CSV record for employee {employee_id}: {csv_error}")

            session.flush()
            
        except Exception as e:
            print(f"Error in _update_existing_employee: {e}")
            raise

    def delete_employee_record(self, employee_id):
        """Delete an employee record and all related information."""
        session = self.session
        
        try:
            biography = session.query(EmployeeBiography).filter_by(emp_id=employee_id).first()
            
            if biography:
                session.delete(biography)
                session.commit()
                print(f"Deleted employee {employee_id} and all related records from database")

                # Delete from all CSV files
                self._delete_from_csv('hexahaul_db/hh_employee_biography.csv', employee_id)
                self._delete_from_csv('hexahaul_db/hh_employee_salary.csv', employee_id)
                self._delete_from_csv('hexahaul_db/hh_vehicle.csv', employee_id)

            else:
                print(f"Employee {employee_id} not found")
                
        except Exception as e:
            session.rollback()
            print(f"Error deleting employee: {e}")
            raise
        finally:
            session.close()

    def get_all_employees_summary(self):
        try:
            query = """
            SELECT 
                b.employee_id, 
                CONCAT(b.first_name, ' ', b.last_name) as `Full Name`,
                b.job_title,  
                b.department, 
                s.salary_yearly as `Yearly Salary`
            FROM hh_employee_biography b
            INNER JOIN hh_employee_salary s ON b.employee_id = s.employee_id
            ORDER BY b.employee_id 
            """
            
            return pd.read_sql(query, con=engine)
            
        except Exception as e:
            print(f"Error retrieving employee data: {e}")
            return pd.DataFrame()


# ==============================================================================
# SIMPLIFIED USER INTERFACE
# ==============================================================================

def display_menu():
    """Display the simplified main menu with 4 options."""
    print("\n" + "=" * 50)
    print("EMPLOYEE MANAGEMENT SYSTEM")
    print("=" * 50)
    print("1. Add Employee")
    print("2. Update Employee") 
    print("3. Delete Employee")
    print("4. Exit")
    print("-" * 50)


def handle_add_employee(manager):
    """Handle adding a new employee."""
    print("\n--- ADD NEW EMPLOYEE ---")
    bio_data, salary_data, vehicle_data = get_complete_employee_data()
    if bio_data and salary_data:
        try:
            manager.add_complete_employee_record(bio_data, salary_data, vehicle_data)
            print("Employee added successfully!")
        except Exception as e:
            print(f"Error adding employee: {e}")
    else:
        print("Employee addition cancelled.")


def handle_update_employee(manager):
    """Handle updating an existing employee."""
    print("\n--- UPDATE EMPLOYEE ---")
    
    # First show current employees
    employees_df = manager.get_all_employees_summary()
    if not employees_df.empty:
        print("\nCurrent Employees:")
        print(employees_df.to_string(index=False))
        print()
    
    bio_data, salary_data, vehicle_data = get_existing_employee_update_data()
    if bio_data and salary_data:
        try:
            manager.add_complete_employee_record(bio_data, salary_data, vehicle_data)
            print("Employee updated successfully!")
        except Exception as e:
            print(f"Error updating employee: {e}")
    else:
        print("Employee update cancelled.")


def handle_delete_employee(manager):
    """Handle deleting an employee."""
    print("\n--- DELETE EMPLOYEE ---")
    
    # First show current employees
    employees_df = manager.get_all_employees_summary()
    if employees_df.empty:
        print("No employees found.")
        return
        
    print("\nCurrent Employees:")
    print(employees_df.to_string(index=False))
    print()
    
    employee_id = get_valid_integer("Enter Employee ID to delete: ", min_val=1)
    
    # Check if employee exists
    employee_exists = employee_id in employees_df['employee_id'].values
    if not employee_exists:
        print(f"Employee with ID {employee_id} not found.")
        return
    
    # Show employee details
    employee_info = employees_df[employees_df['employee_id'] == employee_id]
    print(f"\nEmployee to delete:")
    print(employee_info.to_string(index=False))
    
    confirm = input(f"\nAre you sure you want to delete this employee? (Y/N): ").strip().lower()
    
    if confirm == 'y':
        try:
            manager.delete_employee_record(employee_id)
            print("Employee deleted successfully!")
        except Exception as e:
            print(f"Error deleting employee: {e}")
    else:
        print("Deletion cancelled.")


def main():
    """Main function with simplified 4-option menu."""
    print("Initializing Employee Management System...")
    manager = EmployeeManagement()
    
    while True:
        display_menu()
        choice = input("Select an option (1-4): ").strip()
        
        if choice == '1':
            handle_add_employee(manager)
        elif choice == '2':
            handle_update_employee(manager)
        elif choice == '3':
            handle_delete_employee(manager)
        elif choice == '4':
            print("Exiting Employee Management System. Goodbye!")
            break
        else:
            print("Invalid option. Please select 1, 2, 3, or 4.")


if __name__ == "__main__":
    main()