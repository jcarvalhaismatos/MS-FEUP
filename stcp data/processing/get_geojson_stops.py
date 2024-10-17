import pandas as pd
from geojson import Feature, FeatureCollection, Point

# Read the CSV file
df = pd.read_csv('stcp data/stops.txt')

# Create a list to store features
features = []

# Iterate through each row in the dataframe
for idx, row in df.iterrows():
    # Create a Point geometry
    point = Point((row['stop_lon'], row['stop_lat']))
    
    # Create properties for the feature
    properties = {
        'stop_id': row['stop_id'],
        'stop_code': row['stop_code'],
        'stop_name': row['stop_name'],
        'zone_id': row['zone_id'],
        'stop_url': row['stop_url']
    }
    
    # Create a Feature
    feature = Feature(geometry=point, properties=properties)
    
    # Add the feature to the list
    features.append(feature)

# Create a FeatureCollection
feature_collection = FeatureCollection(features)

# Write the GeoJSON to a file
with open('stcp_data/processing/stcp_stops.geojson', 'w') as f:
    f.write(str(feature_collection))

print("GeoJSON file 'stcp_stops.geojson' has been created.")

