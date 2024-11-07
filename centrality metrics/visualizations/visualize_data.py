import os
import folium
import json
import geopandas as gpd
import random
from shapely.geometry import Point

def get_file_paths():
    """Get absolute paths to required files"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    return {
        'metro': os.path.join(current_dir, '../data/metro_lines.json'),
        'bus': os.path.join(current_dir, '../data/stcp_lines.json'),
        'municipalities': os.path.join(current_dir, '../data/freguesias_municipios.geojson')
    }
    
# Create a map centered on Porto
m = folium.Map(location=[41.15, -8.61], zoom_start=12)

# Get file paths
file_paths = get_file_paths()

# Load municipality boundaries
municipalities_gdf = gpd.read_file(file_paths['municipalities'])

# Filter for Porto municipality to use as boundary
porto_municipality = municipalities_gdf[
    (municipalities_gdf['admin_level'] == '7') & 
    (municipalities_gdf['name'] == 'Porto')
]

# Get Porto boundary before using it
porto_boundary = porto_municipality.iloc[0].geometry

# Get all freguesias
freguesias_gdf = municipalities_gdf[municipalities_gdf['admin_level'] == '8'].copy()

# Calculate centroids for freguesias
freguesias_gdf['centroid'] = freguesias_gdf.geometry.centroid

# After calculating centroids, convert them to coordinates for JSON serialization
freguesias_gdf['centroid_coords'] = freguesias_gdf['centroid'].apply(lambda p: [p.y, p.x])
freguesias_gdf['is_in_porto'] = freguesias_gdf['centroid'].apply(lambda x: porto_boundary.contains(x))
freguesias_gdf = freguesias_gdf.drop(columns=['centroid'])  # Remove the original Point column

# Filter freguesias that have centroids within Porto
freguesias_gdf = freguesias_gdf[freguesias_gdf['is_in_porto']]

# Generate a unique color for each freguesia
colors = ['#FF000030', '#00FF0030', '#0000FF30', '#FFFF0030', '#FF00FF30', '#00FFFF30', '#80000030', '#00800030']
freguesias_gdf['color'] = [colors[i % len(colors)] for i in range(len(freguesias_gdf))]

# Add freguesias boundaries with different colors
folium.GeoJson(
    freguesias_gdf,
    style_function=lambda x: {
        'fillColor': x['properties']['color'],
        'color': '#000000',
        'fillOpacity': 0.5,
        'weight': 2
    },
    popup=folium.GeoJsonPopup(fields=['name'])
).add_to(m)

# Load metro data
with open(file_paths['metro'], 'r', encoding='utf-8') as f:
    metro_data = json.load(f)

# Load bus data
with open(file_paths['bus'], 'r', encoding='utf-8') as f:
    bus_data = json.load(f)

# Add metro lines and stops
for line in metro_data['lines']:
    # Draw line
    coordinates = [(stop['lat'], stop['lon']) for stop in line['stops']]
    folium.PolyLine(
        locations=coordinates,
        color=f"#{line['color']}",
        weight=4,
        opacity=0.8,
        popup=f"Metro Line: {line['line_name']}"
    ).add_to(m)
    
    # Add stops
    for stop in line['stops']:
        folium.CircleMarker(
            location=[stop['lat'], stop['lon']],
            radius=5,
            color='#000000',
            fillColor='#ffffff',
            weight=2,
            popup=f"Metro: {stop['name']}",
        ).add_to(m)

# Add bus lines and stops
for line in bus_data['lines']:
    # Draw line
    coordinates = [(stop['lat'], stop['lon']) for stop in line['stops']]
    folium.PolyLine(
        locations=coordinates,
        color=f"#{line['color']}",
        weight=2,
        opacity=0.5,
        popup=f"Bus Line: {line['line_name']}"
    ).add_to(m)
    
    # Add stops
    for stop in line['stops']:
        folium.CircleMarker(
            location=[stop['lat'], stop['lon']],
            radius=3,
            color='#000000',
            fillColor='#ff0000',
            weight=1,
            popup=f"Bus: {stop['name']}",
        ).add_to(m)

# Add a legend
legend_html = '''
<div style="position: fixed; 
            bottom: 50px; right: 50px; width: 200px;
            border:2px solid grey; z-index:9999; background-color:white;
            opacity:0.8;
            padding: 10px">
            <p style="text-align: center;"><b>Freguesias</b></p>
'''

for idx, row in freguesias_gdf.iterrows():
    legend_html += f'''
            <p><i style="background: {row['color']}; 
                      opacity: 0.5;
                      border: 1px solid black;
                      width: 20px; 
                      height: 10px; 
                      display: inline-block;"></i> {row['name']}</p>
'''

legend_html += '''
            <hr>
            <p><i style="background: #ffffff; border: 2px solid black; border-radius: 50%; width: 10px; height: 10px; display: inline-block;"></i> Metro Stops</p>
            <p><i style="background: #ff0000; border: 1px solid black; border-radius: 50%; width: 6px; height: 6px; display: inline-block;"></i> Bus Stops</p>
</div>
'''
m.get_root().html.add_child(folium.Element(legend_html))

# Save the map
output_path = "centrality metrics/visualizations/transport_network_map.html"
m.save(output_path)

print(f"Map has been saved to {output_path}")