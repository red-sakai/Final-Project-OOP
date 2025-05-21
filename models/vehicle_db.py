import sqlite3
import os
from datetime import datetime

class VehicleDatabase:
    def __init__(self, db_path=None):
        """Initialize the Vehicle Database."""
        if db_path is None:
            # Get the path to the project directory
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            db_path = os.path.join(base_dir, 'hexahaul_vehicles.db')
        
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        self.connect()
        self.create_tables()
        
    def connect(self):
        """Connect to the SQLite database."""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row  # This enables column access by name
            self.cursor = self.conn.cursor()
            print(f"Connected to database: {self.db_path}")
        except sqlite3.Error as e:
            print(f"Error connecting to database: {e}")
    
    def close(self):
        """Close the database connection."""
        if self.conn:
            self.conn.close()
            print("Database connection closed.")
    
    def create_tables(self):
        """Create necessary tables if they don't exist."""
        try:
            # Create the vehicles table
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
            
            # Create index on unit_type for faster filtering
            self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_unit_type ON vehicles(unit_type)')
            
            # Create index on status for faster filtering
            self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_status ON vehicles(status)')
            
            self.conn.commit()
            print("Database tables created successfully.")
        except sqlite3.Error as e:
            print(f"Error creating tables: {e}")

    def add_vehicle(self, unit_brand, unit_model, unit_type, max_weight, min_weight=0, 
                   distance=0, driver_id=None, license_expiry=None, order_id=None, status='available'):
        """Add a new vehicle to the database."""
        try:
            self.cursor.execute('''
                INSERT INTO vehicles (
                    unit_brand, unit_model, unit_type, distance, driver_id,
                    license_expiry, order_id, max_weight, min_weight, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                unit_brand, unit_model, unit_type, distance, driver_id,
                license_expiry, order_id, max_weight, min_weight, status
            ))
            self.conn.commit()
            new_id = self.cursor.lastrowid
            print(f"Vehicle added with ID: {new_id}")
            return new_id
        except sqlite3.Error as e:
            print(f"Error adding vehicle: {e}")
            return None
    
    def get_all_vehicles(self):
        """Get all vehicles from the database."""
        try:
            self.cursor.execute('SELECT * FROM vehicles ORDER BY unit_type, unit_brand, unit_model')
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error retrieving vehicles: {e}")
            return []
    
    def get_vehicle_by_id(self, vehicle_id):
        """Get a vehicle by its ID."""
        try:
            self.cursor.execute('SELECT * FROM vehicles WHERE id = ?', (vehicle_id,))
            return self.cursor.fetchone()
        except sqlite3.Error as e:
            print(f"Error retrieving vehicle by ID: {e}")
            return None
    
    def get_vehicles_by_type(self, unit_type):
        """Get all vehicles of a specific type."""
        try:
            self.cursor.execute('SELECT * FROM vehicles WHERE unit_type = ? ORDER BY unit_brand, unit_model', (unit_type,))
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error retrieving vehicles by type: {e}")
            return []
    
    def get_vehicles_by_status(self, status):
        """Get all vehicles with a specific status."""
        try:
            self.cursor.execute('SELECT * FROM vehicles WHERE status = ? ORDER BY unit_type, unit_brand, unit_model', (status,))
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error retrieving vehicles by status: {e}")
            return []
    
    def update_vehicle(self, vehicle_id, **data):
        """Update vehicle information."""
        try:
            # Get allowed fields that can be updated
            allowed_fields = ['unit_brand', 'unit_model', 'unit_type', 'distance', 
                              'driver_id', 'license_expiry', 'order_id', 
                              'max_weight', 'min_weight', 'status']
            
            # Filter out any fields that shouldn't be updated
            update_data = {k: v for k, v in data.items() if k in allowed_fields}
            
            if not update_data:
                print("No valid fields to update.")
                return False
            
            # Add updated_at timestamp
            update_data['updated_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # Build the SQL query dynamically
            set_clause = ', '.join([f"{key} = ?" for key in update_data.keys()])
            values = list(update_data.values())
            values.append(vehicle_id)
            
            self.cursor.execute(f'''
                UPDATE vehicles 
                SET {set_clause}
                WHERE id = ?
            ''', values)
            
            self.conn.commit()
            print(f"Vehicle {vehicle_id} updated successfully.")
            return True
        except sqlite3.Error as e:
            print(f"Error updating vehicle: {e}")
            return False
    
    def delete_vehicle(self, vehicle_id):
        """Delete a vehicle from the database."""
        try:
            self.cursor.execute('DELETE FROM vehicles WHERE id = ?', (vehicle_id,))
            self.conn.commit()
            print(f"Vehicle {vehicle_id} deleted successfully.")
            return True
        except sqlite3.Error as e:
            print(f"Error deleting vehicle: {e}")
            return False
    
    def search_vehicles(self, search_term):
        """Search for vehicles by brand, model, or type."""
        try:
            search_param = f'%{search_term}%'
            self.cursor.execute('''
                SELECT * FROM vehicles 
                WHERE unit_brand LIKE ? 
                OR unit_model LIKE ? 
                OR unit_type LIKE ?
                ORDER BY unit_type, unit_brand, unit_model
            ''', (search_param, search_param, search_param))
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error searching vehicles: {e}")
            return []
    
    def get_statistics(self):
        """Get vehicle statistics."""
        try:
            stats = {}
            
            # Count by type
            self.cursor.execute('''
                SELECT unit_type, COUNT(*) as count 
                FROM vehicles 
                GROUP BY unit_type
            ''')
            stats['by_type'] = {row['unit_type']: row['count'] for row in self.cursor.fetchall()}
            
            # Count by status
            self.cursor.execute('''
                SELECT status, COUNT(*) as count 
                FROM vehicles 
                GROUP BY status
            ''')
            stats['by_status'] = {row['status']: row['count'] for row in self.cursor.fetchall()}
            
            # Total vehicles
            self.cursor.execute('SELECT COUNT(*) as count FROM vehicles')
            stats['total'] = self.cursor.fetchone()['count']
            
            return stats
        except sqlite3.Error as e:
            print(f"Error getting vehicle statistics: {e}")
            return {}
    
    def initialize_sample_vehicles(self):
        """Initialize the database with sample vehicle data."""
        # Check if there are already vehicles in the database
        self.cursor.execute('SELECT COUNT(*) as count FROM vehicles')
        if self.cursor.fetchone()['count'] > 0:
            print("Database already contains vehicle data. Skipping sample initialization.")
            return False
        
        # Sample motorcycle data
        motorcycles = [
            ('Honda', 'Click 125i', 'motorcycle', 3500, None, None, None, 150, 0, 'available'),
            ('Yamaha', 'Mio Sporty', 'motorcycle', 4200, 101, '2023-12-31', None, 130, 0, 'in-use'),
            ('Yamaha', 'NMAX', 'motorcycle', 1800, 102, '2024-06-30', None, 160, 0, 'maintenance')
        ]
        
        # Sample car data
        cars = [
            ('Toyota', 'Vios', 'car', 12500, 103, '2023-11-15', None, 500, 150, 'available'),
            ('Honda', 'Civic', 'car', 8700, None, None, 1001, 480, 150, 'in-use'),
            ('MG', '5', 'car', 5600, 104, '2024-02-28', None, 450, 150, 'maintenance')
        ]
        
        # Sample truck data
        trucks = [
            ('Isuzu', '4 Wheeler', 'truck', 23400, 105, '2023-10-10', None, 2000, 500, 'available'),
            ('Fuso', '6 Wheeler', 'truck', 18900, 106, '2024-01-15', 1002, 4000, 2000, 'in-use'),
            ('Hino', '10 Wheeler', 'truck', 31200, 107, '2023-12-25', None, 8000, 4000, 'maintenance')
        ]
        
        try:
            # Add all sample vehicles to the database
            for vehicle in motorcycles + cars + trucks:
                self.add_vehicle(
                    unit_brand=vehicle[0],
                    unit_model=vehicle[1],
                    unit_type=vehicle[2],
                    distance=vehicle[3],
                    driver_id=vehicle[4],
                    license_expiry=vehicle[5],
                    order_id=vehicle[6],
                    max_weight=vehicle[7],
                    min_weight=vehicle[8],
                    status=vehicle[9]
                )
            
            print("Sample vehicle data initialized successfully.")
            return True
        except sqlite3.Error as e:
            print(f"Error initializing sample data: {e}")
            return False
