import os
import csv
import pandas as pd
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, Float, String, DateTime, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class Customer(Base):
    __tablename__ = 'customers'
    
    id = Column(Integer, primary_key=True)
    customer_id = Column(String(50), nullable=False)
    order_item_id = Column(String(50), nullable=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    city = Column(String(100), nullable=True)
    country = Column(String(100), nullable=True)
    segment = Column(String(100), nullable=True)
    
    def __repr__(self):
        return f"<Customer(customer_id='{self.customer_id}', name='{self.first_name} {self.last_name}')>"
    
    def to_dict(self):
        return {
            'id': self.id,
            'customer_id': self.customer_id,
            'order_item_id': self.order_item_id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'full_name': f"{self.first_name} {self.last_name}",
            'city': self.city,
            'country': self.country,
            'segment': self.segment
        }

class CustomerDatabase:
    def __init__(self, db_path=None):
        if db_path is None:
            # Use default path relative to this file
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            db_path = os.path.join(base_dir, 'database', 'hexahaul.db')
            
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        # Check if database file exists
        db_exists = os.path.exists(db_path) and os.path.getsize(db_path) > 0
        
        # Create engine with echo for debugging
        self.engine = create_engine(f'sqlite:///{db_path}', echo=True)
        
        # Create all tables
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        
        # Initialize with CSV data if the table is empty
        session = self.Session()
        if session.query(Customer).count() == 0:
            self._load_csv_data()
        session.close()
    
    def _load_csv_data(self):
        try:
            # Path to CSV file
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            csv_path = os.path.join(base_dir, 'hexahaul_db', 'hh_customer_info.csv')
            
            if not os.path.exists(csv_path):
                print(f"CSV file not found: {csv_path}")
                return
            
            # Read CSV file
            df = pd.read_csv(csv_path)
            print(f"Loaded CSV with columns: {df.columns.tolist()}")
            
            # Check for required columns
            required_columns = [
                'Order Item Id', 'Customer Fname', 'Customer Lname', 
                'Customer Id', 'Customer City', 'Customer Country', 'Customer Segment'
            ]
            
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                print(f"Missing columns in CSV: {missing_columns}")
                return
            
            # Convert DataFrame to list of dictionaries
            customers_data = df.to_dict('records')
            
            # Insert into database
            session = self.Session()
            
            # Clear existing data
            session.query(Customer).delete()
            session.commit()
            
            # Track processed customer IDs to avoid duplicates
            processed_customer_ids = set()
            
            print(f"Loading {len(customers_data)} records into database")
            for data in customers_data:
                try:
                    customer_id = str(data['Customer Id'])
                    
                    # Skip duplicates (based on customer_id)
                    if customer_id in processed_customer_ids:
                        continue
                        
                    customer = Customer(
                        customer_id=customer_id,
                        order_item_id=data['Order Item Id'],
                        first_name=data['Customer Fname'],
                        last_name=data['Customer Lname'],
                        city=data['Customer City'],
                        country=data['Customer Country'],
                        segment=data['Customer Segment']
                    )
                    session.add(customer)
                    processed_customer_ids.add(customer_id)
                except Exception as e:
                    print(f"Error adding customer record: {e}")
            
            session.commit()
            session.close()
            print(f"CSV data loaded successfully. Added {len(processed_customer_ids)} unique customers.")
            
        except Exception as e:
            print(f"Error loading CSV data: {e}")
    
    def get_all_customers(self):
        """Return all customers in the database"""
        session = self.Session()
        customers = session.query(Customer).all()
        session.close()
        return customers
        
    def get_customer_stats(self):
        """Return statistics about customers"""
        session = self.Session()
        total_count = session.query(Customer).count()
        corporate_count = session.query(Customer).filter(Customer.segment == 'Corporate').count()
        consumer_count = session.query(Customer).filter(Customer.segment == 'Consumer').count()
        home_office_count = session.query(Customer).filter(Customer.segment == 'Home Office').count()
        
        # Get count of customers by city
        city_counts = session.query(
            Customer.city, func.count(Customer.id).label('count')
        ).group_by(Customer.city).order_by(func.count(Customer.id).desc()).all()
        
        top_city = city_counts[0][0] if city_counts else "N/A"
        
        session.close()
        
        return {
            'total_count': total_count,
            'corporate_count': corporate_count,
            'consumer_count': consumer_count,
            'home_office_count': home_office_count,
            'top_city': top_city
        }

    def get_customer_by_id(self, customer_id):
        """Get a customer by ID"""
        session = self.Session()
        customer = session.query(Customer).filter_by(customer_id=customer_id).first()
        session.close()
        return customer

    def add_customer(self, **kwargs):
        """Add a new customer"""
        session = self.Session()
        customer = Customer(**kwargs)
        session.add(customer)
        session.commit()
        new_id = customer.id
        session.close()
        return new_id
        
    def update_customer(self, customer_id, **kwargs):
        """Update a customer by ID"""
        session = self.Session()
        customer = session.query(Customer).filter_by(customer_id=customer_id).first()
        if customer:
            for key, value in kwargs.items():
                if hasattr(customer, key):
                    setattr(customer, key, value)
            session.commit()
            result = True
        else:
            result = False
        session.close()
        return result
        
    def delete_customer(self, customer_id):
        """Delete a customer by ID"""
        session = self.Session()
        customer = session.query(Customer).filter_by(customer_id=customer_id).first()
        if customer:
            session.delete(customer)
            session.commit()
            result = True
        else:
            result = False
        session.close()
        return result

    def get_segment_data(self):
        """Get customer count by segment for chart displays"""
        session = self.Session()
        segments = session.query(
            Customer.segment, 
            func.count(Customer.id).label('count')
        ).group_by(Customer.segment).all()
        
        result = {segment: count for segment, count in segments}
        session.close()
        return result

    def get_city_data(self):
        """Get customer count by city for chart displays"""
        session = self.Session()
        cities = session.query(
            Customer.city, 
            func.count(Customer.id).label('count')
        ).group_by(Customer.city).order_by(func.count(Customer.id).desc()).limit(10).all()
        
        result = {city: count for city, count in cities}
        session.close()
        return result

# Test function to verify database connection
def test_database():
    db = CustomerDatabase()
    session = db.Session()
    
    try:
        # Check if table exists
        result = session.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='customers'").fetchone()
        print(f"Table exists: {result is not None}")
        
        if result:
            # Check columns
            columns = session.execute("PRAGMA table_info(customers)").fetchall()
            print("Table columns:")
            for col in columns:
                print(f"  {col[1]} ({col[2]})")
        
        # Count records
        count = session.query(func.count(Customer.id)).scalar()
        print(f"Record count: {count}")
        
        # Sample first record
        if count > 0:
            first = session.query(Customer).first()
            print(f"First record: {first.to_dict()}")
    
    except Exception as e:
        print(f"Test error: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    test_database()
