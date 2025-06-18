from mysql_connection import *

# =============================================================================
# DATABASE MODELS
# =============================================================================

class Customer(Base):
    __tablename__ = "hh_customer_info"

    order_item_id = Column("order_item_id", String(20), primary_key=True, nullable=False) 
    customer_id = Column("customer_id", Integer, nullable=False, unique=True) 
    id = Column("id", Integer, nullable=False, unique=True) 
    customer_fname = Column("customer_fname", String(50), nullable=False)  
    customer_lname = Column("customer_lname", String(50), nullable=False)    
    customer_city = Column("customer_city", String(100), nullable=False)    
    customer_country = Column("customer_country", String(100), nullable=False)    
    customer_segment = Column("customer_segment", String(50), nullable=False)    

    def __repr__(self):
        return f"<Customer Info: id={self.customer_id}, name={self.customer_fname} {self.customer_lname}>" 


# =============================================================================
# CUSTOMER MANAGEMENT SYSTEM
# =============================================================================
class CustomerSystem:
    def __init__(self):
        self.session = session
        self.csv_path = "hexahaul_db"

        # Define mappings for CSV column names
        self.customer_column_mapping = {
            'order_item_id': 'Order Item Id',
            'customer_id': 'Customer Id',
            'id': 'id',  
            'customer_fname': 'Customer Fname',
            'customer_lname': 'Customer Lname',
            'customer_city': 'Customer City',
            'customer_country': 'Customer Country',
            'customer_segment': 'Customer Segment'
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

    def _replace_csv_record(self, file_name, order_item_id, new_data):
        """Replace a specific record in CSV file by order_id"""
        df = self._read_csv(file_name)
        
        if not df.empty:
            # Remove the old record
            df = df[df['Order Item Id'] != order_item_id]
            
            # Add the new record
            if not new_data.empty:
                df = pd.concat([df, new_data], ignore_index=True)
        else:
            df = new_data if not new_data.empty else pd.DataFrame()

        self._write_csv(file_name, df)

    def _remove_csv_record(self, file_name, order_item_id):
        """Remove a specific record from CSV file by order_item_id"""
        df = self._read_csv(file_name)
        
        if not df.empty and 'Order Item Id' in df.columns:
            # Remove records with the specified order_item_id
            df_filtered = df[df['Order Item Id'] != order_item_id]
            self._write_csv(file_name, df_filtered)
            print(f"Removed customer with order ID {order_item_id} from {file_name}")

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

    def add_complete_customer_record(self, customer_data: dict):
        """Add a complete customer record"""
        try:
            order_item_id = self._create_new_customer(customer_data)
            self.session.commit()
            print(f"Customer with Order ID {order_item_id} successfully created!")
            # Transform and update CSV files
            self._update_csv("hh_customer_info.csv", pd.DataFrame([self._map_keys_to_columns(customer_data, self.customer_column_mapping)]))
            return order_item_id
        except Exception as e:
            self.session.rollback()
            print(f"Error creating customer: {e}")
            raise

    def _create_new_customer(self, customer_data: dict):
        """Create new customer record"""

        # Assign auto-increment id for customer
        customer_data['id'] = self._get_next_id(Customer)

        # Create new record
        new_customer = Customer(**customer_data)

        # Add to session
        self.session.add(new_customer)

        return customer_data['order_item_id']

    def update_existing_customer(self, customer_data: dict):
        """Update existing customer record"""
        try:
            order_item_id = customer_data['order_item_id']
            
            # Get the existing customer
            customer = self.session.query(Customer).filter_by(order_item_id=order_item_id).first()
            if not customer:
                raise ValueError(f"Customer with Order ID {order_item_id} not found")
            
            # Store the original id to preserve it
            original_id = customer.id
            
            # CREATE A MAPPING for input keys to model attributes
            attribute_mapping = {
                'order_item_id': 'order_item_id',
                'customer_fname': 'customer_fname',
                'customer_lname': 'customer_lname',
                'customer_id': 'customer_id',
                'customer_city': 'customer_city',
                'customer_country': 'customer_country',
                'customer_segment': 'customer_segment'
            }
            
            # Update customer attributes using the mapping
            for key, value in customer_data.items():
                if key in attribute_mapping and key != 'id':  # Don't update the auto-increment id
                    model_attribute = attribute_mapping[key]
                    if hasattr(customer, model_attribute):
                        setattr(customer, model_attribute, value)
                
                # Add the original id to customer_data for CSV update
                customer_data_with_id = customer_data.copy()
                customer_data_with_id['id'] = original_id
            
            # Update CSV file - REPLACE instead of UPDATE
            self._replace_csv_record("hh_customer_info.csv", order_item_id, pd.DataFrame([self._map_keys_to_columns(customer_data_with_id, self.customer_column_mapping)]))
            
            # Commit all changes
            self.session.commit()
            print(f"Customer with Order ID {order_item_id} successfully updated!")
            return order_item_id
            
        except Exception as e:
            self.session.rollback()
            print(f"Error updating customer: {e}")
            raise

    def delete_customer_record(self, order_item_id: str):
        """Delete customer record by order_id"""
        try:
            customer = self.session.query(Customer).filter_by(order_item_id=order_item_id).first()
            if customer:
                self.session.delete(customer)
                self.session.commit()
                print(f"Customer with Order ID {order_item_id} successfully deleted!")
                
                # Remove from CSV
                self._remove_csv_record("hh_customer_info.csv", order_item_id)
                return True
            else:
                print(f"Customer with Order ID {order_item_id} not found!")
                return False
        except Exception as e:
            self.session.rollback()
            print(f"Error deleting customer: {e}")
            raise

    def get_customer_by_order_id(self, order_item_id: str):
        """Retrieve customer information by order_id"""
        customer = self.session.query(Customer).filter_by(order_item_id=order_item_id).first()
        return customer

    def close(self):
        """Close the database session"""
        self.session.close()


# =============================================================================
# INPUT FUNCTIONS
# =============================================================================

def get_customer_info():
    """Get complete customer information"""
    print("Customer Information:")
    
    while True:
        order_id = input("Order Item ID: ").strip().upper()
        if order_id:
            break
        print("Order Item ID cannot be empty")
    
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
        'order_item_id': order_id,
        'customer_fname': fname,
        'customer_lname': lname,
        'customer_id': customer_id,
        'customer_city': city,
        'customer_country': country,
        'customer_segment': segment
    }

