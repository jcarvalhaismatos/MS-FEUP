import pandas as pd
import numpy as np

# Load the data
shapes_data = pd.read_csv('stcp data/shapes.txt')
stops_data = pd.read_csv('stcp data/stops.txt')
routes_data = pd.read_csv('stcp data/routes.txt')

# Function to calculate the Haversine distance
def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Radius of the Earth in kilometers
    dlat = np.radians(lat2 - lat1)
    dlon = np.radians(lon2 - lon1)
    a = np.sin(dlat / 2) ** 2 + np.cos(np.radians(lat1)) * np.cos(np.radians(lat2)) * np.sin(dlon / 2) ** 2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
    return R * c

# Group by shape_id to get routes
routes = shapes_data.groupby('shape_id')

# Create a dictionary to hold stops for each route
bus_routes = {}

# Iterate through each route
for shape_id, group in routes:
    # Extract stops (latitude and longitude) and sort by sequence
    stops = group[['shape_pt_lat', 'shape_pt_lon', 'shape_pt_sequence']].sort_values('shape_pt_sequence')
    
    assigned_stops = []
    
    # Find the nearest stop for each shape point
    for _, shape_point in stops.iterrows():
        shape_lat = shape_point['shape_pt_lat']
        shape_lon = shape_point['shape_pt_lon']
        
        # Calculate distances to all stops
        distances = stops_data.apply(lambda row: haversine(shape_lat, shape_lon, row['stop_lat'], row['stop_lon']), axis=1)
        
        # Get the nearest stop
        nearest_stop_index = distances.idxmin()
        nearest_stop = stops_data.loc[nearest_stop_index]
        
        assigned_stops.append({
            'shape_pt_sequence': shape_point['shape_pt_sequence'],
            'stop_id': nearest_stop['stop_id'],
            'stop_name': nearest_stop['stop_name'],
            'stop_lat': nearest_stop['stop_lat'],
            'stop_lon': nearest_stop['stop_lon'],
            'distance': distances.min(),
            'route_name': routes_data.loc[routes_data['route_id'] == shape_id, 'route_long_name'].values[0],
        })
    
    # Store the assigned stops in the bus_routes dictionary
    bus_routes[shape_id] = pd.DataFrame(assigned_stops)

# Example: Print stops for each route
for route, stops in bus_routes.items():
    print(f"Route: {route}")
    print(stops)

# Combine all stops into a single DataFrame and save to CSV
all_stops = pd.concat(bus_routes.values(), keys=bus_routes.keys())
all_stops.reset_index(level=0, inplace=True)
all_stops.rename(columns={'level_0': 'route'}, inplace=True)
all_stops.to_csv("all_routes_stops.csv", index=False)