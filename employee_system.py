from mysql_connection import *


class EmployeeBiography(Base):
    __tablename__ = "hh_employee_biography"

    emp_id = Column("Employee Id", Integer, primary_key=True, nullable=False)
    fname = Column("First Name", String(100), nullable=False)
    lname = Column("Last Name", String(100), nullable=False)
    gender = Column("Gender", String(10), nullable=False)
    age = Column("Age", Integer, nullable=False)
    birthdate = Column("birth_date", Date, nullable=False)
    contact_num = Column("Contact Number", BigInteger, nullable=False)

    salary_info = relationship('EmployeeSalary', back_populates='employee', uselist=False, cascade="all, delete-orphan")
    vehicle_info = relationship('EmployeeVehicle', back_populates='employee', uselist=False, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Employee Biography: id={self.emp_id}, name={self.fname} {self.lname}>"

class EmployeeSalary(Base):
    __tablename__ = "hh_employee_salary"

    emp_id = Column("Employee Id", Integer, ForeignKey("hh_employee_biography.Employee Id"), primary_key=True, nullable=False)
    job_title = Column("Job Title", String(100), nullable=False)
    department = Column("Department", String(100), nullable=False)
    yearly_sal = Column("salary_yearly", Float, nullable=False)
    monthly_sal = Column("salary_monthly", Float, nullable=False)
    hire_date = Column("hire_date", Date, nullable=False)
    years_exp = Column("Years of Experience", Integer, nullable=False)
    years_exp_comp = Column("Years of Experience (company)", Float, nullable=False)
    rating = Column("Performance Rating", Integer, nullable=True)
    bonus = Column("bonus_amount", Float, nullable=False)
    compensation = Column("Total Compensation", Float, nullable=False)

    employee = relationship('EmployeeBiography', back_populates='salary_info', uselist=False)

    def __repr__(self):
        return f"<Employee Salary: id={self.emp_id}, job_title={self.job_title}, salary={self.yearly_sal}>"

class EmployeeVehicle(Base):
    __tablename__ = "hh_vehicle"

    emp_id = Column("Employee Id", Integer, ForeignKey("hh_employee_biography.Employee Id"), primary_key=True, nullable=False)
    unit_name = Column("unit_name", String(100), nullable=False)
    unit_brand = Column("unit_brand", String(100), nullable=False)
    year = Column("year", Integer, nullable=False)
    km_driven = Column("km_driven", Integer, nullable=False)
    min_weight = Column("min_weight", Float, nullable=False)
    max_weight = Column("max_weight", Float, nullable=False)

    employee = relationship('EmployeeBiography', back_populates='vehicle_info', uselist=False)

    def __repr__(self):
        return f"<Vehicle Driver: id={self.emp_id}, unit={self.unit_name}>"

class EmployeeManagement:
    def __init__(self):
        self.session = emp_session  # Use the existing session from mysql_connection

    def add_complete_employee_record(self, bio_data, salary_data, vehicle_data):
        session = self.session
        
        try:
            # Determine if this is a new employee or existing by presence of employee_id in bio_data
            employee_id = bio_data.get('employee_id')
            
            if employee_id is not None:
                existing_bio = session.query(EmployeeBiography).filter_by(emp_id=employee_id).first()
            else:
                existing_bio = None  # new employee
            
            if existing_bio:
                self._update_existing_employee(session, employee_id, bio_data, salary_data, vehicle_data)
                print(f"✅ Updated driver record for employee ID: {employee_id}")
            else:
                bio_data.pop('employee_id', None)
                new_employee_id = self._create_new_employee(session, bio_data, salary_data, vehicle_data)
                print(f"✅ Added new driver record with employee ID: {new_employee_id}")
            
            session.commit()
            
        except Exception as e:
            session.rollback()
            print(f"❌ Error managing driver record: {e}")
            raise
        finally:
            session.close()

    def _create_new_employee(self, session, bio_data, salary_data, vehicle_data):
        latest_employee_id = session.query(func.max(EmployeeBiography.emp_id)).scalar()
        if latest_employee_id is None:
            latest_employee_id = 0
        new_employee_id = latest_employee_id + 1

        bio_data['emp_id'] = new_employee_id
        biography = EmployeeBiography(**bio_data)
        session.add(biography)

        # Set emp_id for salary data
        salary_data['emp_id'] = new_employee_id
        salary = EmployeeSalary(**salary_data)
        session.add(salary)

        # Set emp_id for vehicle data if provided
        if vehicle_data is not None:
            vehicle_data['emp_id'] = new_employee_id
            vehicle = EmployeeVehicle(**vehicle_data)
            session.add(vehicle)

        return new_employee_id


    def _update_existing_employee(self, session, employee_id, bio_data, salary_data, vehicle_data):
        biography = session.query(EmployeeBiography).filter_by(emp_id=employee_id).first()
        for key, value in bio_data.items():
            if key != 'employee_id':
                setattr(biography, key, value)
        
        salary = session.query(EmployeeSalary).filter_by(emp_id=employee_id).first()
        if salary:
            for key, value in salary_data.items():
                setattr(salary, key, value)
        else:
            salary_data['emp_id'] = employee_id
            new_salary = EmployeeSalary(**salary_data)
            session.add(new_salary)
        
        if vehicle_data is not None:
            vehicle = session.query(EmployeeVehicle).filter_by(emp_id=employee_id).first()
            if vehicle:
                for key, value in vehicle_data.items():
                    setattr(vehicle, key, value)
            else:
                vehicle_data['emp_id'] = employee_id
                new_vehicle = EmployeeVehicle(**vehicle_data)
                session.add(new_vehicle)

    def delete_employee_record(self, employee_id):
        session = self.session
        
        try:
            biography = session.query(EmployeeBiography).filter_by(emp_id=employee_id).first()
            
            if biography:
                session.delete(biography)
                session.commit()
                print(f"✅ Deleted driver {employee_id} and all related records")
            else:
                print(f"⚠️ Employee {employee_id} not found")
                
        except Exception as e:
            session.rollback()
            print(f"❌ Error deleting employee: {e}")
            raise
        finally:
            session.close()
        
    def get_all_employee_complete_info(self):
        try:
            query = """
            SELECT 
                b.`Employee Id`,
                b.`First Name`,
                b.`Last Name`,
                b.Gender,
                b.Age,
                b.birth_date,
                b.`Contact Number`,
                s.`Job Title`,
                s.Department,
                s.salary_yearly,
                s.salary_monthly,
                s.hire_date,
                s.`Years of Experience`,
                s.`Years of Experience (company)`,
                s.`Performance Rating`,
                s.bonus_amount,
                s.`Total Compensation`
            FROM hh_employee_biography b
            INNER JOIN hh_employee_salary s ON b.`Employee Id` = s.`Employee Id`
            ORDER BY b.`Employee Id`
            """
            
            df = pd.read_sql(query, con=emp_engine)
            return df
            
        except Exception as e:
            print(f"❌ Error retrieving driver data: {e}")
            return pd.DataFrame()

    def get_all_employee_by_job_title(self, job_title="Delivery Driver"):
        try:
            if job_title == "Delivery Driver":
                query = """
                SELECT b.`Employee Id`,
                    CONCAT(b.`First Name`, ' ', b.`Last Name`) as full_name,
                    b.Gender,
                    b.Age,
                    s.`Job Title`,
                    s.Department,
                    s.salary_yearly,
                    v.unit_name,
                    v.unit_brand
                FROM hh_employee_biography b
                INNER JOIN hh_employee_salary s ON b.`Employee Id` = s.`Employee Id`
                LEFT JOIN hh_vehicle v ON b.`Employee Id` = v.`Employee Id`
                WHERE s.`Job Title` = %s
                ORDER BY b.`Employee Id`
                """
            else:
                query = """
                SELECT b.`Employee Id`,
                    CONCAT(b.`First Name`, ' ', b.`Last Name`) as full_name,
                    b.Gender,
                    b.Age,
                    s.`Job Title`,
                    s.Department,
                    s.salary_yearly
                FROM hh_employee_biography b
                INNER JOIN hh_employee_salary s ON b.`Employee Id` = s.`Employee Id`
                WHERE s.`Job Title` = %s
                ORDER BY b.`Employee Id`
                """

            # ✅ Use a list/tuple of values
            df = pd.read_sql(query, con=emp_engine, params=[(job_title,)])
            return df

        except Exception as e:
            print(f"Error retrieving employees by job title: {e}")
            return pd.DataFrame()

    def get_employee_by_id(self, employee_id):
        try:
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
            
            df = pd.read_sql(query, con=emp_engine, params=[(employee_id,)])
            return df
            
        except Exception as e:
            print(f"❌ Error retrieving driver {employee_id}: {e}")
            return pd.DataFrame()

    def get_vehicle_statistics(self):
        try:
            query = """
            SELECT 
                COUNT(*) as total_vehicles,
                AVG(year) as avg_vehicle_year,
                AVG(km_driven) as avg_km_driven,
                MIN(km_driven) as min_km_driven,
                MAX(km_driven) as max_km_driven,
                AVG(max_weight - min_weight) as avg_weight_capacity
            FROM hh_vehicle
            """
            
            df = pd.read_sql(query, con=emp_engine)
            return df
            
        except Exception as e:
            print(f"❌ Error retrieving vehicle statistics: {e}")
            return pd.DataFrame()

def get_valid_date(prompt="Enter date (YYYY-MM-DD): "):
    while True:
        try:
            return datetime.strptime(input(prompt).strip(), "%Y-%m-%d").date()
        except ValueError:
            print("Invalid format. Use YYYY-MM-DD.")

def get_vehicle_data(job_title):
    if job_title != "Delivery Driver":
        return None

    print("\nEnter Updated Employee Vehicle Information:")
    unit_name = input("Enter delivery vehicle unit: ").strip().title()
    unit_brand = input("Enter unit brand: ").strip().title()
    year = int(input("Enter unit year: "))
    km_driven = int(input("Enter unit's kilometer/s driven: "))

    weight_map = {
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
    min_weight, max_weight = weight_map.get(unit_name, (0, 0))

    return {
        'unit_name': unit_name,
        'unit_brand': unit_brand,
        'year': year,
        'km_driven': km_driven,
        'min_weight': min_weight,
        'max_weight': max_weight
    }

def get_new_employee_data():
    try:
        print("\nEnter Updated Employee Biography Information:")
        fname = input("Enter employee first name: ").strip().title()
        lname = input("Enter employee last name: ").strip().title()
        gender = input("Enter employee gender (Male/Female): ").strip().title()
        age = int(input("Enter employee age: "))
        birth_date = get_valid_date("Enter employee birthdate (YYYY-MM-DD): ")
        contact_number = int(input("Enter employee contact number (e.g. 9547977563): "))

        bio_data = {
            'fname': fname,
            'lname': lname,
            'gender': gender,
            'age': age,
            'birthdate': birth_date,
            'contact_num': contact_number
        }

        print("\nEnter Updated Employee Salary Information:")
        job_title = input("Enter employee job title: ").strip().title()
        department = input("Enter employee department: ").strip().title()
        salary_yearly = float(input("Enter employee yearly salary: "))
        salary_monthly = round(salary_yearly / 12, 2)
        hire_date = get_valid_date("Enter employee hire date (YYYY-MM-DD): ")
        years_of_exp = int(input("Enter total years of experience: "))
        years_of_exp_comp = int(input("Enter years of experience in the company: "))
        rating = int(input("Enter employee performance rating (1-5): "))
        while rating not in range(1, 6):
            print("Rating must be between 1-5.")
            rating = int(input("Enter employee performance rating (1-5): "))
        bonus_amount = float(input("Enter employee bonus amount: "))
        total_compensation = round(salary_yearly + bonus_amount, 2)

        salary_data = {
            'job_title': job_title,
            'department': department,
            'yearly_sal': salary_yearly,
            'monthly_sal': salary_monthly,
            'hire_date': hire_date,
            'years_exp': years_of_exp,
            'years_exp_comp': years_of_exp_comp,
            'rating': rating,
            'bonus': bonus_amount,
            'compensation': total_compensation
        }

        vehicle_data = get_vehicle_data(job_title)
        return bio_data, salary_data, vehicle_data

    except ValueError as e:
        print(f"\u274c Invalid input format: {e}")
        return None, None, None


def existing_employee_data():
    while True:
        try:
            employee_id = int(input("Enter Employee ID: "))
        except ValueError:
            print("Invalid input. Please enter a valid integer for Employee ID.")
            continue

        emp = emp_session.query(EmployeeBiography).filter_by(emp_id=employee_id).first()

        if not emp:
            print("Employee not found. Please try again.")
            continue

        print("\nIs this the employee you wish to review?")
        print(emp)
        confirm = input("(Y) for Yes, (N) for No: ").strip().lower()

        if confirm == 'y':
            bio_data, salary_data, vehicle_data = get_new_employee_data()
            if bio_data is not None:
                bio_data['employee_id'] = employee_id
            return bio_data, salary_data, vehicle_data

def display_menu():
    print("\n" + "=" * 60)
    print("🚛 DRIVER EMPLOYEE MANAGEMENT SYSTEM")
    print("=" * 60)
    print("1. Manage Employee Records")
    print("2. View All Employees")
    print("3. View Employees by Job Title")
    print("4. Search Employee by ID")
    print("5. View Vehicle Statistics")
    print("6. Delete Employee (Complete Record)")
    print("7. Exit")
    print("-" * 60)

def main():
    print("🚀 Starting Employee Management System...")

    manager = EmployeeManagement()

    # # Predefined weight_map for vehicle capacities
    # weight_map = {
    #     'Honda Civic': (25, 350),
    #     'MG 5': (25, 350),
    #     'Toyota Vios': (20, 300),
    #     'Yamaha Mio Sporty': (0.1, 20),
    #     'Yamaha NMAX': (25, 80),
    #     'Honda Click 125i': (0.1, 25),
    #     'Mitsubishi Fuso Fighter': (3000, 7000),
    #     'Hino 700 Series Dump Truck': (7000, 15000),
    #     'Isuzu ELF NHR 55': (350, 3000),
    # }

    # # Sample data using vehicle unit_name from weight_map only
    # sample_employees = [
    #     {
    #         'bio': {
    #             'fname': 'John',
    #             'lname': 'Smith',
    #             'gender': 'Male',
    #             'age': 35,
    #             'birthdate': datetime.strptime('1987-03-15', "%Y-%m-%d").date(),
    #             'contact_num': 1234567890
    #         },
    #         'salary': {
    #             'job_title': 'Driver',
    #             'department': 'Transportation',
    #             'yearly_sal': 45000.00,
    #             'monthly_sal': 3750.00,
    #             'hire_date': datetime.strptime('2020-01-15', "%Y-%m-%d").date(),
    #             'years_exp': 10,
    #             'years_exp_comp': 4.5,
    #             'rating': 8,
    #             'bonus': 2000.00,
    #             'compensation': 47000.00
    #         },
    #         'vehicle': {
    #             'unit_name': 'Honda Civic',
    #             'unit_brand': 'Honda',
    #             'year': 2019,
    #             'km_driven': 85000,
    #             'min_weight': weight_map['Honda Civic'][0],
    #             'max_weight': weight_map['Honda Civic'][1]
    #         }
    #     },
    #     {
    #         'bio': {
    #             'fname': 'Maria',
    #             'lname': 'Garcia',
    #             'gender': 'Female',
    #             'age': 29,
    #             'birthdate': datetime.strptime('1993-07-22', "%Y-%m-%d").date(),
    #             'contact_num': 9876543210
    #         },
    #         'salary': {
    #             'job_title': 'Senior Driver',
    #             'department': 'Transportation',
    #             'yearly_sal': 52000.00,
    #             'monthly_sal': 4333.33,
    #             'hire_date': datetime.strptime('2019-06-10', "%Y-%m-%d").date(),
    #             'years_exp': 8,
    #             'years_exp_comp': 5.2,
    #             'rating': 9,
    #             'bonus': 3000.00,
    #             'compensation': 55000.00
    #         },
    #         'vehicle': {
    #             'unit_name': 'Mitsubishi Fuso Fighter',
    #             'unit_brand': 'Mitsubishi',
    #             'year': 2021,
    #             'km_driven': 45000,
    #             'min_weight': weight_map['Mitsubishi Fuso Fighter'][0],
    #             'max_weight': weight_map['Mitsubishi Fuso Fighter'][1]
    #         }
    #     }
    # ]

    # print("\n📋 Adding sample employee data...")
    # for emp in sample_employees:
    #     manager.add_complete_employee_record(emp['bio'], emp['salary'], emp['vehicle'])

    while True:
        display_menu()
        choice = input("Select an option (1-7): ").strip()

        if choice == '1':
            print("\n📝 Manage Employee Records:")
            print("1. Add New Employee (Complete Record)")
            print("2. Update Existing Employee (Complete Record)")
            manage_choice = input("Select an option (1-2): ").strip()

            if manage_choice == '1':
                bio_data, salary_data, vehicle_data = get_new_employee_data()
                if bio_data and salary_data:
                    manager.add_complete_employee_record(bio_data, salary_data, vehicle_data)
            elif manage_choice == '2':
                bio_data, salary_data, vehicle_data = existing_employee_data()
                if bio_data and salary_data:
                    manager.add_complete_employee_record(bio_data, salary_data, vehicle_data)
            else:
                print("❌ Invalid option. Please try again.")

        elif choice == '2':
            print("\n📊 All Employees (Complete Information):")
            df = manager.get_all_employee_complete_info()
            if not df.empty:
                print(df.to_string(index=False))
            else:
                print("No employees found.")

        elif choice == '3':
            job_title = input("Enter job title (default: Delivery Driver): ").strip().title()
            if not job_title:
                job_title = "Delivery Driver"
            print(f"\n👥 Employees with job title '{job_title}':")
            df = manager.get_all_employee_by_job_title(job_title)
            if not df.empty:
                print(df.to_string(index=False))
            else:
                print(f"No employees found with job title '{job_title}'.")

        elif choice == '4':
            try:
                emp_id = int(input("Enter Employee ID to search: "))
                df = manager.get_employee_by_id(emp_id)
                if not df.empty:
                    print(f"\n👤 Employee {emp_id} Complete Information:")
                    for col in df.columns:
                        print(f"{col}: {df.iloc[0][col]}")
                else:
                    print(f"Employee {emp_id} not found.")
            except ValueError:
                print("❌ Please enter a valid employee ID.")

        elif choice == '5':
            print("\n📈 Vehicle Statistics:")
            df = manager.get_vehicle_statistics()
            if not df.empty:
                print(df.to_string(index=False))
            else:
                print("No vehicle data found.")

        elif choice == '6':
            try:
                emp_id = int(input("Enter Employee ID to delete: "))
                confirm = input(f"Are you sure you want to delete employee {emp_id} and ALL related records? (y/N): ").strip().lower()
                if confirm == 'y':
                    manager.delete_employee_record(emp_id)
            except ValueError:
                print("❌ Please enter a valid employee ID.")

        elif choice == '7':
            print("👋 Goodbye!")
            break

        else:
            print("❌ Invalid option. Please try again.")

if __name__ == "__main__":
    main()
