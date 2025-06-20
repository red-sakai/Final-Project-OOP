import unittest
from unittest.mock import MagicMock
import pandas as pd
from product_admin_system import ProductSystem, Product

class TestProductSystem(unittest.TestCase):

    def setUp(self):
        """Set up a new ProductSystem instance and mock the session."""
        self.system = ProductSystem()
        self.system.session = MagicMock()  # Mock the database session
        self.system._write_csv = MagicMock()  # Mock CSV writing
        self.system._read_csv = MagicMock(return_value=pd.DataFrame())  # Mock CSV reading

    def test_add_complete_product_record(self):
        """Test adding a complete product record."""
        product_data = {
            'product_id': 'PROD001',
            'product_name': 'Test Product',
            'product_category_id': 1,
            'product_category_name': 'Test Category',
            'dep_id': 1,
            'dep_name': 'Test Department'
        }
        
        # Mock the _create_new_product method to return the product_id
        self.system._create_new_product = MagicMock(return_value='PROD001')
        
        result = self.system.add_complete_product_record(product_data)
        
        self.assertEqual(result, 'PROD001')  # Check if the returned ID is correct
        self.system.session.commit.assert_called_once()  # Ensure commit was called
        self.system._write_csv.assert_called_once()  # Ensure CSV write was called

    def test_update_existing_product(self):
        """Test updating an existing product record."""
        product_data = {
            'product_id': 'PROD001',
            'product_name': 'Updated Product',
            'product_category_id': 1,
            'product_category_name': 'Updated Category',
            'dep_id': 1,
            'dep_name': 'Updated Department'
        }
        
        # Mock the existing product retrieval
        mock_product = MagicMock(spec=Product)
        self.system.session.query().filter_by().first.return_value = mock_product
        
        result = self.system.update_existing_product(product_data)
        
        self.assertEqual(result, 'PROD001')  # Check if the returned ID is correct
        self.system.session.commit.assert_called_once()  # Ensure commit was called
        self.system._write_csv.assert_called_once()  # Ensure CSV write was called

    def test_delete_product_record(self):
        """Test deleting a product record."""
        mock_product = MagicMock(spec=Product)
        self.system.session.query().filter_by().first.return_value = mock_product
        
        result = self.system.delete_product_record('PROD001')
        
        self.assertTrue(result)  # Check if the deletion was successful
        self.system.session.delete.assert_called_once()  # Ensure delete was called
        self.system.session.commit.assert_called_once()  # Ensure commit was called

    def test_delete_product_record_not_found(self):
        """Test deleting a product record that does not exist."""
        self.system.session.query().filter_by().first.return_value = None
        
        result = self.system.delete_product_record('NONEXISTENT')
        
        self.assertFalse(result)  # Check if the deletion was unsuccessful
        self.system.session.commit.assert_not_called()  # Ensure commit was not called

    def test_get_product_by_id(self):
        """Test retrieving a product by ID."""
        mock_product = MagicMock(spec=Product)
        self.system.session.query().filter_by().first.return_value = mock_product
        
        result = self.system.get_product_by_id('PROD001')
        
        self.assertEqual(result, mock_product)  # Check if the returned product is correct

    def test_close(self):
        """Test closing the database session."""
        self.system.session.close = MagicMock()  # Mock the close method
        self.system.close()
        self.system.session.close.assert_called_once()  # Ensure close was called

if __name__ == '__main__':
    unittest.main()
