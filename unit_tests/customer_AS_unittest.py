# Import tools for testing
import unittest
from unittest.mock import MagicMock, patch  # MagicMock fakes objects; patch temporarily replaces things like input()

# Import your system and input functions to test
from customer_admin_system import CustomerSystem, Customer
from customer_admin_system import get_customer_info, get_existing_customer_for_update

# Test class for the main CustomerSystem
class TestCustomerSystem(unittest.TestCase):

    # This runs before each test
    def setUp(self):
        self.system = CustomerSystem()
        self.system.session = MagicMock()  # Fake the database session
        self.system._get_next_id = MagicMock(return_value=1)  # Fake next ID
        self.system._update_csv = MagicMock()  # Fake CSV writing
        self.system._replace_csv_record = MagicMock()
        self.system._remove_csv_record = MagicMock()

    # Test adding a customer
    def test_add_complete_customer_record(self):
        customer_data = {
            'order_item_id': 'ORD001',
            'customer_id': 100,
            'customer_fname': 'Alice',
            'customer_lname': 'Smith',
            'customer_city': 'NYC',
            'customer_country': 'USA',
            'customer_segment': 'Retail'
        }
        result = self.system.add_complete_customer_record(customer_data)

        self.assertEqual(result, 'ORD001')  # Check the result
        self.system.session.add.assert_called_once()  # Check if customer was added to DB
        self.system.session.commit.assert_called_once()  # Check if DB saved
        self.system._update_csv.assert_called_once()  # Check if CSV was updated

    # Test updating a customer
    def test_update_existing_customer(self):
        mock_customer = MagicMock(spec=Customer, id=5)  # Fake an existing customer
        self.system.session.query().filter_by().first.return_value = mock_customer

        customer_data = {
            'order_item_id': 'ORD002',
            'customer_id': 101,
            'customer_fname': 'Bob',
            'customer_lname': 'Jones',
            'customer_city': 'LA',
            'customer_country': 'USA',
            'customer_segment': 'Wholesale'
        }
        result = self.system.update_existing_customer(customer_data)

        self.assertEqual(result, 'ORD002')  # Check the result
        self.system.session.commit.assert_called_once()  # Check if DB saved
        self.system._replace_csv_record.assert_called_once()  # Check if CSV was updated

    # Test deleting a customer
    def test_delete_customer_record(self):
        mock_customer = MagicMock(spec=Customer)  # Fake a customer to delete
        self.system.session.query().filter_by().first.return_value = mock_customer
        result = self.system.delete_customer_record('ORD003')

        self.assertTrue(result)  # Should return True if deleted
        self.system.session.delete.assert_called_once()  # DB delete called
        self.system.session.commit.assert_called_once()  # DB commit called
        self.system._remove_csv_record.assert_called_once()  # CSV update called

    # Test deleting a customer that doesn't exist
    def test_delete_customer_record_not_found(self):
        self.system.session.query().filter_by().first.return_value = None  # No customer found
        result = self.system.delete_customer_record('NONEXISTENT')

        self.assertFalse(result)  # Should return False
        self.system.session.commit.assert_not_called()  # No commit since nothing deleted
        self.system._remove_csv_record.assert_not_called()  # No CSV update

    # Test searching by order ID
    def test_get_customer_by_order_id(self):
        mock_customer = MagicMock(spec=Customer)
        self.system.session.query().filter_by().first.return_value = mock_customer
        result = self.system.get_customer_by_order_id('ORD004')
        self.assertEqual(result, mock_customer)  # Should return the customer

    # Test closing the system
    def test_close(self):
        self.system.session.close = MagicMock()  # Fake close method
        self.system.close()
        self.system.session.close.assert_called_once()  # Check that close was called


# Run all tests
if __name__ == '__main__':
    unittest.main()
