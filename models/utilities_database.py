import sqlite3
import json
import os
from datetime import datetime, timedelta
import random

class UtilitiesDatabase:
    def __init__(self, db_path):
        # Ensure the database directory exists
        self.db_path = db_path
        os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)
        
        # Create the database and tables if they don't exist
        self.initialize_database()
    
    def get_connection(self):
        try:
            # Make sure we're using an absolute path for more reliable connections
            abs_path = os.path.abspath(self.db_path)
            return sqlite3.connect(abs_path)
        except sqlite3.OperationalError as e:
            print(f"Database connection error: {e}")
            print(f"Attempted to connect to: {os.path.abspath(self.db_path)}")
            print(f"Directory exists: {os.path.exists(os.path.dirname(os.path.abspath(self.db_path)))}")
            print(f"File exists: {os.path.exists(os.path.abspath(self.db_path))}")
            print(f"Current working directory: {os.getcwd()}")
            
            # Fall back to in-memory database in case of error
            print("Falling back to in-memory database")
            return sqlite3.connect(":memory:")
    
    def initialize_database(self):
        """Create necessary tables if they don't exist"""
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Create tables for utilities if they don't exist
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sales (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT,
                    product_name TEXT,
                    category TEXT,
                    quantity INTEGER,
                    revenue REAL,
                    cost REAL
                )
            """)
            
            # Add more table creation statements as needed
            
            conn.commit()
            print(f"Database initialized successfully at {self.db_path}")
        except Exception as e:
            print(f"Error initializing database: {e}")
        finally:
            if conn:
                conn.close()
    
    def get_dashboard_stats(self):
        """
        Get summary statistics for the dashboard
        
        Returns:
            dict: Summary statistics
        """
        try:
            conn = self.get_connection()
            try:
                # In a real app, you would query your database for actual stats
                # For now, we'll return mock data
                
                return {
                    "total_revenue": 238492,
                    "deliveries": 1284,
                    "customers": 392,
                    "hexaboxes": 768
                }
            finally:
                conn.close()
        except Exception as e:
            print(f"Error getting dashboard stats: {e}")
            # Return fallback data in case of error
            return {
                "total_revenue": 238492,
                "deliveries": 1284,
                "customers": 392,
                "hexaboxes": 768
            }
    
    def get_sales_data(self, time_range="month"):
        """
        Get sales data for the specified time range
        
        Args:
            time_range (str): The time range to get data for (week, month, quarter, year)
            
        Returns:
            dict: Sales data formatted for Chart.js
        """
        try:
            # Calculate start date based on time range
            today = datetime.now()
            if time_range == "week":
                start_date = today - timedelta(days=7)
                date_format = "%a"  # Day of week
            elif time_range == "month":
                start_date = today - timedelta(days=30)
                date_format = "%d %b"  # Day and month
            elif time_range == "quarter":
                start_date = today - timedelta(days=90)
                date_format = "%b"  # Month
            elif time_range == "year":
                start_date = today - timedelta(days=365)
                date_format = "%b %Y"  # Month and year
            else:
                start_date = today - timedelta(days=30)  # Default to month
                date_format = "%d %b"
            
            conn = self.get_connection()
            try:
                # In a real app, you would query your sales table
                # For example:
                '''
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT 
                        strftime(?, date) as period,
                        SUM(revenue) as revenue,
                        SUM(cost) as cost,
                        SUM(revenue - cost) as profit
                    FROM sales
                    WHERE date BETWEEN ? AND ?
                    GROUP BY period
                    ORDER BY date
                """, (date_format, start_date.strftime("%Y-%m-%d"), today.strftime("%Y-%m-%d")))
                
                results = cursor.fetchall()
                
                labels = []
                revenue = []
                costs = []
                profit = []
                
                for row in results:
                    labels.append(row[0])
                    revenue.append(row[1])
                    costs.append(row[2])
                    profit.append(row[3])
                '''
                
                # Mock data for demonstration
                if time_range == "week":
                    labels = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
                elif time_range == "month":
                    labels = [f"{i} {(today - timedelta(days=30-i)).strftime('%b')}" for i in range(1, 31, 3)]
                elif time_range == "quarter":
                    labels = ["Jan", "Feb", "Mar"]
                else:  # year
                    labels = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", 
                              "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
                
                # Generate realistic looking sales data with upward trend
                revenue = []
                costs = []
                profit = []
                
                base_revenue = 18000
                growth_factor = 1.05
                
                for i in range(len(labels)):
                    # Add some randomness but maintain growth trend
                    rev = base_revenue * (growth_factor ** i) * (0.9 + random.random() * 0.2)
                    rev = round(rev)
                    cost = rev * (0.55 + random.random() * 0.1)  # Costs 55-65% of revenue
                    cost = round(cost)
                    prof = rev - cost
                    
                    revenue.append(rev)
                    costs.append(cost)
                    profit.append(prof)
                
                return {
                    "labels": labels,
                    "datasets": [
                        {
                            "label": "Revenue",
                            "data": revenue,
                            "borderColor": "#4361ee",
                            "backgroundColor": "rgba(67, 97, 238, 0.1)",
                            "tension": 0.3
                        },
                        {
                            "label": "Costs",
                            "data": costs,
                            "borderColor": "#f44336",
                            "backgroundColor": "rgba(244, 67, 54, 0.1)",
                            "tension": 0.3
                        },
                        {
                            "label": "Profit",
                            "data": profit,
                            "borderColor": "#4caf50",
                            "backgroundColor": "rgba(76, 175, 80, 0.1)",
                            "tension": 0.3
                        }
                    ]
                }
            finally:
                conn.close()
        except Exception as e:
            print(f"Error getting sales data: {e}")
            # Return fallback data in case of error
            return {
                "labels": [],
                "datasets": []
            }
    
    def get_vehicle_status_data(self):
        """
        Get vehicle status distribution data
        
        Returns:
            dict: Vehicle status data formatted for Chart.js
        """
        try:
            conn = self.get_connection()
            try:
                # In a real app, you would query your vehicles table
                # For example:
                '''
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT 
                        status,
                        COUNT(*) as count
                    FROM vehicles
                    GROUP BY status
                """)
                
                results = cursor.fetchall()
                
                labels = []
                counts = []
                
                for row in results:
                    labels.append(row[0])
                    counts.append(row[1])
                '''
                
                # Mock data for demonstration
                labels = ["Available", "In Use", "Maintenance"]
                counts = [42, 28, 12]
                
                return {
                    "labels": labels,
                    "datasets": [
                        {
                            "data": counts,
                            "backgroundColor": [
                                "rgba(76, 175, 80, 0.7)",
                                "rgba(255, 152, 0, 0.7)",
                                "rgba(244, 67, 54, 0.7)"
                            ],
                            "borderColor": [
                                "rgba(76, 175, 80, 1)",
                                "rgba(255, 152, 0, 1)",
                                "rgba(244, 67, 54, 1)"
                            ],
                            "borderWidth": 1
                        }
                    ]
                }
            finally:
                conn.close()
        except Exception as e:
            print(f"Error getting vehicle status data: {e}")
            # Return fallback data in case of error
            return {
                "labels": [],
                "datasets": []
            }
    
    def get_employee_performance_data(self):
        """
        Get employee performance data by department
        
        Returns:
            dict: Employee performance data formatted for Chart.js
        """
        try:
            conn = self.get_connection()
            try:
                # In a real app, you would query your employees table
                # For example:
                '''
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT 
                        department,
                        AVG(performance_score) as avg_score
                    FROM employees
                    GROUP BY department
                """)
                
                results = cursor.fetchall()
                
                departments = []
                scores = []
                
                for row in results:
                    departments.append(row[0])
                    scores.append(row[1])
                '''
                
                # Mock data for demonstration
                departments = ["Drivers", "Warehouse", "Admin", "Support", "Management"]
                scores = [85, 78, 92, 88, 82]
                
                return {
                    "labels": departments,
                    "datasets": [
                        {
                            "label": "Performance Score",
                            "data": scores,
                            "backgroundColor": "rgba(67, 97, 238, 0.7)",
                            "borderColor": "rgba(67, 97, 238, 1)",
                            "borderWidth": 1
                        }
                    ]
                }
            finally:
                conn.close()
        except Exception as e:
            print(f"Error getting employee performance data: {e}")
            # Return fallback data in case of error
            return {
                "labels": [],
                "datasets": []
            }
    
    def get_customer_growth_data(self, time_range="month"):
        """
        Get customer growth data for the specified time range
        
        Args:
            time_range (str): The time range to get data for (week, month, quarter, year)
            
        Returns:
            dict: Customer growth data formatted for Chart.js
        """
        try:
            # Calculate start date based on time range
            today = datetime.now()  # Add this line to define 'today'
            if time_range == "week":
                start_date = today - timedelta(days=7)
                date_format = "%a"  # Day of week
            elif time_range == "month":
                start_date = today - timedelta(days=30)
                date_format = "%d %b"  # Day and month
            elif time_range == "quarter":
                start_date = today - timedelta(days=90)
                date_format = "%b"  # Month
            elif time_range == "year":
                start_date = today - timedelta(days=365)
                date_format = "%b %Y"  # Month and year
            else:
                start_date = today - timedelta(days=30)  # Default to month
                date_format = "%d %b"
            
            conn = self.get_connection()
            try:
                # In a real app, you would query your customers and orders tables
                # For example:
                '''
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT 
                        strftime(?, registration_date) as period,
                        COUNT(*) as new_customers,
                        (SELECT COUNT(DISTINCT customer_id) 
                         FROM orders 
                         WHERE order_date BETWEEN ? AND ?
                         AND customer_id IN (
                             SELECT id 
                             FROM customers 
                             WHERE registration_date < ?
                         )) as repeat_customers
                    FROM customers
                    WHERE registration_date BETWEEN ? AND ?
                    GROUP BY period
                    ORDER BY registration_date
                """, (date_format, start_date.strftime("%Y-%m-%d"), today.strftime("%Y-%m-%d"), 
                      start_date.strftime("%Y-%m-%d"), start_date.strftime("%Y-%m-%d"), 
                      today.strftime("%Y-%m-%d")))
                
                results = cursor.fetchall()
                
                periods = []
                new_customers = []
                repeat_customers = []
                
                for row in results:
                    periods.append(row[0])
                    new_customers.append(row[1])
                    repeat_customers.append(row[2])
                '''
                
                # Mock data for demonstration
                if time_range == "week":
                    periods = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
                elif time_range == "month":
                    periods = [f"{i} {(today - timedelta(days=30-i)).strftime('%b')}" for i in range(1, 31, 3)]
                elif time_range == "quarter":
                    periods = ["Jan", "Feb", "Mar"]
                else:  # year
                    periods = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", 
                              "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
                
                # Generate realistic customer growth data
                new_customers = []
                repeat_customers = []
                
                base_new = 20
                base_repeat = 45
                
                for i in range(len(periods)):
                    # Add some randomness but maintain growth trend
                    new = base_new + (i * 2) + random.randint(-5, 5)
                    repeat = base_repeat + (i * 4) + random.randint(-8, 8)
                    
                    new_customers.append(max(0, new))
                    repeat_customers.append(max(0, repeat))
                
                return {
                    "labels": periods,
                    "datasets": [
                        {
                            "label": "New Customers",
                            "data": new_customers,
                            "borderColor": "#4361ee",
                            "backgroundColor": "rgba(67, 97, 238, 0.1)",
                            "tension": 0.3
                        },
                        {
                            "label": "Repeat Customers",
                            "data": repeat_customers,
                            "borderColor": "#4caf50",
                            "backgroundColor": "rgba(76, 175, 80, 0.1)",
                            "tension": 0.3
                        }
                    ]
                }
            finally:
                conn.close()
        except Exception as e:
            print(f"Error getting customer growth data: {e}")
            # Return fallback data in case of error
            return {
                "labels": [],
                "datasets": []
            }
    
    def get_sales_detail_data(self, time_range="month", limit=20):
        """
        Get detailed sales data for table display
        
        Args:
            time_range (str): The time range to get data for (week, month, quarter, year)
            limit (int): Maximum number of rows to return
            
        Returns:
            list: List of sales data dictionaries
        """
        # Calculate start date based on time range
        today = datetime.now()
        if time_range == "week":
            start_date = today - timedelta(days=7)
        elif time_range == "month":
            start_date = today - timedelta(days=30)
        elif time_range == "quarter":
            start_date = today - timedelta(days=90)
        elif time_range == "year":
            start_date = today - timedelta(days=365)
        else:
            start_date = today - timedelta(days=30)  # Default to month
        
        conn = self.get_connection()
        try:
            # In a real app, you would query your sales table
            # For example:
            '''
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    date,
                    product_name,
                    category,
                    quantity,
                    revenue,
                    cost,
                    (revenue - cost) as profit
                FROM sales
                WHERE date BETWEEN ? AND ?
                ORDER BY date DESC
                LIMIT ?
            """, (start_date.strftime("%Y-%m-%d"), today.strftime("%Y-%m-%d"), limit))
            
            results = cursor.fetchall()
            
            sales_data = []
            for row in results:
                sales_data.append({
                    "date": row[0],
                    "product": row[1],
                    "category": row[2],
                    "quantity": row[3],
                    "revenue": row[4],
                    "cost": row[5],
                    "profit": row[6]
                })
            '''
            
            # Mock data for demonstration
            products = [
                {"name": "Express Delivery", "category": "Service"},
                {"name": "Bulk Transport", "category": "Service"},
                {"name": "HexaBox Rental", "category": "Product"},
                {"name": "Warehouse Storage", "category": "Service"},
                {"name": "International Shipping", "category": "Service"},
                {"name": "Packaging Materials", "category": "Product"}
            ]
            
            sales_data = []
            
            # Generate dates within the time range
            date_range = (today - start_date).days
            
            for i in range(limit):
                # Random date within range
                days_ago = random.randint(0, date_range)
                sale_date = today - timedelta(days=days_ago)
                
                # Random product
                product = random.choice(products)
                
                # Random quantity between 1 and 200
                quantity = random.randint(1, 200)
                
                # Calculate financials
                unit_price = random.randint(20, 100)
                revenue = quantity * unit_price
                cost = revenue * (0.55 + random.random() * 0.1)  # Costs 55-65% of revenue
                profit = revenue - cost
                
                sales_data.append({
                    "date": sale_date.strftime("%Y-%m-%d"),
                    "product": product["name"],
                    "category": product["category"],
                    "quantity": quantity,
                    "revenue": round(revenue),
                    "cost": round(cost),
                    "profit": round(profit)
                })
            
            # Sort by date (newest first)
            sales_data.sort(key=lambda x: x["date"], reverse=True)
            
            return sales_data
        finally:
            conn.close()
    
    def get_vehicle_detail_data(self):
        """
        Get detailed vehicle data for table display
        
        Returns:
            list: List of vehicle data dictionaries
        """
        try:
            today = datetime.now()  # Add this line to define 'today'
            conn = self.get_connection()
            try:
                # In a real app, you would query your vehicles table
                # For example:
                '''
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT 
                        id,
                        unit_type,
                        unit_brand,
                        unit_model,
                        status,
                        distance,
                        CASE
                            WHEN distance < 5000 THEN 'Excellent'
                            WHEN distance < 20000 THEN 'Good'
                            WHEN distance < 50000 THEN 'Fair'
                            ELSE 'Poor'
                        END as efficiency,
                        last_maintenance_date
                    FROM vehicles
                    ORDER BY id
                """)
                
                results = cursor.fetchall()
                
                vehicle_data = []
                for row in results:
                    vehicle_data.append({
                        "id": row[0],
                        "type": row[1],
                        "brand": row[2],
                        "model": row[3],
                        "status": row[4],
                        "distance": row[5],
                        "efficiency": row[6],
                        "last_maintenance": row[7]
                    })
                '''
                
                # Mock data for demonstration
                types = ["Car", "Truck", "Motorcycle"]
                brands = {
                    "Car": ["Toyota", "Honda", "Nissan", "Ford", "Tesla"],
                    "Truck": ["Volvo", "Mercedes", "Scania", "MAN", "Iveco"],
                    "Motorcycle": ["Honda", "Yamaha", "Kawasaki", "Ducati", "Harley-Davidson"]
                }
                models = {
                    "Toyota": ["Corolla", "Camry", "Prius", "RAV4"],
                    "Honda": ["Civic", "Accord", "CR-V", "CB500"],
                    "Nissan": ["Leaf", "Altima", "Rogue", "Sentra"],
                    "Ford": ["F-150", "Focus", "Escape", "Mustang"],
                    "Tesla": ["Model 3", "Model S", "Model X", "Model Y"],
                    "Volvo": ["FH16", "FM", "FE", "FL"],
                    "Mercedes": ["Actros", "Arocs", "Atego", "Axor"],
                    "Scania": ["R Series", "S Series", "G Series", "P Series"],
                    "MAN": ["TGX", "TGS", "TGM", "TGL"],
                    "Iveco": ["S-Way", "Eurocargo", "Daily", "Stralis"],
                    "Yamaha": ["MT-07", "R1", "R6", "YZF"],
                    "Kawasaki": ["Ninja", "Z900", "Versys", "Vulcan"],
                    "Ducati": ["Panigale", "Monster", "Multistrada", "Scrambler"],
                    "Harley-Davidson": ["Sportster", "Softail", "Touring", "Street"]
                }
                statuses = ["Available", "In Use", "Maintenance"]
                efficiency_ratings = ["Excellent", "Good", "Fair", "Poor"]
                
                vehicle_data = []
                
                for i in range(1, 16):
                    # Random vehicle type
                    v_type = random.choice(types)
                    
                    # Random brand based on type
                    brand = random.choice(brands[v_type])
                    
                    # Random model based on brand
                    model = random.choice(models[brand])
                    
                    # Random status
                    status = random.choice(statuses)
                    
                    # Random distance
                    distance = random.randint(1000, 50000)
                    
                    # Efficiency based on distance
                    if distance < 5000:
                        efficiency = "Excellent"
                    elif distance < 20000:
                        efficiency = "Good"
                    elif distance < 50000:
                        efficiency = "Fair"
                    else:
                        efficiency = "Poor"
                    
                    # Random maintenance date within last 6 months
                    days_ago = random.randint(0, 180)
                    maintenance_date = (today - timedelta(days=days_ago)).strftime("%Y-%m-%d")
                    
                    vehicle_data.append({
                        "id": f"V{i:03d}",
                        "type": v_type,
                        "brand": brand,
                        "model": model,
                        "status": status,
                        "distance": distance,
                        "efficiency": efficiency,
                        "last_maintenance": maintenance_date
                    })
                
                return vehicle_data
            finally:
                conn.close()
        except Exception as e:
            print(f"Error getting vehicle detail data: {e}")
            # Return fallback data in case of error
            return []
    
    def get_employee_detail_data(self):
        """
        Get detailed employee data for table display
        
        Returns:
            list: List of employee data dictionaries
        """
        conn = self.get_connection()
        try:
            # In a real app, you would query your employees table
            # For example:
            '''
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    id,
                    name,
                    position,
                    department,
                    performance_score,
                    tasks_completed,
                    CASE
                        WHEN performance_score >= 90 THEN 'High'
                        WHEN performance_score >= 75 THEN 'Medium'
                        ELSE 'Low'
                    END as efficiency,
                    status
                FROM employees
                ORDER BY id
            """)
            
            results = cursor.fetchall()
            
            employee_data = []
            for row in results:
                employee_data.append({
                    "id": row[0],
                    "name": row[1],
                    "position": row[2],
                    "department": row[3],
                    "performance": row[4],
                    "tasks_completed": row[5],
                    "efficiency": row[6],
                    "status": row[7]
                })
            '''
            
            # Mock data for demonstration
            first_names = ["John", "Jane", "Bob", "Alice", "Charlie", "David", "Emma", "Frank", "Grace", "Henry"]
            last_names = ["Smith", "Johnson", "Williams", "Jones", "Brown", "Davis", "Miller", "Wilson", "Moore", "Taylor"]
            positions = {
                "Delivery": ["Driver", "Courier", "Fleet Manager"],
                "Logistics": ["Warehouse Staff", "Inventory Manager", "Logistics Coordinator"],
                "Operations": ["Manager", "Supervisor", "Analyst"],
                "Support": ["Customer Service", "Technical Support", "IT Specialist"]
            }
            departments = ["Delivery", "Logistics", "Operations", "Support"]
            statuses = ["Active", "On Leave", "Training"]
            
            employee_data = []
            
            for i in range(1, 16):
                # Random name
                first_name = random.choice(first_names)
                last_name = random.choice(last_names)
                name = f"{first_name} {last_name}"
                
                # Random department
                department = random.choice(departments)
                
                # Random position based on department
                position = random.choice(positions[department])
                
                # Random performance score
                performance = random.randint(70, 98)
                
                # Random tasks completed
                tasks = random.randint(50, 150)
                
                # Efficiency based on performance
                if performance >= 90:
                    efficiency = "High"
                elif performance >= 75:
                    efficiency = "Medium"
                else:
                    efficiency = "Low"
                
                # Random status
                status = random.choice(statuses)
                
                employee_data.append({
                    "id": f"E{i:03d}",
                    "name": name,
                    "position": position,
                    "department": department,
                    "performance": f"{performance}%",
                    "tasks_completed": tasks,
                    "efficiency": efficiency,
                    "status": status
                })
            
            return employee_data
        finally:
            conn.close()
    
    def generate_report(self, report_type, time_range, report_format):
        """
        Generate a report based on specified parameters
        
        Args:
            report_type (str): Type of report to generate
            time_range (str): Time range for the report
            report_format (str): Format of the report (pdf, excel, csv)
            
        Returns:
            dict: Report generation status
        """
        # In a real app, this would generate a file and return a download link
        # For now, we'll just return a success message
        
        return {
            "status": "success",
            "message": f"{report_type.capitalize()} report for {time_range} period has been generated in {report_format.upper()} format.",
            "download_link": f"/reports/{report_type}_{time_range}_{datetime.now().strftime('%Y%m%d%H%M%S')}.{report_format}"
        }
