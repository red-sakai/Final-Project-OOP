"""
TO DO LIST:
1. Implement logic of:
   - database class
   - utilities class
2. Connect back-end to front-end for more accurate visualization
3. Learn matplotlib

WISHLIST:
1. HexaBot
2. Location Tracker
"""

from flask import Flask, render_template, url_for
from abc import ABC, abstractmethod
from enum import Enum
#import matplotlib.pyplot as plt

app = Flask(__name__, 
            static_url_path='',
            static_folder='static')

@app.route("/")
def home():
    print("Home route accessed")
    return render_template("services.html")

@app.route("/services")
def services():
    print("Services route accessed")
    return render_template("services.html")

@app.route("/tracking")
def tracking():
    print("Tracking route accessed")
    return render_template("tracking.html")

# add direct routes for HTML files
@app.route("/services.html")
def services_html():
    print("Services.html route accessed")
    return render_template("services.html")

@app.route("/tracking.html")
def tracking_html():
    print("Tracking.html route accessed")
    return render_template("tracking.html")

if __name__ == "__main__":
    app.debug = True
    print("Flask app routes:")
    print(app.url_map)
    app.run(debug=True)

# employee statuses list inside class
class EmployeeStatus(Enum):
    WORKING = "Working"
    PAID_LEAVE = "Paid_Leave"
    AWOL = "AWOL"
    DAY_OFF = "Day_off"

# vehicle abstract class
class Vehicle(ABC):
    def __init__(self, gas_level: float, needs_maintenance: bool):
        self.__gas_level = gas_level
        self.__needs_maintenance = needs_maintenance

    @property
    def gas_level(self) -> float:
        return self.__gas_level

    @gas_level.setter
    def gas_level(self, level: float):
        self.__gas_level = level

    @property
    def needs_maintenance(self) -> bool:
        return self.__needs_maintenance

    @abstractmethod
    def schedule_maintenance(self):
        pass

# employee abstract class
class Employee(ABC):
    def __init__(self, name: str, employee_id: int, status: EmployeeStatus):
        self.__name = name
        self.__employee_id = employee_id
        self.__status = status

    @property
    def name(self) -> str:
        return self.__name

    @property
    def employee_id(self) -> int:
        return self.__employee_id

    @property
    def status(self) -> EmployeeStatus:
        return self.__status

    @status.setter
    def status(self, status: EmployeeStatus):
        self.__status = status

    @abstractmethod
    def calculate_salary(self) -> float:
        pass

# employee child: TruckDriver subclass
class TruckDriver(Employee):
    __SALARY = 40000.0

    def calculate_salary(self) -> float:
        return TruckDriver.__SALARY

# employee child: CarDriver subclass
class CarDriver(Employee):
    __SALARY = 30000.0

    def calculate_salary(self) -> float:
        return CarDriver.__SALARY

# employee child: MotorcycleDriver subclass
class MotorcycleDriver(Employee):
    __SALARY = 20000.0

    def calculate_salary(self) -> float:
        return MotorcycleDriver.__SALARY

# vehicle child: Motorcycle subclass
class Motorcycle(Vehicle):
    def schedule_maintenance(self):
        self.__needs_maintenance = False

# vehicle child: Car subclass
class Car(Vehicle):
    def schedule_maintenance(self):
        self.__needs_maintenance = False

# vehicle child: Truck subclass
class Truck(Vehicle):
    def schedule_maintenance(self):
        self.__needs_maintenance = False

# parent class for parcel database
class Parcel:
    def __init__(self, parcel_number: str, qr_code: str, bar_code: str):
        self.__parcel_number = parcel_number
        self.__qr_code = qr_code
        self.__bar_code = bar_code

    @property
    def parcel_number(self) -> str:
        return self.__parcel_number

    @property
    def qr_code(self) -> str:
        return self.__qr_code

    @property
    def bar_code(self) -> str:
        return self.__bar_code

# parent class admin in order to access database
class Admin:
    def __init__(self, username: str, password: str, otp_authentication: bool):
        self.__username = username
        self.__password = password
        self.__otp_authentication = otp_authentication

    def login(self, user: str, passw: str) -> bool:
        return self.__username == user and self.__password == passw

    @staticmethod
    def access_database() -> 'Database':
        return Database()

# database class for cj
class Database:
    def __init__(self):
        self.__parcels = []
        self.__employees = []
        self.__vehicles = []

    def add_parcel(self, parcel: Parcel):
        self.__parcels.append(parcel)

    def get_parcel(self):
        pass

    def remove_parcel(self):
        pass

    def find_parcels_by_employee(self):
        pass

    def add_employee(self, employee: Employee):
        self.__employees.append(employee)

    def add_vehicle(self, vehicle: Vehicle):
        self.__vehicles.append(vehicle)

    def get_vehicle(self, vehicle_id: str) -> Vehicle:
        pass

# utilities class for different kinds of graphs
# class Utilities:
#     @staticmethod
#     def generate_salary_graph(employees: list):
#         pass

#     @staticmethod
#     def generate_employee_status_graph(employees: list):
#         status_counts = {}
#         for employee in employees:
#             status = employee.status.value
#             status_counts[status] = status_counts.get(status, 0) + 1
#         plt.bar(list(status_counts.keys()), list(status_counts.values()))
#         plt.title("Employee Status")
#         plt.show()

#     @staticmethod
#     def generate_parcel_count_graph(parcels: list):
#         plt.bar(["Parcels", [len(parcels)]])
#         plt.title("Parcel Count")
#         plt.show()

#     @staticmethod
#     def generate_vehicle_usage_stats(vehicles: list):
#         pass
