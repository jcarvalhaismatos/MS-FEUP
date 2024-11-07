import folium
import json
import geopandas as gpd
from get_municipio_centrality import get_file_paths

# Create a map centered on Porto
m = folium.Map(location=[41.15, -8.61], zoom_start=11)

# Get file paths
file_paths = get_file_paths()

# Load municipality boundaries
municipalities_gdf = gpd.read_file(file_paths['municipalities'])
municipalities_gdf = municipalities_gdf[municipalities_gdf['admin_level'] == '7']

# Add municipality boundaries to map
folium.GeoJson(
    municipalities_gdf,
    style_function=lambda x: {
        'fillColor': '#ffff00',
        'color': '#000000',
        'fillOpacity': 0.1,
        'weight': 1
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
            bottom: 50px; right: 50px; width: 150px; height: 90px; 
            border:2px solid grey; z-index:9999; background-color:white;
            opacity:0.8;
            padding: 10px">
            <p><i style="background: #ffffff; border: 2px solid black; border-radius: 50%; width: 10px; height: 10px; display: inline-block;"></i> Metro Stops</p>
            <p><i style="background: #ff0000; border: 1px solid black; border-radius: 50%; width: 6px; height: 6px; display: inline-block;"></i> Bus Stops</p>
</div>
'''
m.get_root().html.add_child(folium.Element(legend_html))

# Save the map
output_path = "centrality metrics/transport_network_map.html"
m.save(output_path)

print(f"Map has been saved to {output_path}") 