import os
import pandas as pd
from sqlalchemy import create_engine, Column, Integer, String, Float, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

Base = declarative_base()

class Sale(Base):
    __tablename__ = 'sales'
    
    id = Column(Integer, primary_key=True)
    order_item_id = Column(String(20), nullable=False)
    payment_type = Column(String(20), nullable=False)
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
    order_date = Column(Date, nullable=True)

class SalesDatabase:
    def __init__(self, db_path=None):
        if db_path is None:
            # Default to a SQLite database in the project directory
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            db_path = f"sqlite:///{os.path.join(base_dir, 'hexahaul_db', 'sales.db')}"
        
        self.engine = create_engine(db_path)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
    
    def import_csv(self, csv_path):
        try:
            # Read CSV data
            df = pd.read_csv(csv_path)
            
            # Clean and rename columns
            df.columns = [c.strip().replace('"', '').lower().replace(' ', '_').replace('(dateorders)', '') 
                         for c in df.columns]
            
            # Process data
            sales_data = []
            for _, row in df.iterrows():
                sale = Sale(
                    order_item_id=row['order_item_id'],
                    payment_type=row['type'],
                    benefit_per_order=float(row['benefit_per_order']),
                    sales_per_customer=float(row['sales_per_customer']),
                    order_item_discount_rate=float(row['order_item_discount_rate']),
                    order_item_product_price=float(row['order_item_product_price']),
                    order_item_profit_ratio=float(row['order_item_profit_ratio']),
                    order_item_quantity=int(row['order_item_quantity']),
                    sales=float(row['sales']),
                    order_item_total=float(row['order_item_total']),
                    order_profit_per_order=float(row['order_profit_per_order']),
                    product_price=float(row['product_price']),
                    order_date=datetime.strptime(row['order_date'], '%Y-%m-%d').date()
                )
                sales_data.append(sale)
            
            # Insert data into the database
            session = self.Session()
            try:
                # Clear existing data
                session.query(Sale).delete()
                
                # Add all sales records
                session.add_all(sales_data)
                session.commit()
                return True, f"Successfully imported {len(sales_data)} sales records"
            except Exception as e:
                session.rollback()
                return False, f"Error during database insertion: {str(e)}"
            finally:
                session.close()
                
        except Exception as e:
            return False, f"Error importing CSV: {str(e)}"
    
    def get_all_sales(self):
        session = self.Session()
        try:
            sales = session.query(Sale).all()
            return sales
        finally:
            session.close()
    
    def get_sales_by_type(self, payment_type):
        session = self.Session()
        try:
            sales = session.query(Sale).filter_by(payment_type=payment_type).all()
            return sales
        finally:
            session.close()
    
    def get_sales_stats(self):
        session = self.Session()
        try:
            total_sales = session.query(Sale).count()
            total_revenue = session.query(Sale).with_entities(
                Sale.sales
            ).all()
            total_revenue = sum(row[0] for row in total_revenue)
            
            total_profit = session.query(Sale).with_entities(
                Sale.order_profit_per_order
            ).all()
            total_profit = sum(row[0] for row in total_profit)
            
            payment_types = {}
            for type_name in ['CASH', 'TRANSFER', 'DEBIT', 'PAYMENT']:
                count = session.query(Sale).filter_by(payment_type=type_name).count()
                payment_types[type_name] = count
                
            return {
                'total_sales': total_sales,
                'total_revenue': total_revenue,
                'total_profit': total_profit,
                'payment_types': payment_types
            }
        finally:
            session.close()


# Initialize database and import data if this file is run directly
if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    csv_path = os.path.join(base_dir, 'hexahaul_db', 'hh_sales.csv')
    
    db = SalesDatabase()
    success, message = db.import_csv(csv_path)
    print(message)
    
    if success:
        stats = db.get_sales_stats()
        print(f"Total sales: {stats['total_sales']}")
        print(f"Total revenue: ${stats['total_revenue']:,.2f}")
        print(f"Total profit: ${stats['total_profit']:,.2f}")
        print("Payment types:")
        for type_name, count in stats['payment_types'].items():
            print(f"  {type_name}: {count}")
