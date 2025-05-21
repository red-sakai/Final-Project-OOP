import os
import datetime
import pandas as pd
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, Date, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
import random
from datetime import datetime, timedelta
import time
from sqlalchemy.exc import IntegrityError

Base = declarative_base()

class Order(Base):
    __tablename__ = 'orders'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    tracking_id = Column(String, unique=True)
    order_id = Column(Integer)
    order_item_id = Column(String)
    days_for_shipping_real = Column(Integer)
    days_for_shipment_scheduled = Column(Integer)
    delivery_status = Column(String)
    late_delivery_risk = Column(Boolean)
    market = Column(String)
    order_city = Column(String)
    order_country = Column(String)
    order_region = Column(String)
    order_state = Column(String)
    order_status = Column(String)
    origin_branch = Column(String)
    branch_latitude = Column(Float)
    branch_longitude = Column(Float)
    customer_latitude = Column(Float)
    customer_longitude = Column(Float)
    order_date = Column(String)
    driver_id = Column(Integer)
    unit_name = Column(String)
    
    # Added fields for HexaBox UI
    sender = Column(String)
    recipient = Column(String)
    origin = Column(String)
    destination = Column(String)
    package_size = Column(String)
    weight = Column(Float)
    date_shipped = Column(String)
    eta = Column(String)
    assigned_vehicle = Column(String)
    notes = Column(String)

