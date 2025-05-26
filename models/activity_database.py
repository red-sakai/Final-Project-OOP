import csv
import os
from datetime import datetime
from typing import List, Dict, Optional

class ActivityDatabase:
    def __init__(self, csv_path: str = None):
        if csv_path is None:
            csv_path = os.path.join('hexahaul_db', 'hh_activity.csv')
        self.csv_path = csv_path
        self._ensure_csv_exists()
    
    def _ensure_csv_exists(self):
        """Ensure the CSV file exists with proper headers"""
        os.makedirs(os.path.dirname(self.csv_path), exist_ok=True)
        
        if not os.path.exists(self.csv_path):
            with open(self.csv_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['Username', 'Email', 'Activity_Type', 'Activity_Description', 'Timestamp', 'IP_Address', 'User_Agent'])
    
    def log_activity(self, username: str, email: str, activity_type: str, description: str, ip_address: str = '', user_agent: str = ''):
        """Log a user activity to the CSV file"""
        try:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            with open(self.csv_path, 'a', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow([username, email, activity_type, description, timestamp, ip_address, user_agent])
            
            return True
        except Exception as e:
            print(f"Error logging activity: {e}")
            return False
    
    def get_user_activities(self, username: str = None, email: str = None, limit: int = 50) -> List[Dict]:
        """Get activities for a specific user"""
        activities = []
        
        try:
            with open(self.csv_path, 'r', newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    # Filter by username or email
                    if username and row['Username'] == username:
                        activities.append(row)
                    elif email and row['Email'] == email:
                        activities.append(row)
                    elif not username and not email:
                        activities.append(row)
        except FileNotFoundError:
            return []
        except Exception as e:
            print(f"Error reading activities: {e}")
            return []
        
        # Sort by timestamp (newest first) and limit results
        activities.sort(key=lambda x: x['Timestamp'], reverse=True)
        return activities[:limit]
    
    def get_login_history(self, username: str = None, email: str = None, limit: int = 10) -> List[Dict]:
        """Get login history for a specific user"""
        all_activities = self.get_user_activities(username, email)
        login_activities = [
            activity for activity in all_activities 
            if activity['Activity_Type'] == 'LOGIN'
        ]
        return login_activities[:limit]
    
    def get_recent_activities(self, username: str = None, email: str = None, days: int = 30, limit: int = 20) -> List[Dict]:
        """Get recent activities for a user within specified days"""
        from datetime import datetime, timedelta
        
        cutoff_date = datetime.now() - timedelta(days=days)
        all_activities = self.get_user_activities(username, email)
        
        recent_activities = []
        for activity in all_activities:
            try:
                activity_date = datetime.strptime(activity['Timestamp'], '%Y-%m-%d %H:%M:%S')
                if activity_date >= cutoff_date:
                    recent_activities.append(activity)
            except ValueError:
                continue
        
        return recent_activities[:limit]
    
    def format_activity_for_display(self, activity: Dict) -> Dict:
        """Format activity data for display in the frontend"""
        try:
            timestamp = datetime.strptime(activity['Timestamp'], '%Y-%m-%d %H:%M:%S')
            formatted_date = timestamp.strftime('%A %d %B, %Y')
            formatted_time = timestamp.strftime('%I:%M %p')
            
            return {
                'date': formatted_date,
                'time': formatted_time,
                'activity_type': activity['Activity_Type'],
                'description': activity['Activity_Description'],
                'full_timestamp': activity['Timestamp']
            }
        except Exception:
            return {
                'date': 'Unknown date',
                'time': 'Unknown time',
                'activity_type': activity.get('Activity_Type', 'Unknown'),
                'description': activity.get('Activity_Description', 'Unknown activity'),
                'full_timestamp': activity.get('Timestamp', '')
            }
