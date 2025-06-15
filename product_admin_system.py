from mysql_connection import *

# =============================================================================
# DATABASE MODEL
# =============================================================================

class Product(Base):
    __tablename__ = "hh_product_info"

    # Use actual database column names (with spaces as they appear in the database)
    product_id = Column("Order Item Id", String(20), primary_key=True, nullable=False)
    id = Column("id", Integer, nullable=False, unique=True)
    product_name = Column("Product Name", String(100), nullable=False)
    product_category_id = Column("Product Category Id", Integer, nullable=False)
    product_category_name = Column("Product Category Name", String(100), nullable=False)
    dep_id = Column("Department Id", Integer, nullable=False)
    dep_name = Column("Department Name", String(100), nullable=False)

    def __repr__(self):
        return f"<Product: id={self.product_id}, name={self.product_name}>"


# =============================================================================
# PRODUCT MANAGEMENT SYSTEM
# =============================================================================
class ProductSystem:
    def __init__(self):
        self.session = session
        self.csv_path = "hexahaul_db"

        # Define mappings for CSV column names
        self.product_column_mapping = {
            'product_id': 'Order Item Id',
            'id': 'id',
            'product_name': 'Product Name',
            'product_category_id': 'Product Category Id',
            'product_category_name': 'Product Category Name',
            'dep_id': 'Department Id',
            'dep_name': 'Department Name'
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
            # Get the product IDs from new_data
            if 'Order Item Id' in new_data.columns:
                product_ids_to_update = new_data['Order Item Id'].tolist()
                # Remove existing records that match the Order Item Id in new_data
                df = df[~df['Order Item Id'].isin(product_ids_to_update)]
            
            # Append the new records
            df = pd.concat([df, new_data], ignore_index=True)
        elif new_data.empty:
            # If new_data is empty, don't change anything
            pass
        else:
            # If df is empty but new_data is not, use new_data
            df = new_data

        self._write_csv(file_name, df)

    def _replace_csv_record(self, file_name, product_id, new_data):
        """Replace a specific record in CSV file by product_id"""
        df = self._read_csv(file_name)
        
        if not df.empty:
            # Remove the old record
            df = df[df['Order Item Id'] != product_id]
            
            # Add the new record
            if not new_data.empty:
                df = pd.concat([df, new_data], ignore_index=True)
        else:
            df = new_data if not new_data.empty else pd.DataFrame()

        self._write_csv(file_name, df)

    def _remove_csv_record(self, file_name, product_id):
        """Remove a specific record from CSV file by product_id"""
        df = self._read_csv(file_name)
        
        if not df.empty and 'Order Item Id' in df.columns:
            # Remove records with the specified product_id
            df_filtered = df[df['Order Item Id'] != product_id]
            self._write_csv(file_name, df_filtered)
            print(f"Removed product {product_id} from {file_name}")

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

    def add_complete_product_record(self, product_data: dict):
        """Add a complete product record"""
        try:
            product_id = self._create_new_product(product_data)
            self.session.commit()
            print(f"Product {product_id} successfully created!")
            # Transform and update CSV file
            self._update_csv("hh_product_info.csv", pd.DataFrame([self._map_keys_to_columns(product_data, self.product_column_mapping)]))
            return product_id
        except Exception as e:
            self.session.rollback()
            print(f"Error creating product: {e}")
            raise

    def _create_new_product(self, product_data: dict):
        """Create new product record"""
        # Assign auto-increment id for product
        product_data['id'] = self._get_next_id(Product)

        # Create new record
        new_product = Product(**product_data)

        # Add to session
        self.session.add(new_product)

        return product_data['product_id']

    def update_existing_product(self, product_data: dict):
        """Update existing product record"""
        try:
            original_product_id = product_data['product_id']
            
            # Get the existing product
            product = self.session.query(Product).filter_by(product_id=original_product_id).first()
            if not product:
                raise ValueError(f"Product {original_product_id} not found")
            
            print("Updating existing product record...")
            
            # Update product attributes
            for key, value in product_data.items():
                if hasattr(product, key) and key != 'id':  # Don't update the auto-increment id
                    setattr(product, key, value)
            
            # Update CSV file - REPLACE instead of UPDATE
            # Make sure to include the 'id' field in the CSV data
            csv_data = product_data.copy()
            csv_data['id'] = product.id  # Preserve the existing id
            
            self._replace_csv_record("hh_product_info.csv", original_product_id, pd.DataFrame([self._map_keys_to_columns(csv_data, self.product_column_mapping)]))
            
            # Commit all changes
            self.session.commit()
            print(f"Product {original_product_id} successfully updated!")
            return original_product_id
            
        except Exception as e:
            self.session.rollback()
            print(f"Error updating product: {e}")
            raise

    def delete_product_record(self, product_id: str):
        """Delete product record"""
        try:
            product = self.session.query(Product).filter_by(product_id=product_id).first()
            if product:
                self.session.delete(product)
                self.session.commit()
                print(f"Product {product_id} successfully deleted!")
                
                # Remove from CSV
                self._remove_csv_record("hh_product_info.csv", product_id)
                return True
            else:
                print(f"Product {product_id} not found!")
                return False
        except Exception as e:
            self.session.rollback()
            print(f"Error deleting product: {e}")
            raise

    def get_product_by_id(self, product_id: str):
        """Retrieve product information by ID"""
        product = self.session.query(Product).filter_by(product_id=product_id).first()
        return product

    def close(self):
        """Close the database session"""
        self.session.close()


# =============================================================================
# INPUT FUNCTIONS
# =============================================================================

def get_product_data():
    """Get product information with database validation"""
    print("Product Information:")
    
    # Get existing products - use actual column names
    existing_products_df = pd.read_sql("SELECT DISTINCT `Product Name` FROM hh_product_info", con=engine)
    existing_products = existing_products_df['Product Name'].tolist()
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

    # Check if category exists - use actual column names
    category_df = pd.read_sql(
        "SELECT DISTINCT `Product Category Name`, `Product Category Id` FROM hh_product_info", 
        con=engine
    )
    existing_categories = category_df['Product Category Name'].str.lower().tolist()
    
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
        existing_cat_ids = category_df['Product Category Id'].tolist()
        
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

    # Check if department exists - use actual column names
    dep_df = pd.read_sql(
        "SELECT DISTINCT `Department Name`, `Department Id` FROM hh_product_info", 
        con=engine
    )
    existing_deps = dep_df['Department Name'].str.lower().tolist()
    
    if dep_name.lower() in existing_deps:
        # Existing department
        dep_record = session.query(Product).filter(
            Product.dep_name.ilike(dep_name)
        ).first()
        return dep_name, dep_record.dep_id
    else:
        # New department
        existing_dep_ids = dep_df['Department Id'].tolist()
        
        while True:
            try:
                dep_id = int(input("New Department ID: ").strip())
                if dep_id not in existing_dep_ids:
                    break
                print("Department ID already exists. Enter a new one.")
            except ValueError:
                print("Please enter a valid numeric ID")
        
        return dep_name, dep_id


def get_new_product_data():
    """Collect all data for a new product"""
    print("="*60)
    print("           NEW PRODUCT ENTRY SYSTEM")
    print("="*60)

    # Get Product ID
    while True:
        product_id = input("Enter Product ID: ").strip().upper()
        if product_id:
            # Check if product exists
            existing_product = session.query(Product).filter_by(product_id=product_id).first()
            if existing_product:
                print(f"Product ID {product_id} already exists. Please try a different ID.")
                continue
            else:
                break
        print("Product ID cannot be empty")

    # Get product data
    product_info = get_product_data()
    
    # Build product data
    product_data = {
        'product_id': product_id,
        'product_name': product_info['product_name'],
        'product_category_id': product_info['product_category_id'],
        'product_category_name': product_info['product_category_name'],
        'dep_id': product_info['dep_id'],
        'dep_name': product_info['dep_name']
    }

    return product_data


def get_existing_product_for_update(product_id):
    """Get existing product data and allow updates"""
    print("="*60)
    print("           UPDATE PRODUCT ENTRY SYSTEM")
    print("="*60)
    
    # Get the existing product to pre-populate data
    existing_product = session.query(Product).filter_by(product_id=product_id).first()
    if not existing_product:
        print(f"Product {product_id} not found!")
        return None
    
    print(f"Updating Product: {product_id}")
    print("Press Enter to keep current value, or enter new value to change:")
    
    # Product name
    print(f"\nCurrent Product Name: {existing_product.product_name}")
    name_choice = input("Update product name? (y/n): ").lower().strip()
    if name_choice in ['y', 'yes']:
        while True:
            new_name = input("Enter new product name: ").strip().title()
            if new_name:
                product_name = new_name
                break
            print("Product name cannot be empty")
    else:
        product_name = existing_product.product_name
    
    # Product category
    print(f"\nCurrent Category: {existing_product.product_category_name} (ID: {existing_product.product_category_id})")
    category_choice = input("Update product category? (y/n): ").lower().strip()
    if category_choice in ['y', 'yes']:
        while True:
            category_name = input("Product Category Name: ").strip().title()
            if category_name:
                break
            print("Category name cannot be empty")
        
        # Check if category exists - use actual column names
        category_df = pd.read_sql(
            "SELECT DISTINCT `Product Category Name`, `Product Category Id` FROM hh_product_info", 
            con=engine
        )
        existing_categories = category_df['Product Category Name'].str.lower().tolist()
        
        if category_name.lower() in existing_categories:
            # Existing category
            cat_record = session.query(Product).filter(
                Product.product_category_name.ilike(category_name)
            ).first()
            category_id = cat_record.product_category_id
        else:
            # New category
            existing_cat_ids = category_df['Product Category Id'].tolist()
            while True:
                try:
                    category_id = int(input("New Product Category ID: ").strip())
                    if category_id not in existing_cat_ids:
                        break
                    print("Category ID already exists. Enter a new one.")
                except ValueError:
                    print("Please enter a valid numeric ID")
    else:
        category_name = existing_product.product_category_name
        category_id = existing_product.product_category_id
    
    # Department
    print(f"\nCurrent Department: {existing_product.dep_name} (ID: {existing_product.dep_id})")
    dept_choice = input("Update department? (y/n): ").lower().strip()
    if dept_choice in ['y', 'yes']:
        dep_name, dep_id = _handle_department_info()
    else:
        dep_name = existing_product.dep_name
        dep_id = existing_product.dep_id

    # Build updated product data - INCLUDE THE ID FIELD
    product_data = {
        'product_id': product_id,
        'id': existing_product.id,  # Include the existing id
        'product_name': product_name,
        'product_category_id': category_id,
        'product_category_name': category_name,
        'dep_id': dep_id,
        'dep_name': dep_name
    }

    return product_data


def existing_product_data():
    """Get existing product for update"""
    # Loop until a valid product is selected
    while True:
        try:
            # Prompt user to enter a Product ID
            product_id = input("Enter Product ID to update: ").strip().upper()
        except ValueError:
            # Handle invalid input type
            print("Invalid input. Please enter a valid Product ID.")
            continue

        # Query the database for the product with the given Product ID
        product = session.query(Product).filter_by(product_id=product_id).first()

        # If product not found, notify user and retry
        if not product:
            print("Product not found. Please try again.")
            continue

        # Display basic details of the found product
        print("\nFound Product:")
        print(f"Product ID: {product.product_id}")
        print(f"Name: {product.product_name}")
        print(f"Category: {product.product_category_name}")
        print(f"Department: {product.dep_name}")
        
        # Ask user to confirm if this is the correct product
        confirm = input("\nIs this the product you wish to update? (y/n): ").strip().lower()

        if confirm == 'y':
            # If confirmed, fetch and return the product for update
            result = get_existing_product_for_update(product_id)
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

def display_product_summary(product_data):
    """Display a summary of the product before confirmation"""
    print("\n" + "="*60)
    print("                PRODUCT SUMMARY")
    print("="*60)
    print(f"Product ID: {product_data['product_id']}")
    print(f"Product Name: {product_data['product_name']}")
    print(f"Category: {product_data['product_category_name']} (ID: {product_data['product_category_id']})")
    print(f"Department: {product_data['dep_name']} (ID: {product_data['dep_id']})")
    if 'id' in product_data:
        print(f"Internal ID: {product_data['id']}")
    print("="*60)

def main():
    """Main function to run the product management system"""
    product_system = ProductSystem()
    
    try:
        while True:
            print("\nProduct Management System")
            print("1. Create New Product")
            print("2. Update Existing Product")
            print("3. View Product")
            print("4. Delete Product")
            print("5. Exit")
            
            choice = input("\nSelect option (1-5): ").strip()
            
            if choice == '1':
                try:
                    product_data = get_new_product_data()
                    if product_data:
                        display_product_summary(product_data)
                        
                        confirm = input("\nConfirm product creation? (y/n): ").lower().strip()
                        if confirm in ['y', 'yes']:
                            product_system.add_complete_product_record(product_data)
                        else:
                            print("Product creation cancelled")
                except Exception as e:
                    print(f"Error creating product: {e}")

            elif choice == '2':
                try:
                    product_data = existing_product_data()
                    if product_data:
                        display_product_summary(product_data)
                        
                        confirm = input("\nConfirm product update? (y/n): ").lower().strip()
                        if confirm in ['y', 'yes']:
                            product_system.update_existing_product(product_data)
                        else:
                            print("Product update cancelled")

                except Exception as e:
                    print(f"Error updating product: {e}")
            
            elif choice == '3':
                product_id = input("Enter Product ID to view: ").strip().upper()
                product = product_system.get_product_by_id(product_id)
                if product:
                    print(f"\n{product}")
                    print(f"Name: {product.product_name}")
                    print(f"Category: {product.product_category_name} (ID: {product.product_category_id})")
                    print(f"Department: {product.dep_name} (ID: {product.dep_id})")
                else:
                    print("Product not found")
            
            elif choice == '4':
                product_id = input("Enter Product ID to delete: ").strip().upper()
                # Show product details before deletion
                product = product_system.get_product_by_id(product_id)
                if product:
                    print(f"\nProduct to delete:")
                    print(f"ID: {product.product_id}")
                    print(f"Name: {product.product_name}")
                    print(f"Category: {product.product_category_name}")
                    print(f"Department: {product.dep_name}")
                    
                    confirm = input(f"\nConfirm deletion of product {product_id}? (y/n): ").lower().strip()
                    if confirm in ['y', 'yes']:
                        product_system.delete_product_record(product_id)
                    else:
                        print("Deletion cancelled")
                else:
                    print("Product not found")
            
            elif choice == '5':
                print("Goodbye!")
                break
            
            else:
                print("Invalid option. Please choose 1-5.")
                
    except KeyboardInterrupt:
        print("\n\nProgram interrupted. Goodbye!")
    
    except Exception as e:
        print(f"Unexpected error: {e}")
    
    finally:
        product_system.close()


# =============================================================================
# ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    main()
