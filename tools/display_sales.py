import csv
import os
import pandas as pd
from datetime import datetime

def display_formatted_sales():
    """
    Display selected columns from the sales data CSV file in a formatted table
    """
    # Path to the CSV file
    csv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                           'hexahaul_db', 'hh_sales.csv')
    
    # Read data using pandas for better formatting options
    try:
        # Read the CSV file
        df = pd.read_csv(csv_path)
        
        # Select and rename the columns we want to display
        selected_data = df[[
            'Order Item Id', 
            'Type', 
            'Order Item Product Price', 
            'Order Item Quantity', 
            'Order Profit Per Order',
            'order date (DateOrders)'
        ]]
        
        # Rename columns for better display
        selected_data.columns = [
            'Order ID', 
            'Payment Type', 
            'Product Price ($)', 
            'Quantity', 
            'Profit ($)',
            'Order Date'
        ]
        
        # Format currency columns
        selected_data['Product Price ($)'] = selected_data['Product Price ($)'].map('${:,.2f}'.format)
        selected_data['Profit ($)'] = selected_data['Profit ($)'].map('${:,.2f}'.format)
        
        # Format the date column
        selected_data['Order Date'] = pd.to_datetime(selected_data['Order Date']).dt.strftime('%Y-%m-%d')
        
        # Display the formatted data
        print("\n=== HexaHaul Sales Data ===\n")
        print(selected_data.to_string(index=False))
        print(f"\nTotal records: {len(selected_data)}")
        
    except Exception as e:
        print(f"Error processing sales data: {e}")

if __name__ == "__main__":
    display_formatted_sales()