def get_existing_customer_for_update():
    """Get existing customer for update"""
    while True:
        try:
            # Prompt user to enter an Order ID
            order_id = input("Enter Order ID to update: ").strip().upper()
        except ValueError:
            # Handle invalid input type
            print("Invalid input. Please enter a valid Order ID.")
            continue

        # Query the database for the customer with the given Order ID
        customer = session.query(Customer).filter_by(order_item_id=order_id).first()

        # If customer not found, notify user and retry
        if not customer:
            print("Customer not found. Please try again.")
            continue

        # Display basic details of the found customer
        print("\nFound Customer:")
        print(f"Order ID: {customer.order_item_id}")
        print(f"Customer ID: {customer.customer_id}")
        print(f"Name: {customer.customer_fname} {customer.customer_lname}")
        print(f"City: {customer.customer_city}")
        print(f"Country: {customer.customer_country}")
        print(f"Segment: {customer.customer_segment}")
        
        # Ask user to confirm if this is the correct customer
        confirm = input("\nIs this the customer you wish to update? (y/n): ").strip().lower()

        if confirm == 'y':
            # Get updated customer data
            print("\nPress Enter to keep current value, or enter new value to change:")
            
            # First Name
            print(f"Current First Name: {customer.customer_fname}")
            new_fname = input("New First Name (Enter to keep): ").strip().title()
            fname = new_fname if new_fname else customer.customer_fname
            
            # Last Name
            print(f"Current Last Name: {customer.customer_lname}")
            new_lname = input("New Last Name (Enter to keep): ").strip().title()
            lname = new_lname if new_lname else customer.customer_lname
            
            # Customer ID
            print(f"Current Customer ID: {customer.customer_id}")
            new_customer_id_input = input("New Customer ID (Enter to keep): ").strip()
            if new_customer_id_input:
                try:
                    customer_id = int(new_customer_id_input)
                except ValueError:
                    print("Invalid Customer ID, keeping current value")
                    customer_id = customer.customer_id
            else:
                customer_id = customer.customer_id
            
            # City
            print(f"Current City: {customer.customer_city}")
            new_city = input("New City (Enter to keep): ").strip().title()
            city = new_city if new_city else customer.customer_city
            
            # Country
            print(f"Current Country: {customer.customer_country}")
            new_country = input("New Country (Enter to keep): ").strip().title()
            country = new_country if new_country else customer.customer_country
            
            # Segment
            segments = ["Corporate", "Consumer", "Home Office", "Small Business"]
            print(f"Current Segment: {customer.customer_segment}")
            print(f"Available segments: {', '.join(segments)}")
            new_segment = input("New Segment (Enter to keep): ").strip().title()
            if new_segment and new_segment in segments:
                segment = new_segment
            elif new_segment and new_segment not in segments:
                print("Invalid segment, keeping current value")
                segment = customer.customer_segment
            else:
                segment = customer.customer_segment
            
            return {
                'order_item_id': order_id,
                'customer_fname': fname,
                'customer_lname': lname,
                'customer_id': customer_id,
                'customer_city': city,
                'customer_country': country,
                'customer_segment': segment
            }
            
        elif confirm == 'n':
            # If not confirmed, loop again
            continue
        else:
            # Handle unexpected input
            print("Please enter 'y' or 'n'")


