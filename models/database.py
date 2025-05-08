from .employee import Employee
from .vehicle import Vehicle
from .parcel import Parcel

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
        
    # Add getters to access the lists if needed
    @property
    def parcels(self):
        return self.__parcels.copy()  # Return a copy to prevent direct modification
        
    @property
    def employees(self):
        return self.__employees.copy()
        
    @property
    def vehicles(self):
        return self.__vehicles.copy()