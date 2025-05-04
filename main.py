from abc import ABC, abstractmethod
from enum import Enum

class EmployeeStatus(Enum):
    WORKING = "Working"
    PAID_LEAVE = "Paid_Leave"
    AWOL = "AWOL"
    DAY_OFF = "Day_off"

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
