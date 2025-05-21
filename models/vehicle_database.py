import sqlite3
import os
import datetime

class VehicleDatabase:
    def __init__(self, db_path="vehicles.db"):
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        self.initialize_database()
        
    def connect(self):
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        
    def disconnect(self):
        if self.conn:
            self.conn.close()
            
    def initialize_database(self):
        self.connect()
        
        # Create vehicles table
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS vehicles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            unit_brand TEXT,
            unit_model TEXT,
            unit_type TEXT,
            category TEXT,
            distance INTEGER DEFAULT 0,
            driver_employee_id INTEGER,
            license_expiration_date TEXT,
            order_id INTEGER,
            max_weight INTEGER,
            min_weight INTEGER,
            status TEXT DEFAULT 'Available'
        )
        ''')
        
        # Initial data for motorcycles, cars, and trucks
        self.populate_initial_data()
        
        self.conn.commit()
        self.disconnect()
        
    def populate_initial_data(self):
        # Check if data already exists
        self.cursor.execute("SELECT COUNT(*) FROM vehicles")
        count = self.cursor.fetchone()[0]
        
        if count > 0:
            return
            
        # Motorcycles
        motorcycles = [
            ('Honda', 'Click 125i', 'Motorcycle', 'Motorcycle', 0, None, None, None, 150, 0, 'Available'),
            ('Yamaha', 'Mio Sporty', 'Motorcycle', 'Motorcycle', 0, None, None, None, 120, 0, 'Available'),
            ('Yamaha', 'NMAX', 'Motorcycle', 'Motorcycle', 0, None, None, None, 170, 0, 'Available')
        ]
        
        # Cars
        cars = [
            ('Toyota', 'Vios', 'Sedan', 'Car', 0, None, None, None, 500, 0, 'Available'),
            ('Honda', 'Civic', 'Sedan', 'Car', 0, None, None, None, 450, 0, 'Available'),
            ('MG', '5', 'Sedan', 'Car', 0, None, None, None, 480, 0, 'Available')
        ]
        
        # Trucks
        trucks = [
            ('Isuzu', '4 Wheeler', 'Truck', 'Truck', 0, None, None, None, 3000, 500, 'Available'),
            ('Isuzu', '6 Wheeler', 'Truck', 'Truck', 0, None, None, None, 7000, 3000, 'Available'),
            ('Isuzu', '10 Wheeler', 'Truck', 'Truck', 0, None, None, None, 15000, 7000, 'Available')
        ]
        
        vehicles = motorcycles + cars + trucks
        
        for vehicle in vehicles:
            self.cursor.execute('''
            INSERT INTO vehicles (unit_brand, unit_model, unit_type, category, distance, 
                                driver_employee_id, license_expiration_date, order_id, 
                                max_weight, min_weight, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', vehicle)
    
    def get_all_vehicles(self):
        self.connect()
        self.cursor.execute("SELECT * FROM vehicles")
        vehicles = self.cursor.fetchall()
        self.disconnect()
        return vehicles
        
    def get_vehicles_by_category(self, category):
        self.connect()
        self.cursor.execute("SELECT * FROM vehicles WHERE category = ?", (category,))
        vehicles = self.cursor.fetchall()
        self.disconnect()
        return vehicles
        
    def update_vehicle(self, vehicle_id, **kwargs):
        self.connect()
        
        set_clause = ", ".join([f"{key} = ?" for key in kwargs.keys()])
        values = list(kwargs.values())
        values.append(vehicle_id)
        
        query = f"UPDATE vehicles SET {set_clause} WHERE id = ?"
        self.cursor.execute(query, values)
        
        self.conn.commit()
        self.disconnect()
        
    def delete_vehicle(self, vehicle_id):
        self.connect()
        self.cursor.execute("DELETE FROM vehicles WHERE id = ?", (vehicle_id,))
        self.conn.commit()
        self.disconnect()
        
    def add_vehicle(self, **kwargs):
        self.connect()
        
        columns = ", ".join(kwargs.keys())
        placeholders = ", ".join(["?" for _ in kwargs.keys()])
        values = list(kwargs.values())
        
        query = f"INSERT INTO vehicles ({columns}) VALUES ({placeholders})"
        self.cursor.execute(query, values)
        
        self.conn.commit()
        vehicle_id = self.cursor.lastrowid
        self.disconnect()
        
        return vehicle_id