# =============================================================================
# MAIN FUNCTIONS
# =============================================================================

def display_customer_summary(customer_data):
    """Display a summary of the customer before confirmation"""
    print("\n" + "="*60)
    print("                CUSTOMER SUMMARY")
    print("="*60)
    print(f"Order ID: {customer_data['order_item_id']}")
    print(f"Customer ID: {customer_data['customer_id']}")
    print(f"Name: {customer_data['customer_fname']} {customer_data['customer_lname']}")
    print(f"City: {customer_data['customer_city']}")
    print(f"Country: {customer_data['customer_country']}")
    print(f"Segment: {customer_data['customer_segment']}")
    print("="*60)


def main():
    """Main function to run the customer management system"""
    customer_system = CustomerSystem()
    
    try:
        while True:
            print("\nCustomer Management System")
            print("1. Create New Customer")
            print("2. Update Existing Customer")
            print("3. View Customer")
            print("4. Delete Customer")
            print("5. Exit")
            
            choice = input("\nSelect option (1-5): ").strip()
            
            if choice == '1':
                try:
                    customer_data = get_customer_info()
                    
                    # Check if customer with this order_id already exists
                    existing_customer = customer_system.get_customer_by_order_id(customer_data['order_item_id'])
                    if existing_customer:
                        print(f"Customer with Order ID {customer_data['order_item_id']} already exists!")
                        continue
                    
                    display_customer_summary(customer_data)
                    
                    confirm = input("\nConfirm customer creation? (y/n): ").lower().strip()
                    if confirm in ['y', 'yes']:
                        customer_system.add_complete_customer_record(customer_data)
                    else:
                        print("Customer creation cancelled")
                except Exception as e:
                    print(f"Error creating customer: {e}")

            elif choice == '2':
                try:
                    customer_data = get_existing_customer_for_update()
                    if customer_data:
                        display_customer_summary(customer_data)
                        
                        confirm = input("\nConfirm customer update? (y/n): ").lower().strip()
                        if confirm in ['y', 'yes']:
                            customer_system.update_existing_customer(customer_data)
                        else:
                            print("Customer update cancelled")

                except Exception as e:
                    print(f"Error updating customer: {e}")
            
            elif choice == '3':
                order_id = input("Enter Order ID to view: ").strip().upper()
                customer = customer_system.get_customer_by_order_id(order_id)
                if customer:
                    print(f"\n{customer}")
                else:
                    print("Customer not found")
            
            elif choice == '4':
                order_id = input("Enter Order ID to delete: ").strip().upper()
                customer = customer_system.get_customer_by_order_id(order_id)
                if customer:
                    print(f"\nCustomer to delete: {customer.customer_fname} {customer.customer_lname} (ID: {customer.customer_id})")
                    confirm = input(f"Confirm deletion of customer with Order ID {order_id}? (y/n): ").lower().strip()
                    if confirm in ['y', 'yes']:
                        customer_system.delete_customer_record(order_id)
                else:
                    print("Customer not found")
            
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
        customer_system.close()


# =============================================================================
# ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    main()