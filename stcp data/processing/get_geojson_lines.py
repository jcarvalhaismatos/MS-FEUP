import os
import pandas as pd
import json
import random
import csv

# Function to generate a random color
def random_color():
    return f"#{random.randint(0, 0xFFFFFF):06x}"

# Directory containing the CSV files
data_dir = 'stcp data/processing/data'

# Load stops data
stops_file = 'stcp data/stops.txt'
stops_data = {}
with open(stops_file, 'r', encoding='utf-8') as f:
    reader = csv.reader(f, delimiter=',')
    next(reader)  # Skip header
    for row in reader:
        stop_id, stop_code, stop_name, stop_lat, stop_lon = row[0], row[1], row[2], row[3], row[4]
        stops_data[stop_id] = {
            'name': stop_name,
            'lat': float(stop_lat),
            'lon': float(stop_lon)
        }

# List to store line data
lines = []

# Dictionary to store colors for each line
line_colors = {}

# Dictionary to store missing stops
missing_stops = {}

# Iterate through CSV files in the data directory
for filename in os.listdir(data_dir):
    if filename.endswith('.csv') and not "route_stops" in filename:
        line_name = filename.split('_')[0]  # Extract line name from filename
        
        # Read the CSV file
        df = pd.read_csv(os.path.join(data_dir, filename), encoding='utf-8')
        
        # Sort by sequence
        df = df.sort_values('sequence')
        
        # Create a list of stop names and coordinates
        stops = []
        for _, row in df.iterrows():
            stop_id = row['code']
            if stop_id in stops_data:
                stops.append({
                    'name': stops_data[stop_id]['name'],
                    'lat': stops_data[stop_id]['lat'],
                    'lon': stops_data[stop_id]['lon']
                })
            else:
                if stop_id not in missing_stops:
                    missing_stops[stop_id] = {'count': 1, 'lines': [line_name]}
                else:
                    missing_stops[stop_id]['count'] += 1
                    if line_name not in missing_stops[stop_id]['lines']:
                        missing_stops[stop_id]['lines'].append(line_name)
                print(f"Warning: Stop ID '{stop_id}' not found in stops.txt")
        
        # Generate a random color for this line if not already assigned
        if line_name not in line_colors:
            line_colors[line_name] = random_color()
        
        # Create line data
        line_data = {
            'line_name': line_name,
            'color': line_colors[line_name],
            'stops': stops
        }
        
        # Add the line data to the list
        lines.append(line_data)

# Create a JSON object with the lines data
lines_json = {'lines': lines}

# Write the JSON to a file in the current directory
output_file = 'stcp data/processing/stcp_lines.json'
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(lines_json, f, ensure_ascii=False, indent=2)

print(f"JSON file '{output_file}' has been created in the current directory.")

# Print summary of missing stops
print("\nMissing stops summary:")
for stop_id, info in sorted(missing_stops.items(), key=lambda x: x[1]['count'], reverse=True):
    print(f"'{stop_id}': {info['count']} occurrences, in lines: {', '.join(info['lines'])}")