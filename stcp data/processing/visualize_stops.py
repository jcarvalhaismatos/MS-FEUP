import folium
import pandas as pd
import os

# Read the CSV file
df = pd.read_csv('stcp data/stops.txt')

# Create a map centered on Porto
m = folium.Map(location=[41.15, -8.61], zoom_start=13)

# Add CircleMarkers for each stop
for _, row in df.iterrows():
    folium.CircleMarker(
        location=[row['stop_lat'], row['stop_lon']],
        radius=3,  # Small radius for a dot-like appearance
        color='blue',
        fill=True,
        fillColor='blue',
        fillOpacity=0.7,
        popup=row['stop_name'],
        tooltip=row['stop_name']
    ).add_to(m)

# Save the map as an HTML file
output_path = os.path.join(os.path.dirname(__file__), 'stcp_stops_map.html')
m.save(output_path)

print(f"Map has been saved to {output_path}")
print("Open this file in your web browser to view the map.")
