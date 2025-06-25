from mysql_connection import *

# =============================================================================
# DATABASE MODELS
# =============================================================================

class CustomerOrder(Base):
    __tablename__ = "hh_order"

    # order_id = Column("order_item_id", String(20), primary_key=True, nullable=False)
    # id = Column(Integer, nullable=False, unique=True) 
    order_id = Column("order_item_id", String(20), nullable=False, unique=True)
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    delivery_status = Column("delivery_status", String(50), nullable=False)
    late_delivery_risk = Column("late_delivery_risk", Integer, nullable=False)
    origin_branch = Column("origin_branch", String(100), nullable=False)
    branch_latitude = Column("branch_latitude", Float, nullable=False)
    branch_longitude = Column("branch_longitude", Float, nullable=False)
    customer_latitude = Column("customer_latitude", Float, nullable=False)
    customer_longitude = Column("customer_longitude", Float, nullable=False)
    order_date = Column("order date (DateOrders)", Date, nullable=False)
    driver_id = Column("driver_id", Integer, nullable=False)

    customer_info = relationship('Customer', back_populates='order', uselist=False, cascade="all, delete-orphan")
    product_info = relationship('Product', back_populates='order', uselist=False, cascade="all, delete-orphan")
    sales_info = relationship('Sales', back_populates='order', uselist=False, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Customer Order: id={self.order_id}, date={self.order_date} driver={self.driver_id}>"


class Customer(Base):
    __tablename__ = "hh_customer_info"   

    # order_id = Column("order_item_id", String(20), ForeignKey("hh_order.order_item_id"), primary_key=True, nullable=False) 
    # customer_id = Column("customer_id", Integer, nullable=False, unique=True) 
    # id = Column(Integer, nullable=False, unique=True) 
    order_id = Column("order_item_id", String(20), ForeignKey("hh_order.order_item_id"), nullable=False)
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    customer_id = Column("customer_id", Integer, nullable=False, unique=True)
    fname = Column("customer_fname", String(50), nullable=False)
    lname = Column("customer_lname", String(50), nullable=False)
    customer_city = Column("customer_city", String(100), nullable=False)
    customer_country = Column("customer_country", String(100), nullable=False)
    customer_segment = Column("customer_segment", String(50), nullable=False)

    order = relationship('CustomerOrder', back_populates='customer_info', uselist=False)

    def __repr__(self):
        return f"<Customer Info: id={self.customer_id}, name={self.fname} {self.lname}>"


class Product(Base):
    __tablename__ = "hh_product_info"

    # order_id = Column("order_item_id", String(20), ForeignKey("hh_order.order_item_id"), primary_key=True, nullable=False)
    # id = Column(Integer, nullable=False, unique=True)
    order_id = Column("order_item_id", String(20), ForeignKey("hh_order.order_item_id"), nullable=False)
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    product_name = Column("product_name", String(100), nullable=False)  
    product_category_id = Column("product_category_id", Integer, nullable=False)  
    product_category_name = Column("product_category_name", String(100), nullable=False)  
    dep_id = Column("department_id", Integer, nullable=False)
    dep_name = Column("department_name", String(100), nullable=False)

    order = relationship("CustomerOrder", back_populates='product_info', uselist=False)

    def __repr__(self):
        return f"Product Info: name={self.product_name}"


class Sales(Base):
    __tablename__ = "hh_sales"

    # order_id = Column("order_item_id", String(20), ForeignKey("hh_order.order_item_id"), primary_key=True, nullable=False)  
    # id = Column(Integer, nullable=False, unique=True)
    order_id = Column("order_item_id", String(20), ForeignKey("hh_order.order_item_id"), nullable=False)
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    type = Column("type", String(10), nullable=False) 
    benefit_per_order = Column("benefit_per_order", Float, nullable=False) 
    sales_per_customer = Column("sales_per_order", Float, nullable=True)
    order_discount = Column("order_item_discount_rate", Float, nullable=False) 
    profit_ratio = Column("order_item_profit_ratio", Float, nullable=False) 
    order_quantity = Column("order_item_quantity", Integer, nullable=False) 
    sales = Column("sales", Float, nullable=False)
    order_item_total = Column("order_item_total", Float, nullable=False) 
    order_profit = Column("order_profit_per_order", Float, nullable=False) 
    product_price = Column("product_price", Float, nullable=False)  
    date = Column("dateorders", Date, nullable=False)

    order = relationship("CustomerOrder", back_populates='sales_info', uselist=False)

    def __repr__(self):
        return f"Product Sales: price={self.product_price}, profit_ratio={self.profit_ratio}"



# =============================================================================
# ORDER MANAGEMENT SYSTEM
# =============================================================================
class OrderSystem:
    def __init__(self):
        self.session = session
        self.csv_path = "hexahaul_db"

        # Define mappings for CSV column names
        self.order_column_mapping = {
            'order_id': 'Order Item Id',
            'id': 'id',
            'delivery_status': 'Delivery Status',
            'late_delivery_risk': 'Late_delivery_risk',
            'origin_branch': 'Origin Branch',
            'branch_latitude': 'Branch Latitude',
            'branch_longitude': 'Branch Longitude',
            'customer_latitude': 'Customer Latitude',
            'customer_longitude': 'Customer Longitude',
            'order_date': 'order date (DateOrders)',
            'driver_id': 'driver_id'
        }
        # self.order_column_mapping = {
        #     'order_id': 'order_item_id',
        #     'id': 'id',
        #     'delivery_status': 'delivery_status',
        #     'late_delivery_risk': 'late_delivery_risk',
        #     'origin_branch': 'origin_branch',
        #     'branch_latitude': 'branch_latitude',
        #     'branch_longitude': 'branch_longitude',
        #     'customer_latitude': 'customer_latitude',
        #     'customer_longitude': 'customer_longitude',
        #     'order_date': 'order date (DateOrders)',
        #     'driver_id': 'driver_id'
        # }

        self.customer_column_mapping = {
            'order_id': 'Order Item Id',
            'customer_id': 'Customer Id',
            'id': 'id',  
            'fname': 'Customer Fname',
            'lname': 'Customer Lname',
            'customer_city': 'Customer City',
            'customer_country': 'Customer Country',
            'customer_segment': 'Customer Segment'
        }

        self.product_column_mapping = {
            'order_id': 'Order Item Id',
            'id': 'id',
            'product_name': 'Product Name',
            'product_category_id': 'Product Category Id',
            'product_category_name': 'Product Category Name',
            'dep_id': 'Department Id',
            'dep_name': 'Department Name'
        }

        self.sales_column_mapping = {
            'order_id': 'Order Item Id',
            'id': 'id',
            'type': 'Type',
            'benefit_per_order': 'Benefit per order',
            'sales_per_customer': 'Sales per customer',
            'order_discount': 'Order Item Discount Rate',
            'profit_ratio': 'Order Item Profit Ratio',
            'order_quantity': 'Order Item Quantity',
            'sales': 'Sales',
            'order_item_total': 'Order Item Total',
            'order_profit': 'Order Profit Per Order',
            'product_price': 'Product Price',
            'date': 'order date (DateOrders)'
        }

    def _read_csv(self, file_name):
        """Read data from a CSV file."""
        file_path = os.path.join(self.csv_path, file_name)
        if os.path.exists(file_path):
            return pd.read_csv(file_path)
        return pd.DataFrame()

    def _write_csv(self, file_name, data):
        """Write data to a CSV file."""
        file_path = os.path.join(self.csv_path, file_name)
        data.to_csv(file_path, index=False)

    def _update_csv(self, file_name, new_data):
        """Update the CSV file with new data - replaces existing records completely."""
        df = self._read_csv(file_name)
        
        if not df.empty and not new_data.empty:
            # Get the order IDs from new_data
            if 'Order Item Id' in new_data.columns:
                order_ids_to_update = new_data['Order Item Id'].tolist()
                # Remove existing records that match the Order Item Id in new_data
                df = df[~df['Order Item Id'].isin(order_ids_to_update)]
            
            # Append the new records
            df = pd.concat([df, new_data], ignore_index=True)
        elif new_data.empty:
            # If new_data is empty, don't change anything
            pass
        else:
            # If df is empty but new_data is not, use new_data
            df = new_data

        self._write_csv(file_name, df)

    def _replace_csv_record(self, file_name, order_id, new_data):
        """Replace a specific record in CSV file by order_id"""
        df = self._read_csv(file_name)
        
        if not df.empty:
            # Remove the old record
            df = df[df['Order Item Id'] != order_id]
            
            # Add the new record
            if not new_data.empty:
                df = pd.concat([df, new_data], ignore_index=True)
        else:
            df = new_data if not new_data.empty else pd.DataFrame()

        self._write_csv(file_name, df)

    def _remove_csv_record(self, file_name, order_id):
        """Remove a specific record from CSV file by order_id"""
        df = self._read_csv(file_name)
        
        if not df.empty and 'Order Item Id' in df.columns:
            # Remove records with the specified order_id
            df_filtered = df[df['Order Item Id'] != order_id]
            self._write_csv(file_name, df_filtered)
            print(f"Removed order {order_id} from {file_name}")

    def _map_keys_to_columns(self, data: dict, mapping: dict) -> dict:
        """
        Map dictionary keys to CSV column names according to mapping.
        Only keys present in mapping are included.
        """
        return {mapping[key]: value for key, value in data.items() if key in mapping}

    def _get_next_id(self, model_class):
        """Get the next id for a model by querying max existing id"""
        max_id = self.session.query(func.max(model_class.id)).scalar()
        if max_id is None:
            return 1
        else:
            return max_id + 1

    
    def add_complete_order_record(self, order_data: dict, user_data: dict, product_data: dict, sales_data: dict):
        """Add a complete order record with all related information"""
        try:
            order_id = self._create_new_order(order_data, user_data, product_data, sales_data)
            self.session.commit()
            print(f"Order {order_id} successfully created!")
            # Transform and update CSV files
            self._update_csv("hh_order.csv", pd.DataFrame([self._map_keys_to_columns(order_data, self.order_column_mapping)]))
            self._update_csv("hh_customer_info.csv", pd.DataFrame([self._map_keys_to_columns(user_data, self.customer_column_mapping)]))
            self._update_csv("hh_product_info.csv", pd.DataFrame([self._map_keys_to_columns(product_data, self.product_column_mapping)]))
            self._update_csv("hh_sales.csv", pd.DataFrame([self._map_keys_to_columns(sales_data, self.sales_column_mapping)]))
            return order_id
        except Exception as e:
            self.session.rollback()
            print(f"Error creating order: {e}")
            raise

    def _create_new_order(self, order_data: dict, user_data: dict, product_data: dict, sales_data: dict):
        """Create new order with all related records"""

        # Assign auto-increment ids for order, product, sales, and customer
        order_data['id'] = self._get_next_id(CustomerOrder)
        user_data['id'] = self._get_next_id(Customer)  # Assign id for customer
        product_data['id'] = self._get_next_id(Product)
        sales_data['id'] = self._get_next_id(Sales)

        # Add order_id to related data
        user_data['order_id'] = order_data['order_id']
        product_data['order_id'] = order_data['order_id']
        sales_data['order_id'] = order_data['order_id']

        # Create new records
        new_order = CustomerOrder(**order_data)
        new_customer = Customer(**user_data)
        new_product = Product(**product_data)
        new_sales = Sales(**sales_data)

        # Add to session
        self.session.add(new_order)
        self.session.add(new_customer)
        self.session.add(new_product)
        self.session.add(new_sales)

        return order_data['order_id']


    def update_existing_order(self, order_data: dict, user_data: dict, product_data: dict, sales_data: dict):
        try:
            original_order_id = order_data['order_id']
            
            # Get the existing order
            order = self.session.query(CustomerOrder).filter_by(order_id=original_order_id).first()
            if not order:
                raise ValueError(f"Order {original_order_id} not found")
            
            # Check if driver changed and update order ID accordingly
            old_driver_id = order.driver_id
            new_driver_id = order_data['driver_id']
            new_order_id = original_order_id  # Default to keeping the same ID
            
            if old_driver_id != new_driver_id:
                # Driver changed, need to generate new order ID with new prefix
                old_pin = original_order_id[2:]  # Extract PIN from current order ID
                
                try:
                    new_order_id = generate_order_id(old_pin, new_driver_id)
                    
                    # Check if new order ID already exists (and it's not the same record)
                    existing_order_check = self.session.query(CustomerOrder).filter_by(order_id=new_order_id).first()
                    if existing_order_check and existing_order_check.order_id != original_order_id:
                        raise ValueError(f"New order ID {new_order_id} already exists. Cannot update driver.")
                    
                    print(f"Driver changed: Order ID will be updated from {original_order_id} to {new_order_id}")
                    
                except ValueError as e:
                    print(f"Error generating new order ID: {e}")
                    raise
            
            # If order ID changed, we need to create new records and delete old ones
            if new_order_id != original_order_id:
                print("Creating new records with updated Order ID...")
                
                # Get existing related records
                existing_customer = self.session.query(Customer).filter_by(order_id=original_order_id).first()
                existing_product = self.session.query(Product).filter_by(order_id=original_order_id).first()
                existing_sales = self.session.query(Sales).filter_by(order_id=original_order_id).first()
                
                # Update order_data with new order ID
                order_data['order_id'] = new_order_id
                user_data['order_id'] = new_order_id
                product_data['order_id'] = new_order_id
                sales_data['order_id'] = new_order_id
                
                # Assign new IDs for the new records
                order_data['id'] = self._get_next_id(CustomerOrder)
                user_data['id'] = self._get_next_id(Customer)
                product_data['id'] = self._get_next_id(Product)
                sales_data['id'] = self._get_next_id(Sales)
                
                # Create new records with updated data
                new_order = CustomerOrder(**order_data)
                new_customer = Customer(**user_data)
                new_product = Product(**product_data)
                new_sales = Sales(**sales_data)
                
                # Add new records to session
                self.session.add(new_order)
                self.session.add(new_customer)  
                self.session.add(new_product)
                self.session.add(new_sales)
                
                # Delete old records (in correct order to avoid foreign key constraints)
                if existing_customer:
                    self.session.delete(existing_customer)
                if existing_product:
                    self.session.delete(existing_product)
                if existing_sales:
                    self.session.delete(existing_sales)
                if order:
                    self.session.delete(order)
                
                # Flush to ensure order of operations
                self.session.flush()
                
                # FIXED: Remove old records from CSV files first
                print(f"Removing old records with order ID {original_order_id} from CSV files...")
                self._remove_csv_record("hh_order.csv", original_order_id)
                self._remove_csv_record("hh_customer_info.csv", original_order_id)
                self._remove_csv_record("hh_product_info.csv", original_order_id)
                self._remove_csv_record("hh_sales.csv", original_order_id)
                
                # Add new records to CSV files
                print(f"Adding new records with order ID {new_order_id} to CSV files...")
                self._update_csv("hh_order.csv", pd.DataFrame([self._map_keys_to_columns(order_data, self.order_column_mapping)]))
                self._update_csv("hh_customer_info.csv", pd.DataFrame([self._map_keys_to_columns(user_data, self.customer_column_mapping)]))
                self._update_csv("hh_product_info.csv", pd.DataFrame([self._map_keys_to_columns(product_data, self.product_column_mapping)]))
                self._update_csv("hh_sales.csv", pd.DataFrame([self._map_keys_to_columns(sales_data, self.sales_column_mapping)]))
            
            else:
                # No order ID change, just update existing records
                print("Updating existing records...")
                
                # Update order attributes
                for key, value in order_data.items():
                    if hasattr(order, key):
                        setattr(order, key, value)
                
                # Update customer
                customer = self.session.query(Customer).filter_by(order_id=original_order_id).first()
                if customer:
                    for key, value in user_data.items():
                        if hasattr(customer, key) and key != 'order_id':
                            setattr(customer, key, value)
                
                # Update product
                product = self.session.query(Product).filter_by(order_id=original_order_id).first()
                if product:
                    for key, value in product_data.items():
                        if hasattr(product, key) and key != 'order_id':
                            setattr(product, key, value)
                
                # Update sales
                sales = self.session.query(Sales).filter_by(order_id=original_order_id).first()
                if sales:
                    for key, value in sales_data.items():
                        if hasattr(sales, key) and key != 'order_id':
                            setattr(sales, key, value)
                
                # Update CSV files - REPLACE instead of UPDATE
                self._replace_csv_record("hh_order.csv", original_order_id, pd.DataFrame([self._map_keys_to_columns(order_data, self.order_column_mapping)]))
                self._replace_csv_record("hh_customer_info.csv", original_order_id, pd.DataFrame([self._map_keys_to_columns(user_data, self.customer_column_mapping)]))
                self._replace_csv_record("hh_product_info.csv", original_order_id, pd.DataFrame([self._map_keys_to_columns(product_data, self.product_column_mapping)]))
                self._replace_csv_record("hh_sales.csv", original_order_id, pd.DataFrame([self._map_keys_to_columns(sales_data, self.sales_column_mapping)]))
            
            # Commit all changes
            self.session.commit()
            print(f"Order {new_order_id} successfully updated!")
            return new_order_id
            
        except Exception as e:
            self.session.rollback()
            print(f"Error updating order: {e}")
            raise


    def delete_order_record(self, order_id: str):
        try:
            order = self.session.query(CustomerOrder).filter_by(order_id=order_id).first()
            if order:
                self.session.delete(order)  # Cascade will handle related records
                self.session.commit()
                print(f"Order {order_id} successfully deleted!")
                for file_name in [
                    "hh_order.csv",
                    "hh_customer_info.csv",
                    "hh_product_info.csv",
                    "hh_sales.csv"
                ]:
                    df = self._read_csv(file_name)
                    if not df.empty:
                        df = df[df['Order Item Id'] != order_id]
                        self._write_csv(file_name, df)
                return True
            else:
                print(f"Order {order_id} not found!")
                return False
        except Exception as e:
            self.session.rollback()
            print(f"Error deleting order: {e}")
            raise

    def get_order_by_id(self, order_id: str):
        """Retrieve complete order information"""
        order = self.session.query(CustomerOrder).filter_by(order_id=order_id).first()
        return order

    def close(self):
        """Close the database session"""
        self.session.close()


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def generate_order_id(pin: str, driver_id: int) -> str:
    """Generate order ID based on driver's vehicle type"""
    query = "SELECT unit_name FROM hh_vehicle WHERE employee_id = %s"
    df = pd.read_sql(query, con=engine, params=[(driver_id,)])

    if df.empty:
        raise ValueError(f"No unit found for driver ID {driver_id}")

    unit_name = df.iloc[0]['unit_name']

    # Vehicle type mapping
    vehicle_prefixes = {
        'car': ['Honda Civic', 'Toyota Vios', 'MG 5'],
        'motorcycle': ['Honda Click 125i', 'Yamaha Mio Sporty', 'Yamaha NMAX'], 
        'truck': ['Isuzu ELF NHR 55', 'Hino 700 Series Dump Truck', 'Mitsubishi Fuso Fighter']
    }

    for prefix, vehicles in vehicle_prefixes.items():
        if unit_name in vehicles:
            prefix_code = {'car': 'CR', 'motorcycle': 'MC', 'truck': 'TK'}[prefix]
            return prefix_code + pin

    raise ValueError(f"Unrecognized vehicle type: {unit_name}")


# =============================================================================
# INPUT FUNCTIONS
# =============================================================================

def get_driver_assignment():
    """Get valid driver assignment with confirmation"""
    drivers_df = pd.read_sql("SELECT employee_id FROM hh_vehicle", con=engine)
    valid_ids = drivers_df['employee_id'].tolist()
    
    print("Available Driver IDs:")
    for i in range(0, len(valid_ids), 8):
        row = valid_ids[i:i + 8]
        print(" | ".join(f"{id:>4}" for id in row))
    print()

    while True:
        try:
            driver_input = input("Assign Delivery Driver ID: ").strip()
            driver_id = int(driver_input)
            
            if driver_id not in valid_ids:
                print("Invalid Driver ID. Please choose from the list above.")
                continue

            # Get vehicle info
            vehicle_df = pd.read_sql(
                "SELECT unit_name FROM hh_vehicle WHERE employee_id = %s", 
                con=engine, params=[(driver_id,)]
            )
            
            if vehicle_df.empty:
                print("No vehicle assigned to this Driver ID.")
                continue

            unit_name = vehicle_df.iloc[0]['unit_name']
            print(f"Driver: {driver_id} | Vehicle: {unit_name}")
            
            confirm = input("Confirm this driver assignment? (y/n): ").lower().strip()
            if confirm in ['y', 'yes']:
                return driver_id
            elif confirm in ['n', 'no']:
                continue
            else:
                print("Please enter 'y' or 'n'")
                
        except ValueError:
            print("Please enter a valid numeric Driver ID.")


def get_branch_info():
    """Get branch information with coordinates"""
    query = "SELECT DISTINCT origin_branch, branch_latitude, branch_longitude FROM hh_order"
    df = pd.read_sql(query, con=engine)
    
    if df.empty:
        raise ValueError("No branch data found in database")
    
    branches_dict = df.set_index('origin_branch').to_dict('index')
    valid_branches = list(branches_dict.keys())
    normalized_branches = {b.lower(): b for b in valid_branches}

    print("Available Branches:")
    for i, branch in enumerate(valid_branches, 1):
        print(f"  {i}. {branch}")
    print()

    while True:
        branch_input = input("Enter branch name: ").strip().lower()
        
        # Handle common misspellings
        if branch_input == 'paranaque':
            branch_input = 'parañaque'

        if branch_input in normalized_branches:
            selected_branch = normalized_branches[branch_input]
            branch_data = branches_dict[selected_branch]
            return (
                selected_branch,
                branch_data['branch_latitude'], 
                branch_data['branch_longitude']
            )
        else:
            print("Invalid branch name. Please choose from the list above.")


def get_customer_location():
    """Get customer location coordinates"""
    print("Customer Location:")
    
    while True:
        try:
            lat = float(input("Enter Customer Latitude: ").strip())
            if -90 <= lat <= 90:
                break
            else:
                print("Latitude must be between -90 and 90")
        except ValueError:
            print("Please enter a valid decimal number")
    
    while True:
        try:
            lng = float(input("Enter Customer Longitude: ").strip())
            if -180 <= lng <= 180:
                break
            else:
                print("Longitude must be between -180 and 180")
        except ValueError:
            print("Please enter a valid decimal number")
    
    return lat, lng


def get_customer_info():
    """Get complete customer information"""
    print("Customer Information:")
    
    while True:
        fname = input("First Name: ").strip().title()
        if fname:
            break
        print("First name cannot be empty")
    
    while True:
        lname = input("Last Name: ").strip().title()
        if lname:
            break
        print("Last name cannot be empty")
    
    while True:
        try:
            customer_id = int(input("Customer ID: ").strip())
            break
        except ValueError:
            print("Please enter a valid numeric Customer ID")
    
    while True:
        city = input("City: ").strip().title()
        if city:
            break
        print("City cannot be empty")
    
    country = input("Country (Philippines): ").strip().title() or "Philippines"
    
    segments = ["Corporate", "Consumer", "Home Office", "Small Business"]
    print(f"Segments: {', '.join(segments)}")
    while True:
        segment = input("Customer Segment: ").strip().title()
        if segment in segments:
            break
        print(f"Please choose from: {', '.join(segments)}")
    
    return {
        'fname': fname,
        'lname': lname,
        'customer_id': customer_id,
        'customer_city': city,
        'customer_country': country,
        'customer_segment': segment
    }


def get_product_data():
    """Get product information with database validation"""
    print("Product Information:")
    
    # Get existing products
    existing_products_df = pd.read_sql("SELECT DISTINCT product_name FROM hh_product_info", con=engine)
    existing_products = existing_products_df['product_name'].tolist()
    existing_products_lower = [p.lower() for p in existing_products]

    # Input product name
    while True:
        product_name_input = input("Product Name: ").strip()
        if product_name_input:
            break
        print("Product name cannot be empty")

    product_name_lower = product_name_input.lower()
    
    if product_name_lower in existing_products_lower:
        # Existing product
        matched_name = existing_products[existing_products_lower.index(product_name_lower)]
        product_record = session.query(Product).filter(Product.product_name == matched_name).first()

        if not product_record:
            raise ValueError("Product exists in DB but not accessible through Product model")

        return {
            'product_name': matched_name.title(),
            'product_category_id': product_record.product_category_id,
            'product_category_name': product_record.product_category_name.title(),
            'dep_id': product_record.dep_id,
            'dep_name': product_record.dep_name.title()
        }
    else:
        # New product
        return _handle_new_product(product_name_input.title())


def _handle_new_product(product_name: str):
    """Handle new product creation"""
    # Get category info
    while True:
        category_name = input("Product Category Name: ").strip().title()
        if category_name:
            break
        print("Category name cannot be empty")

    # Check if category exists
    category_df = pd.read_sql(
        "SELECT DISTINCT product_category_name, product_category_id FROM hh_product_info", 
        con=engine
    )
    existing_categories = category_df['product_category_name'].str.lower().tolist()
    
    if category_name.lower() in existing_categories:
        # Existing category
        cat_record = session.query(Product).filter(
            Product.product_category_name.ilike(category_name)
        ).first()
        
        category_id = cat_record.product_category_id
        dep_id = cat_record.dep_id
        dep_name = cat_record.dep_name.title()
    else:
        # New category
        existing_cat_ids = category_df['product_category_id'].tolist()
        
        while True:
            try:
                category_id = int(input("New Product Category ID: ").strip())
                if category_id not in existing_cat_ids:
                    break
                print("Category ID already exists. Enter a new one.")
            except ValueError:
                print("Please enter a valid numeric ID")

        # Get department info
        dep_name, dep_id = _handle_department_info()

    return {
        'product_name': product_name,
        'product_category_id': category_id,
        'product_category_name': category_name,
        'dep_id': dep_id,
        'dep_name': dep_name
    }


def _handle_department_info():
    """Handle department information"""
    while True:
        dep_name = input("Department Name: ").strip().title()
        if dep_name:
            break
        print("Department name cannot be empty")

    # Check if department exists
    dep_df = pd.read_sql(
        "SELECT DISTINCT department_name, department_id FROM hh_product_info", 
        con=engine
    )
    existing_deps = dep_df['department_name'].str.lower().tolist()
    
    if dep_name.lower() in existing_deps:
        # Existing department
        dep_record = session.query(Product).filter(
            Product.dep_name.ilike(dep_name)
        ).first()
        return dep_name, dep_record.dep_id
    else:
        # New department
        existing_dep_ids = dep_df['department_id'].tolist()
        
        while True:
            try:
                dep_id = int(input("New Department ID: ").strip())
                if dep_id not in existing_dep_ids:
                    break
                print("Department ID already exists. Enter a new one.")
            except ValueError:
                print("Please enter a valid numeric ID")
        
        return dep_name, dep_id


def get_sales_data():
    """Get sales/order information"""
    print("Sales Information:")
    
    # Order type
    order_type = input("Order Type (e.g., TRANSFER): ").strip().upper() or "TRANSFER"

    # Discount rate
    while True:
        try:
            discount = float(input("Discount Rate (0.0-1.0, e.g., 0.25 for 25%): ").strip())
            if 0 <= discount < 1:
                break
            print("Discount must be between 0 and 1")
        except ValueError:
            print("Please enter a valid decimal number")

    # Quantity
    while True:
        try:
            quantity = int(input("Order Quantity: ").strip())
            if quantity > 0:
                break
            print("Quantity must be positive")
        except ValueError:
            print("Please enter a valid whole number")

    # Product price
    while True:
        try:
            price = float(input("Product Price (per unit): ").strip())
            if price >= 0:
                break
            print("Price cannot be negative")
        except ValueError:
            print("Please enter a valid number")

    # Order profit
    while True:
        try:
            profit = float(input("Order Profit: ").strip())
            break
        except ValueError:
            print("Please enter a valid number")

    # Calculate derived values
    order_total = round(price * quantity, 6)
    sales_amount = round(order_total * (1 - discount), 6)
    profit_ratio = round(profit / order_total, 6) if order_total > 0 else 0
    benefit_per_order = round(profit / quantity, 6) if quantity > 0 else 0

    return {
        'type': order_type,
        'benefit_per_order': benefit_per_order,
        'sales_per_customer': None,  # This would need customer history
        'order_discount': discount,
        'profit_ratio': profit_ratio,
        'order_quantity': quantity,
        'sales': sales_amount,
        'order_item_total': order_total,
        'order_profit': profit,
        'product_price': price,
        'date': date.today()
    }


def get_existing_order_for_update(order_id):
    """Get existing order data and allow updates"""
    print("="*60)
    print("           UPDATE ORDER ENTRY SYSTEM")
    print("="*60)
    
    # Get the existing order to pre-populate data
    existing_order = session.query(CustomerOrder).filter_by(order_id=order_id).first()
    if not existing_order:
        print(f"Order {order_id} not found!")
        return None
    
    print(f"Updating Order: {order_id}")
    print("Press Enter to keep current value, or enter new value to change:")
    
    # Driver assignment (with current value shown)
    print(f"\nCurrent Driver ID: {existing_order.driver_id}")
    driver_choice = input("Keep current driver? (y/n): ").lower().strip()
    if driver_choice in ['n', 'no']:
        driver_id = get_driver_assignment()
    else:
        driver_id = existing_order.driver_id
    
    # Branch info (with current value shown)
    print(f"\nCurrent Branch: {existing_order.origin_branch}")
    branch_choice = input("Keep current branch? (y/n): ").lower().strip()
    if branch_choice in ['n', 'no']:
        branch_name, branch_lat, branch_lng = get_branch_info()
    else:
        branch_name = existing_order.origin_branch
        branch_lat = existing_order.branch_latitude
        branch_lng = existing_order.branch_longitude
    
    # Customer location
    print(f"\nCurrent Customer Location: ({existing_order.customer_latitude}, {existing_order.customer_longitude})")
    location_choice = input("Keep current customer location? (y/n): ").lower().strip()
    if location_choice in ['n', 'no']:
        customer_lat, customer_lng = get_customer_location()
    else:
        customer_lat = existing_order.customer_latitude
        customer_lng = existing_order.customer_longitude
    
    # Delivery status
    print(f"\nCurrent Delivery Status: {existing_order.delivery_status}")
    status_choice = input("Update delivery status? (y/n): ").lower().strip()
    if status_choice in ['y', 'yes']:
        statuses = ["Order Placed", "In Transit", "Delivered", "Cancelled"]
        print(f"Available statuses: {', '.join(statuses)}")
        while True:
            new_status = input("Enter new delivery status: ").strip().title()
            if new_status in statuses:
                delivery_status = new_status
                break
            print(f"Please choose from: {', '.join(statuses)}")
    else:
        delivery_status = existing_order.delivery_status
    
    # Late delivery risk
    print(f"\nCurrent Late Delivery Risk: {existing_order.late_delivery_risk}")
    risk_choice = input("Update late delivery risk? (y/n): ").lower().strip()
    if risk_choice in ['y', 'yes']:
        while True:
            try:
                late_delivery_risk = int(input("Enter late delivery risk (0 or 1): ").strip())
                if late_delivery_risk in [0, 1]:
                    break
                print("Late delivery risk must be 0 or 1")
            except ValueError:
                print("Please enter 0 or 1")
    else:
        late_delivery_risk = existing_order.late_delivery_risk

    # Build updated order data
    order_data = {
        'order_id': order_id,  # Keep the same order ID
        'delivery_status': delivery_status,
        'late_delivery_risk': late_delivery_risk,
        'origin_branch': branch_name,
        'branch_latitude': branch_lat,
        'branch_longitude': branch_lng,
        'customer_latitude': customer_lat,
        'customer_longitude': customer_lng,
        'order_date': existing_order.order_date,  # Keep original order date
        'driver_id': driver_id
    }

    # Get updated customer, product, and sales data
    print("\n--- Customer Information ---")
    user_choice = input("Update customer information? (y/n): ").lower().strip()
    if user_choice in ['y', 'yes']:
        user_data = get_customer_info()
    else:
        # Keep existing customer data
        existing_customer = existing_order.customer_info
        user_data = {
            'fname': existing_customer.fname,
            'lname': existing_customer.lname,
            'customer_id': existing_customer.customer_id,
            'customer_city': existing_customer.customer_city,
            'customer_country': existing_customer.customer_country,
            'customer_segment': existing_customer.customer_segment
        }

    print("\n--- Product Information ---")
    product_choice = input("Update product information? (y/n): ").lower().strip()
    if product_choice in ['y', 'yes']:
        product_data = get_product_data()
    else:
        # Keep existing product data
        existing_product = existing_order.product_info
        product_data = {
            'product_name': existing_product.product_name,
            'product_category_id': existing_product.product_category_id,
            'product_category_name': existing_product.product_category_name,
            'dep_id': existing_product.dep_id,
            'dep_name': existing_product.dep_name
        }

    print("\n--- Sales Information ---")
    sales_choice = input("Update sales information? (y/n): ").lower().strip()
    if sales_choice in ['y', 'yes']:
        sales_data = get_sales_data()
    else:
        # Keep existing sales data
        existing_sales = existing_order.sales_info
        sales_data = {
            'type': existing_sales.type,
            'benefit_per_order': existing_sales.benefit_per_order,
            'sales_per_customer': existing_sales.sales_per_customer,
            'order_discount': existing_sales.order_discount,
            'profit_ratio': existing_sales.profit_ratio,
            'order_quantity': existing_sales.order_quantity,
            'sales': existing_sales.sales,
            'order_item_total': existing_sales.order_item_total,
            'order_profit': existing_sales.order_profit,
            'product_price': existing_sales.product_price,
            'date': existing_sales.date
        }

    return order_data, user_data, product_data, sales_data


def get_new_order_data():
    """Collect all data for a new order"""
    print("="*60)
    print("           NEW ORDER ENTRY SYSTEM")
    print("="*60)

    # Get PIN and driver
    while True:
        pin = input("Enter 6-digit Order PIN: ").strip()
        if pin.isdigit() and len(pin) == 6:
            break
        print("PIN must be exactly 6 digits")

    driver_id = get_driver_assignment()

    # Generate and validate order ID
    while True:
        try:
            order_id = generate_order_id(pin, driver_id)
            
            # Check if order exists
            existing_order = session.query(CustomerOrder).filter_by(order_id=order_id).first()
            if existing_order:
                print(f"Order ID {order_id} already exists. Please try a different PIN.")
                pin = input("Enter new 6-digit PIN: ").strip()
                continue
            else:
                break
        except ValueError as e:
            print(f"{e}")
            return None

    # Get branch info
    branch_name, branch_lat, branch_lng = get_branch_info()
    
    # Get customer location
    customer_lat, customer_lng = get_customer_location()

    # Build order data
    order_data = {
        'order_id': order_id,
        'delivery_status': "Order Placed",
        'late_delivery_risk': 0,
        'origin_branch': branch_name,
        'branch_latitude': branch_lat,
        'branch_longitude': branch_lng,
        'customer_latitude': customer_lat,
        'customer_longitude': customer_lng,
        'order_date': date.today(),
        'driver_id': driver_id
    }

    # Get other data
    user_data = get_customer_info()
    product_data = get_product_data()
    sales_data = get_sales_data()

    return order_data, user_data, product_data, sales_data


def get_existing_order_data(order_id):
    """Collect all data for a existing order"""
    print("="*60)
    print("               ORDER ENTRY SYSTEM")
    print("="*60)

    pin = order_id[2:]

    driver_id = get_driver_assignment()

    # Generate and validate order ID
    while True:
        try:
            order_id = generate_order_id(pin, driver_id)
            
            # Check if order exists
            existing_order = session.query(CustomerOrder).filter_by(order_id=order_id).first()
            if existing_order:
                print(f"Order ID {order_id} already exists. Please try a different PIN.")
                pin = input("Enter new 6-digit PIN: ").strip()
                continue
            else:
                break
        except ValueError as e:
            print(f"{e}")
            return None


    # Get branch info
    branch_name, branch_lat, branch_lng = get_branch_info()
    
    # Get customer location
    customer_lat, customer_lng = get_customer_location()

    # Build order data
    order_data = {
        'order_id': order_id,
        'delivery_status': "Order Placed",
        'late_delivery_risk': 0,
        'origin_branch': branch_name,
        'branch_latitude': branch_lat,
        'branch_longitude': branch_lng,
        'customer_latitude': customer_lat,
        'customer_longitude': customer_lng,
        'order_date': date.today(),
        'driver_id': driver_id
    }

    # Get other data
    user_data = get_customer_info()
    product_data = get_product_data()
    sales_data = get_sales_data()

    return order_data, user_data, product_data, sales_data


def existing_order_data():
    """Get existing order for update"""

    # Loop until a valid order is selected
    while True:
        try:
            # Prompt user to enter an Order ID
            order_id = input("Enter Order ID to update: ").strip().upper()
        except ValueError:
            # Handle invalid input type
            print("Invalid input. Please enter a valid Order ID.")
            continue

        # Query the database for the order with the given Order ID
        order = session.query(CustomerOrder).filter_by(order_id=order_id).first()

        # If order not found, notify user and retry
        if not order:
            print("Order not found. Please try again.")
            continue

        # Display basic details of the found order
        print("\nFound Order:")
        print(f"Order ID: {order.order_id}")
        print(f"Date: {order.order_date}")
        print(f"Driver: {order.driver_id}")
        print(f"Status: {order.delivery_status}")
        
        # Display customer name if customer info is available
        if order.customer_info:
            print(f"Customer: {order.customer_info.fname} {order.customer_info.lname}")
        
        # Display product name if product info is available
        if order.product_info:
            print(f"Product: {order.product_info.product_name}")
        
        # Ask user to confirm if this is the correct order
        confirm = input("\nIs this the order you wish to update? (y/n): ").strip().lower()

        if confirm == 'y':
            # If confirmed, fetch and return the order for update
            result = get_existing_order_for_update(order_id)
            return result
        elif confirm == 'n':
            # If not confirmed, loop again
            continue
        else:
            # Handle unexpected input
            print("Please enter 'y' or 'n'")

        
# =============================================================================
# MAIN FUNCTIONS
# =============================================================================

def display_order_summary(order_data, user_data, product_data, sales_data):
    """Display a summary of the order before confirmation"""
    print("\n" + "="*60)
    print("                ORDER SUMMARY")
    print("="*60)
    print(f"Order ID: {order_data['order_id']}")
    print(f"Date: {order_data['order_date']}")
    print(f"Driver: {order_data['driver_id']}")
    print(f"Branch: {order_data['origin_branch']}")
    print(f"Customer: {user_data['fname']} {user_data['lname']}")
    print(f"Product: {product_data['product_name']}")
    print(f"Quantity: {sales_data['order_quantity']}")
    print(f"Total: ₱{sales_data['order_item_total']:,.2f}")
    print(f"Profit: ₱{sales_data['order_profit']:,.2f}")
    print("="*60)


def main():
    """Main function to run the order management system"""
    order_system = OrderSystem()
    
    try:
        while True:
            print("\nOrder Management System")
            print("1. Create New Order")
            print("2. Update existing Order")
            print("3. View Order")
            print("4. Delete Order")
            print("5. Exit")
            
            choice = input("\nSelect option (1-4): ").strip()
            
            if choice == '1':
                try:
                    result = get_new_order_data()
                    if result:
                        order_data, user_data, product_data, sales_data = result
                        display_order_summary(order_data, user_data, product_data, sales_data)
                        
                        confirm = input("\nConfirm order creation? (y/n): ").lower().strip()
                        if confirm in ['y', 'yes']:
                            order_system.add_complete_order_record(
                                order_data, user_data, product_data, sales_data
                            )
                        else:
                            print("Order creation cancelled")
                except Exception as e:
                    print(f"Error creating order: {e}")

            elif choice == '2':
                try:
                    result = existing_order_data()
                    if result:
                        order_data, user_data, product_data, sales_data = result
                        display_order_summary(order_data, user_data, product_data, sales_data)
                        
                        confirm = input("\nConfirm order to update? (y/n): ").lower().strip()
                        if confirm in ['y', 'yes']:
                            order_system.update_existing_order(
                                order_data, user_data, product_data, sales_data
                            )
                        else:
                            print("Order update cancelled")

                except Exception as e:
                    print(f"Error update order: {e}")
            
            elif choice == '3':
                order_id = input("Enter Order ID to view: ").strip()
                order = order_system.get_order_by_id(order_id)
                if order:
                    print(f"\n{order}")
                    if order.customer_info:
                        print(f"{order.customer_info}")
                    if order.product_info:
                        print(f"{order.product_info}")
                    if order.sales_info:
                        print(f"{order.sales_info}")
                else:
                    print("Order not found")
            
            elif choice == '4':
                order_id = input("Enter Order ID to delete: ").strip().upper()
                confirm = input(f"Confirm deletion of order {order_id}? (y/n): ").lower().strip()
                if confirm in ['y', 'yes']:
                    order_system.delete_order_record(order_id)
            
            elif choice == '5':
                print("Goodbye!")
                break
            
            else:
                print("Invalid option. Please choose 1-4.")
                
    except KeyboardInterrupt:
        print("\n\nProgram interrupted. Goodbye!")
    
    except Exception as e:
        print(f"Unexpected error: {e}")
    
    finally:
        order_system.close()


# =============================================================================
# ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    main()