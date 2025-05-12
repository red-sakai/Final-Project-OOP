from abc import ABC, abstractmethod

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

# vehicle child: Motorcycle subclass
class Motorcycle(Vehicle):
    def schedule_maintenance(self):
        self._Vehicle__needs_maintenance = False  # accessing private attribute in parent class

# vehicle child: Car subclass
class Car(Vehicle):
    def schedule_maintenance(self):
        self._Vehicle__needs_maintenance = False  # accessing private attribute in parent class

# vehicle child: Truck subclass
class Truck(Vehicle):
    def schedule_maintenance(self):
        self._Vehicle__needs_maintenance = False  # accessing private attribute in parent class