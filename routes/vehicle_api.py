from flask import Blueprint, request, jsonify
from models.vehicle_database import VehicleDatabase

# Create a Blueprint for the vehicle API
vehicle_api = Blueprint('vehicle_api', __name__)
vehicle_db = None

# Initialize the vehicle database
def initialize_vehicle_db():
    global vehicle_db
    vehicle_db = VehicleDatabase()
    # Add sample data if the database is empty
    vehicle_db.initialize_sample_data()

# Get all vehicles
@vehicle_api.route('/api/vehicles', methods=['GET'])
def get_vehicles():
    global vehicle_db
    if not vehicle_db:
        initialize_vehicle_db()
    
    try:
        vehicles = vehicle_db.get_all_vehicles()
        return jsonify(vehicles), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Get a specific vehicle by ID
@vehicle_api.route('/api/vehicles/<int:vehicle_id>', methods=['GET'])
def get_vehicle(vehicle_id):
    global vehicle_db
    if not vehicle_db:
        initialize_vehicle_db()
    
    try:
        vehicle = vehicle_db.get_vehicle_by_id(vehicle_id)
        if vehicle:
            return jsonify(vehicle), 200
        return jsonify({'error': 'Vehicle not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Create a new vehicle
@vehicle_api.route('/api/vehicles', methods=['POST'])
def create_vehicle():
    global vehicle_db
    if not vehicle_db:
        initialize_vehicle_db()
    
    try:
        data = request.get_json()
        
        # Check required fields
        required_fields = ['unit_brand', 'unit_model', 'unit_type', 'max_weight']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Process optional fields
        min_weight = data.get('min_weight', 0)
        distance = data.get('distance', 0)
        driver_id = data.get('driver_id')
        license_expiry = data.get('license_expiry')
        order_id = data.get('order_id')
        status = data.get('status', 'available')
        
        # Add the vehicle
        vehicle_id = vehicle_db.add_vehicle(
            unit_brand=data['unit_brand'],
            unit_model=data['unit_model'],
            unit_type=data['unit_type'],
            max_weight=data['max_weight'],
            min_weight=min_weight,
            distance=distance,
            driver_id=driver_id,
            license_expiry=license_expiry,
            order_id=order_id,
            status=status
        )
        
        if vehicle_id:
            # Return the newly created vehicle
            new_vehicle = vehicle_db.get_vehicle_by_id(vehicle_id)
            return jsonify(new_vehicle), 201
        
        return jsonify({'error': 'Failed to create vehicle'}), 500
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Update a vehicle
@vehicle_api.route('/api/vehicles/<int:vehicle_id>', methods=['PUT'])
def update_vehicle(vehicle_id):
    global vehicle_db
    if not vehicle_db:
        initialize_vehicle_db()
    
    try:
        # Check if the vehicle exists
        vehicle = vehicle_db.get_vehicle_by_id(vehicle_id)
        if not vehicle:
            return jsonify({'error': 'Vehicle not found'}), 404
        
        # Get update data
        data = request.get_json()
        
        # Update vehicle
        success = vehicle_db.update_vehicle(vehicle_id, **data)
        
        if success:
            # Return the updated vehicle
            updated_vehicle = vehicle_db.get_vehicle_by_id(vehicle_id)
            return jsonify(updated_vehicle), 200
        
        return jsonify({'error': 'Failed to update vehicle'}), 500
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Delete a vehicle
@vehicle_api.route('/api/vehicles/<int:vehicle_id>', methods=['DELETE'])
def delete_vehicle(vehicle_id):
    global vehicle_db
    if not vehicle_db:
        initialize_vehicle_db()
    
    try:
        # Check if the vehicle exists
        vehicle = vehicle_db.get_vehicle_by_id(vehicle_id)
        if not vehicle:
            return jsonify({'error': 'Vehicle not found'}), 404
        
        # Delete vehicle
        success = vehicle_db.delete_vehicle(vehicle_id)
        
        if success:
            return jsonify({'message': f'Vehicle {vehicle_id} deleted successfully'}), 200
        
        return jsonify({'error': 'Failed to delete vehicle'}), 500
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Get vehicles by type
@vehicle_api.route('/api/vehicles/type/<string:unit_type>', methods=['GET'])
def get_vehicles_by_type(unit_type):
    global vehicle_db
    if not vehicle_db:
        initialize_vehicle_db()
    
    try:
        vehicles = vehicle_db.get_vehicles_by_type(unit_type)
        return jsonify(vehicles), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Get vehicles by status
@vehicle_api.route('/api/vehicles/status/<string:status>', methods=['GET'])
def get_vehicles_by_status(status):
    global vehicle_db
    if not vehicle_db:
        initialize_vehicle_db()
    
    try:
        vehicles = vehicle_db.get_vehicles_by_status(status)
        return jsonify(vehicles), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Search for vehicles
@vehicle_api.route('/api/vehicles/search', methods=['GET'])
def search_vehicles():
    global vehicle_db
    if not vehicle_db:
        initialize_vehicle_db()
    
    try:
        search_term = request.args.get('q', '')
        if not search_term:
            return jsonify({'error': 'Missing search term'}), 400
            
        vehicles = vehicle_db.search_vehicles(search_term)
        return jsonify(vehicles), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
