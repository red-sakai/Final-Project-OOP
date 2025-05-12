# Comment out matplotlib import until it's implemented
# import matplotlib.pyplot as plt
from models import Employee, Vehicle, Parcel

# utilities class for different kinds of graphs
class Utilities:
    @staticmethod
    def generate_salary_graph(employees: list):
        pass

    @staticmethod
    def generate_employee_status_graph(employees: list):
        # status_counts = {}
        # for employee in employees:
        #     status = employee.status.value
        #     status_counts[status] = status_counts.get(status, 0) + 1
        # plt.bar(list(status_counts.keys()), list(status_counts.values()))
        # plt.title("Employee Status")
        # plt.show()
        pass

    @staticmethod
    def generate_parcel_count_graph(parcels: list):
        # plt.bar(["Parcels"], [len(parcels)])
        # plt.title("Parcel Count")
        # plt.show()
        pass

    @staticmethod
    def generate_vehicle_usage_stats(vehicles: list):
        pass