import os
import datetime
import pandas as pd
from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session

Base = declarative_base()

class Vehicle(Base):
    __tablename__ = 'vehicles'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    unit_brand = Column(String)
    unit_model = Column(String)
    unit_type = Column(String)
    category = Column(String)
    distance = Column(Integer, default=0)
    driver_employee_id = Column(Integer)
    license_expiration_date = Column(String)
    order_id = Column(Integer)
    max_weight = Column(Integer)
    min_weight = Column(Integer)
    status = Column(String, default='Available')
    year = Column(Integer)

class VehicleDatabase:
    def __init__(self, db_path="vehicles.db"):
        self.db_path = db_path
        self.engine = create_engine(f'sqlite:///{db_path}')
        self.session_factory = sessionmaker(bind=self.engine)
        self.Session = scoped_session(self.session_factory)
        self.initialize_database()
        
    def connect(self):
        return self.Session()
        
    def disconnect(self):
        self.Session.remove()
            
    def initialize_database(self):
        Base.metadata.create_all(self.engine)
        
        # Check if data already exists
        session = self.connect()
        count = session.query(Vehicle).count()
        if count == 0:
            self.populate_from_csv()
        self.disconnect()
        
    def populate_from_csv(self):
        csv_path = os.path.join('hexahaul_db', 'hh_vehicle.csv')
        
        # Check if the CSV file exists
        if not os.path.exists(csv_path):
            # If CSV file is not found, use default data
            self.populate_initial_data()
            return
            
        # Read data from CSV file using pandas
        try:
            df = pd.read_csv(csv_path)
            session = self.connect()
            
            # Map CSV columns to our database schema
            for _, row in df.iterrows():
                # Determine category based on model or weight
                if 'Mio' in row['unit_name'] or 'Click' in row['unit_name'] or 'NMAX' in row['unit_name']:
                    category = 'Motorcycle'
                    unit_type = 'Motorcycle'
                elif 'Vios' in row['unit_name'] or 'Civic' in row['unit_name'] or 'MG 5' in row['unit_name']:
                    category = 'Car'
                    unit_type = 'Sedan'
                else:
                    category = 'Truck'
                    unit_type = 'Truck'
                
                # Create new Vehicle object
                vehicle = Vehicle(
                    unit_brand=row['unit_brand'],
                    unit_model=row['unit_name'].replace(row['unit_brand'] + ' ', ''),
                    unit_type=unit_type,
                    category=category,
                    distance=row['km_driven'],
                    driver_employee_id=row['Employee Id'],
                    license_expiration_date=None,
                    order_id=None,
                    max_weight=row['max_weight'],
                    min_weight=row['min_weight'],
                    status='Available',
                    year=row['year']
                )
                session.add(vehicle)
            
            session.commit()
            self.disconnect()
        except Exception as e:
            print(f"Error loading data from CSV: {e}")
            # Fallback to default data if CSV loading fails
            self.populate_initial_data()
    
    def populate_initial_data(self):
        session = self.connect()
        
        # Motorcycles
        motorcycles = [
            Vehicle(unit_brand='Honda', unit_model='Click 125i', unit_type='Motorcycle', category='Motorcycle', 
                   distance=0, driver_employee_id=None, license_expiration_date=None, order_id=None, 
                   max_weight=150, min_weight=0, status='Available'),
            Vehicle(unit_brand='Yamaha', unit_model='Mio Sporty', unit_type='Motorcycle', category='Motorcycle', 
                   distance=0, driver_employee_id=None, license_expiration_date=None, order_id=None, 
                   max_weight=120, min_weight=0, status='Available'),
            Vehicle(unit_brand='Yamaha', unit_model='NMAX', unit_type='Motorcycle', category='Motorcycle', 
                   distance=0, driver_employee_id=None, license_expiration_date=None, order_id=None, 
                   max_weight=170, min_weight=0, status='Available')
        ]
        
        # Cars
        cars = [
            Vehicle(unit_brand='Toyota', unit_model='Vios', unit_type='Sedan', category='Car', 
                   distance=0, driver_employee_id=None, license_expiration_date=None, order_id=None, 
                   max_weight=500, min_weight=0, status='Available'),
            Vehicle(unit_brand='Honda', unit_model='Civic', unit_type='Sedan', category='Car', 
                   distance=0, driver_employee_id=None, license_expiration_date=None, order_id=None, 
                   max_weight=450, min_weight=0, status='Available'),
            Vehicle(unit_brand='MG', unit_model='5', unit_type='Sedan', category='Car', 
                   distance=0, driver_employee_id=None, license_expiration_date=None, order_id=None, 
                   max_weight=480, min_weight=0, status='Available')
        ]
        
        # Trucks
        trucks = [
            Vehicle(unit_brand='Isuzu', unit_model='4 Wheeler', unit_type='Truck', category='Truck', 
                   distance=0, driver_employee_id=None, license_expiration_date=None, order_id=None, 
                   max_weight=3000, min_weight=500, status='Available'),
            Vehicle(unit_brand='Isuzu', unit_model='6 Wheeler', unit_type='Truck', category='Truck', 
                   distance=0, driver_employee_id=None, license_expiration_date=None, order_id=None, 
                   max_weight=7000, min_weight=3000, status='Available'),
            Vehicle(unit_brand='Isuzu', unit_model='10 Wheeler', unit_type='Truck', category='Truck', 
                   distance=0, driver_employee_id=None, license_expiration_date=None, order_id=None, 
                   max_weight=15000, min_weight=7000, status='Available')
        ]
        
        vehicles = motorcycles + cars + trucks
        
        for vehicle in vehicles:
            session.add(vehicle)
        
        session.commit()
        self.disconnect()
    
    def get_all_vehicles(self):
        session = self.connect()
        vehicles = session.query(Vehicle).all()
        result = [(v.id, v.unit_brand, v.unit_model, v.unit_type, v.category, v.distance, 
                  v.driver_employee_id, v.license_expiration_date, v.order_id, 
                  v.max_weight, v.min_weight, v.status) for v in vehicles]
        self.disconnect()
        return result
        
    def get_vehicles_by_category(self, category):
        session = self.connect()
        vehicles = session.query(Vehicle).filter_by(category=category).all()
        result = [(v.id, v.unit_brand, v.unit_model, v.unit_type, v.category, v.distance, 
                  v.driver_employee_id, v.license_expiration_date, v.order_id, 
                  v.max_weight, v.min_weight, v.status) for v in vehicles]
        self.disconnect()
        return result
        
    def update_vehicle(self, vehicle_id, **kwargs):
        session = self.connect()
        vehicle = session.query(Vehicle).filter_by(id=vehicle_id).first()
        
        if vehicle:
            for key, value in kwargs.items():
                if hasattr(vehicle, key):
                    setattr(vehicle, key, value)
            
            session.commit()
        
        self.disconnect()
        
    def delete_vehicle(self, vehicle_id):
        session = self.connect()
        vehicle = session.query(Vehicle).filter_by(id=vehicle_id).first()
        
        if vehicle:
            session.delete(vehicle)
            session.commit()
        
        self.disconnect()
        
    def add_vehicle(self, **kwargs):
        session = self.connect()
        
        vehicle = Vehicle(**kwargs)
        session.add(vehicle)
        session.commit()
        
        # Get the ID of the newly created vehicle
        vehicle_id = vehicle.id
        
        self.disconnect()
        return vehicle_id