class HexaBoxesDatabase:
    def __init__(self, db_path="hexaboxes.db"):
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
        try:
            count = session.query(Order).count()
            session.close()
            if count == 0:
                self.populate_from_csv()
        except Exception as e:
            session.rollback()
            print(f"Error checking database: {e}")
            session.close()
            self.disconnect()
    
    def generate_unique_tracking_id(self, order_id):
        # Generate a unique tracking ID by combining order ID with timestamp
        timestamp = int(time.time() * 1000) % 10000  # Get milliseconds and use last 4 digits
        return f"HX-{order_id:08d}{timestamp:04d}"
    
    def populate_from_csv(self):
        csv_path = os.path.join('hexahaul_db', 'hh_order.csv')
        
        # Check if the CSV file exists
        if not os.path.exists(csv_path):
            # If CSV file is not found, use default data
            self.populate_initial_data()
            return
            
        # Read data from CSV file using pandas
        try:
            df = pd.read_csv(csv_path)
            session = self.connect()
            
            # Generate random names for senders and recipients
            first_names = ["John", "Jane", "Michael", "Emily", "Robert", "Sarah", "David", "Linda", 
                          "James", "Maria", "William", "Jennifer", "Richard", "Elizabeth", "Joseph", 
                          "Patricia", "Thomas", "Barbara", "Charles", "Susan"]
            last_names = ["Smith", "Johnson", "Brown", "Garcia", "Miller", "Davis", "Rodriguez", 
                         "Martinez", "Hernandez", "Lopez", "Wilson", "Anderson", "Taylor", "Thomas", 
                         "Moore", "Jackson", "Martin", "Lee", "Thompson", "White"]
            
            # Package sizes
            sizes = ["Small", "Medium", "Large", "Extra Large"]
            
            # Process rows in batches to handle large CSV files
            batch_size = 100
            total_processed = 0
            
            for i in range(0, len(df), batch_size):
                batch = df.iloc[i:i+batch_size]
                
                for _, row in batch.iterrows():
                    try:
                        # Generate unique tracking ID
                        tracking_id = self.generate_unique_tracking_id(row['Order Id'])
                        
                        # Generate random sender and recipient
                        sender = f"{random.choice(first_names)} {random.choice(last_names)}"
                        recipient = f"{random.choice(first_names)} {random.choice(last_names)}"
                        
                        # Generate origin and destination
                        origin = f"{row['Origin Branch']}, Philippines"
                        destination = f"{row['Order City']}, {row['Order Country']}"
                        
                        # Generate package size and weight
                        package_size = random.choice(sizes)
                        weight = round(random.uniform(0.5, 25.0), 2)
                        
                        # Parse date and calculate ETA
                        try:
                            order_date = datetime.strptime(row['order date (DateOrders)'], '%Y-%m-%d')
                            date_shipped = order_date.strftime('%Y-%m-%d')
                            eta_date = order_date + timedelta(days=row['Days for shipment (scheduled)'])
                            eta = eta_date.strftime('%Y-%m-%d')
                        except:
                            # Fallback if date parsing fails
                            date_shipped = "2023-01-01"
                            eta = "2023-01-05"
                        
                        # Map delivery status to package status
                        status_mapping = {
                            "Shipping on time": "In Transit",
                            "Advance shipping": "In Transit",
                            "Late delivery": "In Transit",
                            "Shipping canceled": "Returned"
                        }
                        
                        # Map order status
                        order_status_mapping = {
                            "COMPLETE": "Delivered",
                            "CLOSED": "Delivered",
                            "PENDING": "Pending",
                            "PROCESSING": "In Transit",
                            "ON_HOLD": "Pending",
                            "PAYMENT_REVIEW": "Pending",
                            "PENDING_PAYMENT": "Pending",
                            "SUSPECTED_FRAUD": "Returned",
                            "CANCELED": "Returned"
                        }
                        
                        # Determine final status based on both delivery status and order status
                        package_status = status_mapping.get(row['Delivery Status'], "In Transit")
                        if row['Order Status'] in ["COMPLETE", "CLOSED"]:
                            package_status = "Delivered"
                        elif row['Order Status'] in ["SUSPECTED_FRAUD", "CANCELED"]:
                            package_status = "Returned"
                        
                        # Assigned vehicle info
                        assigned_vehicle = f"{row['unit_name']} (ID: {row['driver_id']})"
                        
                        # Create notes (optional field)
                        if row['Late_delivery_risk'] == 1:
                            notes = "This package has a high risk of late delivery. Please prioritize."
                        else:
                            notes = ""
                        
                        # Create new Order object
                        order = Order(
                            tracking_id=tracking_id,
                            order_id=row['Order Id'],
                            order_item_id=row['Order Item Id'],
                            days_for_shipping_real=row['Days for shipping (real)'],
                            days_for_shipment_scheduled=row['Days for shipment (scheduled)'],
                            delivery_status=row['Delivery Status'],
                            late_delivery_risk=bool(row['Late_delivery_risk']),
                            market=row['Market'],
                            order_city=row['Order City'],
                            order_country=row['Order Country'],
                            order_region=row['Order Region'],
                            order_state=row['Order State'],
                            order_status=row['Order Status'],
                            origin_branch=row['Origin Branch'],
                            branch_latitude=row['Branch Latitude'],
                            branch_longitude=row['Branch Longitude'],
                            customer_latitude=row['Customer Latitude'],
                            customer_longitude=row['Customer Longitude'],
                            order_date=row['order date (DateOrders)'],
                            driver_id=row['driver_id'],
                            unit_name=row['unit_name'],
                            
                            # Additional fields for UI
                            sender=sender,
                            recipient=recipient,
                            origin=origin,
                            destination=destination,
                            package_size=package_size,
                            weight=weight,
                            date_shipped=date_shipped,
                            eta=eta,
                            assigned_vehicle=assigned_vehicle,
                            notes=notes
                        )
                        session.add(order)
                        
                        # Try to commit each record individually
                        try:
                            session.commit()
                            total_processed += 1
                        except IntegrityError:
                            # Skip duplicates and continue
                            session.rollback()
                            print(f"Skipping duplicate tracking ID: {tracking_id}")
                            
                    except Exception as e:
                        session.rollback()
                        print(f"Error processing row {total_processed}: {e}")
            
            self.disconnect()
            print(f"Successfully imported {total_processed} orders from CSV.")
        except Exception as e:
            print(f"Error loading data from CSV: {e}")
            # Make sure to close and roll back the session
            try:
                session.rollback()
                session.close()
            except:
                pass
            # Fallback to default data if CSV loading fails
            self.populate_initial_data()
    
    def populate_initial_data(self):
        session = self.connect()
        
        try:
            # Sample orders with unique tracking IDs
            orders = [
                Order(
                    tracking_id=f"HX-78542{int(time.time())%1000}",
                    order_id=12345,
                    order_item_id="MC123456",
                    days_for_shipping_real=3,
                    days_for_shipment_scheduled=4,
                    delivery_status="Shipping on time",
                    late_delivery_risk=False,
                    market="Pacific Asia",
                    order_city="Manila",
                    order_country="Philippines",
                    order_region="Southeast Asia",
                    order_state="Capital Nacional",
                    order_status="PROCESSING",
                    origin_branch="Quezon City",
                    branch_latitude=14.676,
                    branch_longitude=121.0437,
                    customer_latitude=14.585361,
                    customer_longitude=121.066905,
                    order_date="2023-06-15",
                    driver_id=201,
                    unit_name="Honda Civic",
                    sender="John Smith",
                    recipient="Jane Doe",
                    origin="Manila, Philippines",
                    destination="Cebu, Philippines",
                    package_size="Medium",
                    weight=3.5,
                    date_shipped="2023-06-15",
                    eta="2023-06-18",
                    assigned_vehicle="Honda Civic (ID: 5)",
                    notes="Handle with care."
                ),
                Order(
                    tracking_id=f"HX-65923{int(time.time())%1000}",
                    order_id=12346,
                    order_item_id="CR123457",
                    days_for_shipping_real=2,
                    days_for_shipment_scheduled=4,
                    delivery_status="Advance shipping",
                    late_delivery_risk=False,
                    market="Pacific Asia",
                    order_city="Davao",
                    order_country="Philippines",
                    order_region="Southeast Asia",
                    order_state="Davao del Sur",
                    order_status="COMPLETE",
                    origin_branch="Parañaque",
                    branch_latitude=14.4793,
                    branch_longitude=121.0198,
                    customer_latitude=14.446598,
                    customer_longitude=121.00225,
                    order_date="2023-06-10",
                    driver_id=207,
                    unit_name="Isuzu ELF",
                    sender="Robert Johnson",
                    recipient="Michael Brown",
                    origin="Davao, Philippines",
                    destination="Iloilo, Philippines",
                    package_size="Large",
                    weight=8.2,
                    date_shipped="2023-06-10",
                    eta="2023-06-15",
                    assigned_vehicle="Isuzu ELF (ID: 7)",
                    notes=""
                ),
                Order(
                    tracking_id=f"HX-32145{int(time.time())%1000}",
                    order_id=12347,
                    order_item_id="TK123458",
                    days_for_shipping_real=5,
                    days_for_shipment_scheduled=4,
                    delivery_status="Late delivery",
                    late_delivery_risk=True,
                    market="Pacific Asia",
                    order_city="Baguio",
                    order_country="Philippines",
                    order_region="Southeast Asia",
                    order_state="Benguet",
                    order_status="PENDING",
                    origin_branch="Manila",
                    branch_latitude=14.5995,
                    branch_longitude=120.9842,
                    customer_latitude=14.514598,
                    customer_longitude=121.01225,
                    order_date="2023-06-17",
                    driver_id=0,
                    unit_name="",
                    sender="Lisa Davis",
                    recipient="Kevin Wilson",
                    origin="Baguio, Philippines",
                    destination="Bacolod, Philippines",
                    package_size="Small",
                    weight=1.2,
                    date_shipped="2023-06-17",
                    eta="2023-06-21",
                    assigned_vehicle="Not Assigned",
                    notes="This package has a high risk of late delivery. Please prioritize."
                )
            ]
            
            for order in orders:
                session.add(order)
            
            session.commit()
        except Exception as e:
            session.rollback()
            print(f"Error in populate_initial_data: {e}")
        finally:
            session.close()
            self.disconnect()
    
    def get_all_orders(self):
        session = self.connect()
        orders = session.query(Order).all()
        self.disconnect()
        return orders
        
    def get_orders_by_status(self, status):
        session = self.connect()
        orders = session.query(Order).filter_by(order_status=status).all()
        self.disconnect()
        return orders
        
    def get_order_by_tracking_id(self, tracking_id):
        session = self.connect()
        order = session.query(Order).filter_by(tracking_id=tracking_id).first()
        self.disconnect()
        return order
        
    def update_order(self, tracking_id, **kwargs):
        session = self.connect()
        order = session.query(Order).filter_by(tracking_id=tracking_id).first()
        
        if order:
            for key, value in kwargs.items():
                if hasattr(order, key):
                    setattr(order, key, value)
            
            session.commit()
        
        self.disconnect()
        
    def delete_order(self, tracking_id):
        session = self.connect()
        order = session.query(Order).filter_by(tracking_id=tracking_id).first()
        
        if order:
            session.delete(order)
            session.commit()
        
        self.disconnect()
        
    def add_order(self, **kwargs):
        session = self.connect()
        
        try:
            # Generate tracking ID if not provided
            if 'tracking_id' not in kwargs:
                order_id = random.randint(10000, 99999)
                kwargs['tracking_id'] = self.generate_unique_tracking_id(order_id)
            
            order = Order(**kwargs)
            session.add(order)
            session.commit()
            
            # Get the ID of the newly created order
            tracking_id = order.tracking_id
            
            return tracking_id
        except Exception as e:
            session.rollback()
            print(f"Error adding order: {e}")
            return None
        finally:
            session.close()
            self.disconnect()
