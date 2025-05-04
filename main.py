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

