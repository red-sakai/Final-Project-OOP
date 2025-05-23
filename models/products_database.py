import os
import pandas as pd
import sqlalchemy as sa
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('products_database')

Base = declarative_base()

class Product(Base):
    __tablename__ = 'products'
    
    id = Column(Integer, primary_key=True)
    product_name = Column(String)
    order_item_id = Column(String)
    product_category_id = Column(Integer)
    product_category_name = Column(String)
    department_id = Column(Integer)
    department_name = Column(String)
    
    def to_dict(self):
        return {
            'id': self.id,
            'product_name': self.product_name,
            'order_item_id': self.order_item_id,
            'product_category_id': self.product_category_id,
            'product_category_name': self.product_category_name,
            'department_id': self.department_id,
            'department_name': self.department_name
        }

class ProductsDatabase:
    def __init__(self, db_path=None):
        # Use a specific database file if none provided
        if db_path is None:
            db_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'database')
            os.makedirs(db_dir, exist_ok=True)
            db_path = os.path.join(db_dir, 'products.db')
            logger.info(f"Using default database path: {db_path}")
        
        # Create database directory if it doesn't exist
        os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)
        
        # Use absolute path for SQLite connection with explicit URI for better diagnostics
        db_uri = f'sqlite:///{os.path.abspath(db_path)}'
        logger.info(f"Connecting to database with URI: {db_uri}")
        
        try:
            self.engine = create_engine(db_uri)
            
            # Create tables explicitly
            logger.info("Creating database tables...")
            Base.metadata.create_all(self.engine)
            logger.info("Tables created successfully")
            
            self.Session = sessionmaker(bind=self.engine)
            
            # Check if tables were created properly
            inspector = sa.inspect(self.engine)
            tables = inspector.get_table_names()
            logger.info(f"Tables in database: {tables}")
            
            if 'products' not in tables:
                logger.error("products table was not created!")
            
            # Load data from CSV
            self.load_from_csv()
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            raise
    
    def connect(self):
        return self.Session()
    
    def disconnect(self, session=None):
        if session:
            session.close()
    
    def load_from_csv(self):
        try:
            # Find the CSV file in hexahaul_db directory
            script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            csv_path = os.path.join(script_dir, 'hexahaul_db', 'hh_product_info.csv')
            
            if not os.path.exists(csv_path):
                logger.error(f"CSV file not found: {csv_path}")
                return
            
            logger.info(f"Found CSV file at: {csv_path}")
            
            # Read the CSV file
            df = pd.read_csv(csv_path)
            logger.info(f"CSV loaded with {len(df)} rows")
            
            # Clean column names
            df.columns = [col.strip('"').lower().replace(' ', '_') for col in df.columns]
            logger.info(f"Columns after cleaning: {df.columns.tolist()}")
            
            # Check if data already exists
            session = self.connect()
            try:
                existing_count = session.query(Product).count()
                logger.info(f"Found {existing_count} existing records in database")
                
                if existing_count == 0:
                    logger.info(f"Loading product data from CSV: {csv_path}")
                    # Convert DataFrame to list of dictionaries
                    records = df.to_dict('records')
                    
                    # Insert records into the database
                    for i, record in enumerate(records):
                        try:
                            # Handle any missing values
                            for key, value in record.items():
                                if pd.isna(value):
                                    record[key] = None
                            
                            product = Product(
                                product_name=record['product_name'],
                                order_item_id=record['order_item_id'],
                                product_category_id=int(record['product_category_id']),
                                product_category_name=record['product_category_name'],
                                department_id=int(record['department_id']),
                                department_name=record['department_name']
                            )
                            session.add(product)
                            
                            # Commit in batches to avoid memory issues
                            if i % 50 == 0:
                                session.commit()
                                logger.info(f"Committed batch of records (up to {i})")
                                
                        except Exception as e:
                            logger.error(f"Error processing record {i}: {e}")
                            logger.error(f"Record data: {record}")
                    
                    # Final commit
                    session.commit()
                    logger.info(f"Loaded {len(records)} product records from CSV")
                    
                    # Verify data was loaded
                    count_after = session.query(Product).count()
                    logger.info(f"After loading, database has {count_after} records")
                else:
                    logger.info(f"Database already contains {existing_count} product records")
            except Exception as e:
                logger.error(f"Error querying or loading data: {e}")
                session.rollback()
                raise
            finally:
                session.close()
        except Exception as e:
            logger.error(f"Error loading CSV data: {e}")
            raise
    
    def get_all_products(self):
        session = self.connect()
        try:
            products = session.query(Product).all()
            return products
        finally:
            self.disconnect(session)
    
    def get_product_by_id(self, product_id):
        session = self.connect()
        try:
            product = session.query(Product).filter_by(id=product_id).first()
            return product
        finally:
            self.disconnect(session)
    
    def add_product(self, **kwargs):
        session = self.connect()
        try:
            new_product = Product(**kwargs)
            session.add(new_product)
            session.commit()
            return new_product
        finally:
            self.disconnect(session)
    
    def update_product(self, product_id, **kwargs):
        session = self.connect()
        try:
            product = session.query(Product).filter_by(id=product_id).first()
            if product:
                for key, value in kwargs.items():
                    if hasattr(product, key):
                        setattr(product, key, value)
                session.commit()
                return True
            return False
        finally:
            self.disconnect(session)
    
    def delete_product(self, product_id):
        session = self.connect()
        try:
            product = session.query(Product).filter_by(id=product_id).first()
            if product:
                session.delete(product)
                session.commit()
                return True
            return False
        finally:
            self.disconnect(session)
    
    def get_department_stats(self):
        """Get product statistics by department"""
        session = self.connect()
        try:
            # Get all products
            products = session.query(Product).all()
            
            # Group by department
            departments = {}
            for product in products:
                dept = product.department_name
                if dept not in departments:
                    departments[dept] = {
                        'count': 0
                    }
                departments[dept]['count'] += 1
            
            return departments
        finally:
            self.disconnect(session)
    
    def get_category_stats(self):
        """Get product statistics by category"""
        session = self.connect()
        try:
            # Get all products
            products = session.query(Product).all()
            
            # Group by category
            categories = {}
            for product in products:
                cat = product.product_category_name
                if cat not in categories:
                    categories[cat] = {
                        'count': 0
                    }
                categories[cat]['count'] += 1
            
            return categories
        finally:
            self.disconnect(session)
