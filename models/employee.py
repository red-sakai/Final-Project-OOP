from abc import ABC, abstractmethod
from enum import Enum

# employee statuses list inside class
class EmployeeStatus(Enum):
    WORKING = "Working"
    PAID_LEAVE = "Paid_Leave"
    AWOL = "AWOL"
    DAY_OFF = "Day_off"

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