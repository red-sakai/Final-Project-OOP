import os
import pandas as pd
from sqlalchemy import create_engine, Column, Integer, Float, String, Date, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

Base = declarative_base()

class Sale(Base):
    __tablename__ = 'sales'
    id = Column(Integer, primary_key=True)
    order_item_id = Column(String(50))
    payment_type = Column(String(20))
    order_date = Column(Date)
    product_price = Column(Float)
    order_item_quantity = Column(Integer)
    order_item_total = Column(Float)
    order_profit_per_order = Column(Float)

    def to_dict(self):
        return {
            'id': self.id,
            'order_item_id': self.order_item_id,
            'payment_type': self.payment_type,
            'order_date': self.order_date.strftime('%Y-%m-%d') if self.order_date else '',
            'product_price': self.product_price,
            'order_item_quantity': self.order_item_quantity,
            'order_item_total': self.order_item_total,
            'order_profit_per_order': self.order_profit_per_order
        }

class SalesDatabase:
    def __init__(self, db_path=None):
        if db_path is None:
            db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'database', 'hexahaul_sales.db')
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.engine = create_engine(f'sqlite:///{db_path}', echo=False)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self._load_csv_to_db()

    def _load_csv_to_db(self):
        session = self.Session()
        # Only load if table is empty
        if session.query(Sale).count() == 0:
            csv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'hexahaul_db', 'hh_sales.csv')
            if not os.path.exists(csv_path):
                session.close()
                return
            df = pd.read_csv(csv_path)
            for idx, row in df.iterrows():
                try:
                    sale = Sale(
                        order_item_id=row.get('Order Item Id', ''),
                        payment_type=row.get('Type', ''),
                        order_date=datetime.strptime(str(row.get('order date (DateOrders)', '')), '%Y-%m-%d').date() if pd.notnull(row.get('order date (DateOrders)', '')) else None,
                        product_price=float(row.get('Product Price', 0)) if pd.notnull(row.get('Product Price', 0)) else 0,
                        order_item_quantity=int(row.get('Order Item Quantity', 0)) if pd.notnull(row.get('Order Item Quantity', 0)) else 0,
                        order_item_total=float(row.get('Order Item Total', 0)) if pd.notnull(row.get('Order Item Total', 0)) else 0,
                        order_profit_per_order=float(row.get('Order Profit Per Order', 0)) if pd.notnull(row.get('Order Profit Per Order', 0)) else 0
                    )
                    session.add(sale)
                except Exception as e:
                    print(f"Error loading row {idx}: {e}")
            session.commit()
        session.close()

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
