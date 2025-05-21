import os
import sqlite3
from datetime import datetime

class VehicleDatabase:
    """
    Vehicle Database class to handle all database operations related to vehicles.
    Uses SQLite to store the vehicle data in a .db file.
    """
    
    def __init__(self, db_path=None):
        """
        Initialize the database connection.
        
        Args:
            db_path: Path to the SQLite database file. If None, uses default path in project directory.
        """
        if db_path is None:
            # Get the path to the project root directory
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            db_path = os.path.join(project_root, 'hexahaul_vehicles.db')
            
        self.db_path = db_path
        self.connection = None
        self.cursor = None
        
        # Connect to database
        self.connect()
        
        # Create tables if they don't exist
        self.create_tables()
        
    def connect(self):
        """Establish a connection to the SQLite database."""
        try:
            self.connection = sqlite3.connect(self.db_path)
            
            # Enable foreign keys
            self.connection.execute("PRAGMA foreign_keys = ON")
            
            # Configure connection to return rows as dictionaries
            self.connection.row_factory = sqlite3.Row
            
            self.cursor = self.connection.cursor()
            print(f"Connected to database: {self.db_path}")
        except sqlite3.Error as e:
            print(f"Error connecting to database: {e}")
    
    def close(self):
        """Close the database connection."""
        if self.connection:
            self.connection.close()
            print("Database connection closed.")
    
    def create_tables(self):
        """Create the necessary tables if they don't exist."""
        try:
            # Vehicles table
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS vehicles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                unit_brand TEXT NOT NULL,
                unit_model TEXT NOT NULL,
                unit_type TEXT NOT NULL,
                distance INTEGER DEFAULT 0,
                driver_id INTEGER,
                license_expiry DATE,
                order_id INTEGER,
                max_weight INTEGER NOT NULL,
                min_weight INTEGER DEFAULT 0,
                status TEXT DEFAULT 'available',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')
            
            # Create indexes for frequently queried columns
            self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_unit_type ON vehicles(unit_type)')
            self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_status ON vehicles(status)')
            
            self.connection.commit()
            print("Vehicle tables created successfully.")
        except sqlite3.Error as e:
            print(f"Error creating tables: {e}")
    
    def add_vehicle(self, unit_brand, unit_model, unit_type, max_weight, min_weight=0, 
                  distance=0, driver_id=None, license_expiry=None, order_id=None, status='available'):
        """
        Add a new vehicle to the database.
        
        Args:
            unit_brand (str): The brand of the vehicle
            unit_model (str): The model of the vehicle
            unit_type (str): The type of the vehicle (motorcycle, car, truck)
            max_weight (int): Maximum weight capacity in kg
            min_weight (int): Minimum weight capacity in kg
            distance (int): Total distance traveled in km
            driver_id (int): ID of the assigned driver
            license_expiry (str): License expiration date (YYYY-MM-DD)
            order_id (int): ID of the current order
            status (str): Current status of the vehicle ('available', 'in-use', 'maintenance')
            
        Returns:
            int: ID of the newly inserted vehicle, or None if the operation failed
        """
        try:
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            query = '''
            INSERT INTO vehicles (
                unit_brand, unit_model, unit_type, distance, driver_id, 
                license_expiry, order_id, max_weight, min_weight, status, 
                created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            '''
            
            self.cursor.execute(query, (
                unit_brand, unit_model, unit_type, distance, driver_id,
                license_expiry, order_id, max_weight, min_weight, status,
                current_time, current_time
            ))
            
            self.connection.commit()
            vehicle_id = self.cursor.lastrowid
            print(f"Vehicle added with ID: {vehicle_id}")
            return vehicle_id
        except sqlite3.Error as e:
            print(f"Error adding vehicle: {e}")
            return None
    
    def get_all_vehicles(self):
        """
        Get all vehicles from the database.
        
        Returns:
            list: List of dictionaries containing vehicle information
        """
        try:
            self.cursor.execute('SELECT * FROM vehicles ORDER BY id')
            
            # Convert rows to dictionaries
            vehicles = []
            for row in self.cursor.fetchall():
                vehicle = dict(row)
                vehicles.append(vehicle)
                
            return vehicles
        except sqlite3.Error as e:
            print(f"Error retrieving vehicles: {e}")
            return []
    
    def get_vehicle_by_id(self, vehicle_id):
        """
        Get a specific vehicle by its ID.
        
        Args:
            vehicle_id (int): The ID of the vehicle to retrieve
            
        Returns:
            dict: Vehicle information, or None if not found
        """
        try:
            self.cursor.execute('SELECT * FROM vehicles WHERE id = ?', (vehicle_id,))
            row = self.cursor.fetchone()
            
            if row:
                return dict(row)
            return None
        except sqlite3.Error as e:
            print(f"Error retrieving vehicle by ID: {e}")
            return None
    
    def get_vehicles_by_type(self, unit_type):
        """
        Get all vehicles of a specific type.
        
        Args:
            unit_type (str): Type of vehicles to retrieve (motorcycle, car, truck)
            
        Returns:
            list: List of dictionaries containing vehicle information
        """
        try:
            self.cursor.execute('SELECT * FROM vehicles WHERE unit_type = ?', (unit_type,))
            
            vehicles = []
            for row in self.cursor.fetchall():
                vehicle = dict(row)
                vehicles.append(vehicle)
                
            return vehicles
        except sqlite3.Error as e:
            print(f"Error retrieving vehicles by type: {e}")
            return []
    
    def get_vehicles_by_status(self, status):
        """
        Get all vehicles with a specific status.
        
        Args:
            status (str): Status of vehicles to retrieve (available, in-use, maintenance)
            
        Returns:
            list: List of dictionaries containing vehicle information
        """
        try:
            self.cursor.execute('SELECT * FROM vehicles WHERE status = ?', (status,))
            
            vehicles = []
            for row in self.cursor.fetchall():
                vehicle = dict(row)
                vehicles.append(vehicle)
                
            return vehicles
        except sqlite3.Error as e:
            print(f"Error retrieving vehicles by status: {e}")
            return []
    
    def update_vehicle(self, vehicle_id, **kwargs):
        """
        Update a vehicle's information.
        
        Args:
            vehicle_id (int): The ID of the vehicle to update
            **kwargs: Vehicle attributes to update
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Only allow updating certain fields
            allowed_fields = [
                'unit_brand', 'unit_model', 'unit_type', 'distance', 
                'driver_id', 'license_expiry', 'order_id', 'max_weight', 
                'min_weight', 'status'
            ]
            
            # Filter out invalid fields
            update_fields = {k: v for k, v in kwargs.items() if k in allowed_fields}
            
            if not update_fields:
                print("No valid fields to update.")
                return False
            
            # Add updated timestamp
            update_fields['updated_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # Build SET clause
            set_clause = ', '.join([f"{field} = ?" for field in update_fields.keys()])
            values = list(update_fields.values()) + [vehicle_id]  # Add vehicle_id at the end for the WHERE clause
            
            query = f"UPDATE vehicles SET {set_clause} WHERE id = ?"
            
            self.cursor.execute(query, values)
            self.connection.commit()
            
            if self.cursor.rowcount > 0:
                print(f"Vehicle ID {vehicle_id} updated successfully")
                return True
            else:
                print(f"No vehicle found with ID {vehicle_id}")
                return False
                
        except sqlite3.Error as e:
            print(f"Error updating vehicle: {e}")
            return False
    
    def delete_vehicle(self, vehicle_id):
        """
        Delete a vehicle from the database.
        
        Args:
            vehicle_id (int): The ID of the vehicle to delete
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            self.cursor.execute('DELETE FROM vehicles WHERE id = ?', (vehicle_id,))
            self.connection.commit()
            
            if self.cursor.rowcount > 0:
                print(f"Vehicle ID {vehicle_id} deleted successfully")
                return True
            else:
                print(f"No vehicle found with ID {vehicle_id}")
                return False
                
        except sqlite3.Error as e:
            print(f"Error deleting vehicle: {e}")
            return False
    
    def search_vehicles(self, search_term):
        """
        Search for vehicles by brand, model, type, or status.
        
        Args:
            search_term (str): Term to search for
            
        Returns:
            list: List of matching vehicles
        """
        try:
            search_pattern = f"%{search_term}%"
            
            query = '''
            SELECT * FROM vehicles 
            WHERE unit_brand LIKE ? 
               OR unit_model LIKE ? 
               OR unit_type LIKE ?
               OR status LIKE ?
            '''
            
            self.cursor.execute(query, (
                search_pattern, search_pattern, search_pattern, search_pattern
            ))
            
            vehicles = []
            for row in self.cursor.fetchall():
                vehicle = dict(row)
                vehicles.append(vehicle)
                
            return vehicles
        except sqlite3.Error as e:
            print(f"Error searching vehicles: {e}")
            return []
    
    def initialize_sample_data(self):
        """
        Initialize the database with sample vehicle data.
        Only runs if the vehicles table is empty.
        
        Returns:
            bool: True if successfully initialized or already has data, False if error occurred
        """
        try:
            # Check if table already has data
            self.cursor.execute('SELECT COUNT(*) as count FROM vehicles')
            count = self.cursor.fetchone()['count']
            
            if count > 0:
                print("Vehicles table already contains data. Skipping sample data initialization.")
                return True
            
            # Define sample vehicle data for each category
            sample_vehicles = [
                # Motorcycles
                {
                    'unit_brand': 'Honda', 
                    'unit_model': 'Click 125i', 
                    'unit_type': 'motorcycle',
                    'distance': 3500, 
                    'driver_id': 101, 
                    'license_expiry': '2023-12-31',
                    'order_id': None,
                    'max_weight': 150,
                    'min_weight': 0,
                    'status': 'available'
                },
                {
                    'unit_brand': 'Yamaha', 
                    'unit_model': 'Mio Sporty', 
                    'unit_type': 'motorcycle',
                    'distance': 4200, 
                    'driver_id': 102, 
                    'license_expiry': '2024-06-15',
                    'order_id': 5032,
                    'max_weight': 130,
                    'min_weight': 0,
                    'status': 'in-use'
                },
                {
                    'unit_brand': 'Yamaha', 
                    'unit_model': 'NMAX', 
                    'unit_type': 'motorcycle',
                    'distance': 1800, 
                    'driver_id': 103, 
                    'license_expiry': '2023-11-20',
                    'order_id': None,
                    'max_weight': 160,
                    'min_weight': 0,
                    'status': 'maintenance'
                },
                
                # Cars
                {
                    'unit_brand': 'Toyota', 
                    'unit_model': 'Vios', 
                    'unit_type': 'car',
                    'distance': 12500, 
                    'driver_id': 104, 
                    'license_expiry': '2024-02-28',
                    'order_id': None,
                    'max_weight': 500,
                    'min_weight': 150,
                    'status': 'available'
                },
                {
                    'unit_brand': 'Honda', 
                    'unit_model': 'Civic', 
                    'unit_type': 'car',
                    'distance': 8700, 
                    'driver_id': 105, 
                    'license_expiry': '2024-03-15',
                    'order_id': 5033,
                    'max_weight': 480,
                    'min_weight': 150,
                    'status': 'in-use'
                },
                {
                    'unit_brand': 'MG', 
                    'unit_model': '5', 
                    'unit_type': 'car',
                    'distance': 5600, 
                    'driver_id': 106, 
                    'license_expiry': '2023-10-10',
                    'order_id': None,
                    'max_weight': 450,
                    'min_weight': 150,
                    'status': 'maintenance'
                },
                
                # Trucks
                {
                    'unit_brand': 'Isuzu', 
                    'unit_model': '4 Wheeler', 
                    'unit_type': 'truck',
                    'distance': 23400, 
                    'driver_id': 107, 
                    'license_expiry': '2024-01-20',
                    'order_id': None,
                    'max_weight': 2000,
                    'min_weight': 500,
                    'status': 'available'
                },
                {
                    'unit_brand': 'Fuso', 
                    'unit_model': '6 Wheeler', 
                    'unit_type': 'truck',
                    'distance': 18900, 
                    'driver_id': 108, 
                    'license_expiry': '2024-05-12',
                    'order_id': 5034,
                    'max_weight': 4000,
                    'min_weight': 2000,
                    'status': 'in-use'
                },
                {
                    'unit_brand': 'Hino', 
                    'unit_model': '10 Wheeler', 
                    'unit_type': 'truck',
                    'distance': 31200, 
                    'driver_id': 109, 
                    'license_expiry': '2023-12-05',
                    'order_id': None,
                    'max_weight': 8000,
                    'min_weight': 4000,
                    'status': 'maintenance'
                }
            ]
            
            # Insert all sample vehicles
            for vehicle in sample_vehicles:
                self.add_vehicle(**vehicle)
                
            print(f"Successfully added {len(sample_vehicles)} sample vehicles to the database.")
            return True
            
        except sqlite3.Error as e:
            print(f"Error initializing sample data: {e}")
            return False
