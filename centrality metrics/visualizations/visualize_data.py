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
        "metro": os.path.join(current_dir, "../data/metro_lines.json"),
        "bus": os.path.join(current_dir, "../data/stcp_lines.json"),
        "municipalities": os.path.join(
            current_dir, "../data/freguesias_municipios.geojson"
        ),
    }


# Replace the single map creation with multiple tile layers
m = folium.Map(
    location=[41.16, -8.613], zoom_start=13.5, tiles=None
)  # Start with no default tiles

# Add different tile layers
folium.TileLayer(
    tiles="OpenStreetMap", name="Streets (OpenStreetMap)", control=True, show=False
).add_to(m)

folium.TileLayer(
    tiles="CartoDB positron", name="Light Map", control=True, show=True
).add_to(m)

folium.TileLayer(
    tiles="CartoDB dark_matter", name="Dark Map", control=True, show=False
).add_to(m)

folium.TileLayer(
    tiles="", name="No Background", attr="Empty Background", control=True, show=False
).add_to(m)

# Get file paths
file_paths = get_file_paths()

# Load municipality boundaries
municipalities_gdf = gpd.read_file(file_paths["municipalities"])

# Filter for Porto municipality to use as boundary
porto_municipality = municipalities_gdf[
    (municipalities_gdf["admin_level"] == "7") & (municipalities_gdf["name"] == "Porto")
]

# Get Porto boundary before using it
porto_boundary = porto_municipality.iloc[0].geometry

# Get all freguesias
freguesias_gdf = municipalities_gdf[municipalities_gdf["admin_level"] == "8"].copy()

# Calculate centroids for freguesias
freguesias_gdf["centroid"] = freguesias_gdf.geometry.centroid

# After calculating centroids, convert them to coordinates for JSON serialization
freguesias_gdf["centroid_coords"] = freguesias_gdf["centroid"].apply(
    lambda p: [p.y, p.x]
)
freguesias_gdf["is_in_porto"] = freguesias_gdf["centroid"].apply(
    lambda x: porto_boundary.contains(x)
)
freguesias_gdf = freguesias_gdf.drop(
    columns=["centroid"]
)  # Remove the original Point column

# Filter freguesias that have centroids within Porto
freguesias_gdf = freguesias_gdf[freguesias_gdf["is_in_porto"]]

# Generate a unique color for each freguesia
colors = [
    "#FF000010",
    "#00FF0010",
    "#0000FF10",
    "#FFFF0010",
    "#FF00FF10",
    "#00FFFF10",
    "#80000010",
    "#00800010",
]
freguesias_gdf["color"] = [colors[i % len(colors)] for i in range(len(freguesias_gdf))]

# Add freguesias boundaries with different colors
folium.GeoJson(
    freguesias_gdf,
    name="Freguesias",
    show=True,
    style_function=lambda x: {
        "fillColor": x["properties"]["color"],
        "color": "#000000",
        "fillOpacity": 0.5,
        "weight": 2,
    },
    popup=folium.GeoJsonPopup(fields=["name"]),
).add_to(m)

# Load metro data
with open(file_paths["metro"], "r", encoding="utf-8") as f:
    metro_data = json.load(f)

# Load bus data
with open(file_paths["bus"], "r", encoding="utf-8") as f:
    bus_data = json.load(f)

# Create feature groups for lines and stops
porto_metro_stops = folium.FeatureGroup(name="Porto Metro Stops", show=False)
outside_metro_stops = folium.FeatureGroup(name="Outside Metro Stops", show=False)
porto_bus_stops = folium.FeatureGroup(name="Porto Bus Stops", show=True)
outside_bus_stops = folium.FeatureGroup(name="Outside Bus Stops", show=False)
metro_lines = folium.FeatureGroup(name="Metro Lines", show=True)
bus_lines = folium.FeatureGroup(name="Bus Lines", show=False)

# Add metro lines and stops
for line in metro_data["lines"]:
    # Draw line
    coordinates = [(stop["lat"], stop["lon"]) for stop in line["stops"]]
    folium.PolyLine(
        locations=coordinates,
        color=f"#{line['color']}",
        weight=4,
        opacity=1,
        popup=f"Metro Line: {line['line_name']}",
    ).add_to(metro_lines)

    # Add stops
    for stop in line["stops"]:
        marker = folium.CircleMarker(
            location=[stop["lat"], stop["lon"]],
            radius=5,
            color=f"#{line['color']}",
            fillColor=f"#{line['color']}",
            weight=2,
            fillOpacity=1,
            popup=f"Metro: {stop['name']}",
        )
        # Check if stop is in Porto
        point = Point(stop["lon"], stop["lat"])
        if porto_boundary.contains(point):
            marker.add_to(porto_metro_stops)
        else:
            marker.add_to(outside_metro_stops)

# Add bus lines and stops
for line in bus_data["lines"]:
    # Draw line
    coordinates = [(stop["lat"], stop["lon"]) for stop in line["stops"]]
    folium.PolyLine(
        locations=coordinates,
        color=f"{line['color']}",
        weight=2,
        opacity=1,
        popup=f"Bus Line: {line['line_name']}",
    ).add_to(bus_lines)

    # Add stops
    for stop in line["stops"]:
        marker = folium.CircleMarker(
            location=[stop["lat"], stop["lon"]],
            radius=3,
            color=f"{line['color']}",
            fillColor=f"{line['color']}",
            weight=1,
            fillOpacity=1,
            popup=f"Bus: {stop['name']}",
        )
        # Check if stop is in Porto
        point = Point(stop["lon"], stop["lat"])
        if porto_boundary.contains(point):
            marker.add_to(porto_bus_stops)
        else:
            marker.add_to(outside_bus_stops)

# Add all feature groups to map
porto_metro_stops.add_to(m)
outside_metro_stops.add_to(m)
porto_bus_stops.add_to(m)
outside_bus_stops.add_to(m)
metro_lines.add_to(m)
bus_lines.add_to(m)

# Add layer control
folium.LayerControl().add_to(m)

# Add a legend
legend_html = """
<div style="position: fixed; 
            bottom: 50px; right: 50px; width: 200px;
            border:2px solid grey; z-index:9999; background-color:white;
            opacity:0.7;
            padding: 10px">
            <p style="text-align: center;"><b>Freguesias</b></p>
"""

for idx, row in freguesias_gdf.iterrows():
    legend_html += f"""
            <p><i style="background: {row['color']}; 
                      opacity: 0.5;
                      border: 1px solid black;
                      width: 20px; 
                      height: 10px; 
                      display: inline-block;"></i> {row['name']}</p>
"""

legend_html += """
            <hr>
            <p><i style="background: #000000; 
                        border-radius: 50%; 
                        width: 10px; 
                        height: 10px; 
                        display: inline-block;
                        opacity: 1.0;"></i> Metro Stops</p>
            <p><i style="background: #000000; 
                        border-radius: 50%; 
                        width: 6px; 
                        height: 6px; 
                        display: inline-block;
                        opacity: 1.0;"></i> Bus Stops</p>
</div>
"""
m.get_root().html.add_child(folium.Element(legend_html))

# Save the map
output_path = "centrality metrics/visualizations/transport_network_map.html"
m.save(output_path)

print(f"Map has been saved to {output_path}")
