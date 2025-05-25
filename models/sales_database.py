import os
import pandas as pd
from sqlalchemy import create_engine, Column, Integer, Float, String, DateTime, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

Base = declarative_base()

class Sale(Base):
    __tablename__ = 'sales'
    
    id = Column(Integer, primary_key=True)
    order_item_id = Column(String(50), nullable=True)  # Changed nullable to True
    payment_type = Column(String(20), nullable=True)   # Changed nullable to True
    benefit_per_order = Column(Float, nullable=True)
    sales_per_customer = Column(Float, nullable=True)
    order_item_discount_rate = Column(Float, nullable=True)
    order_item_product_price = Column(Float, nullable=True)
    order_item_profit_ratio = Column(Float, nullable=True)
    order_item_quantity = Column(Integer, nullable=True)
    sales = Column(Float, nullable=True)
    order_item_total = Column(Float, nullable=True)
    order_profit_per_order = Column(Float, nullable=True)
    product_price = Column(Float, nullable=True)
    order_date = Column(DateTime, nullable=True)
    
    def __repr__(self):
        return f"<Sale(order_item_id='{self.order_item_id}', payment_type='{self.payment_type}')>"
    
    def to_dict(self):
        return {
            'id': self.id,
            'order_item_id': self.order_item_id,
            'payment_type': self.payment_type,
            'benefit_per_order': self.benefit_per_order,
            'sales_per_customer': self.sales_per_customer,
            'order_item_discount_rate': self.order_item_discount_rate,
            'order_item_product_price': self.order_item_product_price,
            'order_item_profit_ratio': self.order_item_profit_ratio,
            'order_item_quantity': self.order_item_quantity,
            'sales': self.sales,
            'order_item_total': self.order_item_total,
            'order_profit_per_order': self.order_profit_per_order,
            'product_price': self.product_price,
            'order_date': self.order_date.strftime('%Y-%m-%d') if self.order_date else None
        }

class SalesDatabase:
    def __init__(self, db_path=None):
        if db_path is None:
            # Use default path relative to this file
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            db_path = os.path.join(base_dir, 'database', 'hexahaul.db')
            
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        # Check if database file exists or is empty
        db_exists = os.path.exists(db_path) and os.path.getsize(db_path) > 0
        
        # Create engine with echo=True for debugging
        self.engine = create_engine(f'sqlite:///{db_path}', echo=True)
        
        # Drop the sales table if it exists to recreate it with proper schema
        if db_exists:
            try:
                Sale.__table__.drop(self.engine, checkfirst=True)
                print("Dropped existing sales table")
            except Exception as e:
                print(f"Error dropping table: {e}")
        
        # Create all tables
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        
        # Initialize with CSV data regardless
        self._load_csv_data()
    
    def _load_csv_data(self):
        try:
            # Path to CSV file
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            csv_path = os.path.join(base_dir, 'hexahaul_db', 'hh_sales.csv')
            
            if not os.path.exists(csv_path):
                print(f"CSV file not found: {csv_path}")
                return
            
            # Read CSV file
            df = pd.read_csv(csv_path)
            print(f"Loaded CSV with columns: {df.columns.tolist()}")
            
            # Check for required columns
            required_columns = ['Order Item Id', 'Type', 'Order Item Product Price', 
                               'Order Item Quantity', 'Order Profit Per Order', 'order date (DateOrders)']
            
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                print(f"Missing columns in CSV: {missing_columns}")
                return
            
            # Convert DataFrame to list of dictionaries
            sales_data = df.to_dict('records')
            
            # Insert into database
            session = self.Session()
            
            # Clear existing data
            session.query(Sale).delete()
            session.commit()
            
            print(f"Loading {len(sales_data)} records into database")
            for data in sales_data:
                try:
                    sale = Sale(
                        order_item_id=str(data['Order Item Id']),
                        payment_type=data['Type'],
                        benefit_per_order=data.get('Benefit per order', 0),
                        sales_per_customer=data.get('Sales per customer', 0),
                        order_item_discount_rate=data.get('Order Item Discount Rate', 0),
                        order_item_product_price=data.get('Order Item Product Price', 0),
                        order_item_profit_ratio=data.get('Order Item Profit Ratio', 0),
                        order_item_quantity=int(data.get('Order Item Quantity', 1)),
                        sales=data.get('Sales', 0),
                        order_item_total=data.get('Order Item Total', 0),
                        order_profit_per_order=data.get('Order Profit Per Order', 0),
                        product_price=data.get('Product Price', 0),
                        order_date=datetime.strptime(data['order date (DateOrders)'], '%Y-%m-%d') if 'order date (DateOrders)' in data else None
                    )
                    session.add(sale)
                except Exception as e:
                    print(f"Error adding record: {e}")
            
            session.commit()
            session.close()
            print("CSV data loaded successfully")
            
        except Exception as e:
            print(f"Error loading CSV data: {e}")
    
    def get_all_sales(self):
        session = self.Session()
        sales = session.query(Sale).all()
        session.close()
        return sales
        
    def get_sales_stats(self):
        session = self.Session()
        total_sales = session.query(func.count(Sale.id)).scalar() or 0
        total_revenue = session.query(func.sum(Sale.order_item_total)).scalar() or 0
        total_profit = session.query(func.sum(Sale.order_profit_per_order)).scalar() or 0
        session.close()
        
        return {
            'total_sales': total_sales,
            'total_revenue': total_revenue,
            'total_profit': total_profit
        }

    def add_sale(self, **kwargs):
        session = self.Session()
        sale = Sale(**kwargs)
        session.add(sale)
        session.commit()
        new_id = sale.id
        session.close()
        return new_id
        
    def update_sale(self, sale_id, **kwargs):
        session = self.Session()
        sale = session.query(Sale).filter_by(id=sale_id).first()
        if sale:
            for key, value in kwargs.items():
                if hasattr(sale, key):
                    setattr(sale, key, value)
            session.commit()
            result = True
        else:
            result = False
        session.close()
        return result
        
    def delete_sale(self, sale_id):
        session = self.Session()
        sale = session.query(Sale).filter_by(id=sale_id).first()
        if sale:
            session.delete(sale)
            session.commit()
            result = True
        else:
            result = False
        session.close()
        return result

# Test function to verify connection
def test_database():
    db = SalesDatabase()
    session = db.Session()
    
    try:
        # Check if table exists
        result = session.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='sales'").fetchone()
        print(f"Table exists: {result is not None}")
        
        if result:
            # Check columns
            columns = session.execute("PRAGMA table_info(sales)").fetchall()
            print("Table columns:")
            for col in columns:
                print(f"  {col[1]} ({col[2]})")
        
        # Count records
        count = session.query(func.count(Sale.id)).scalar()
        print(f"Record count: {count}")
        
        # Sample first record
        if count > 0:
            first = session.query(Sale).first()
            print(f"First record: {first.to_dict()}")
    
    except Exception as e:
        print(f"Test error: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    test_database()
