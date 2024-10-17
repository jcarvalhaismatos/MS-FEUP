import folium
import json
import os

# Create a map centered on Porto
m = folium.Map(location=[41.15, -8.61], zoom_start=13)

# Load the stops GeoJSON file
stops_geojson_path = os.path.join(os.path.dirname(__file__), "stcp_stops.geojson")
with open(stops_geojson_path, "r") as f:
    stops_data = json.load(f)

# Add stops to the map
for feature in stops_data["features"]:
    lat, lon = feature["geometry"]["coordinates"][::-1]
    folium.CircleMarker(
        location=[lat, lon],
        radius=3,
        color="blue",
        fill=True,
        fillColor="blue",
        fillOpacity=0.7,
        popup=feature["properties"]["stop_name"],
        tooltip=feature["properties"]["stop_name"],
    ).add_to(m)

# Load the lines GeoJSON file
lines_geojson_path = os.path.join(os.path.dirname(__file__), "stcp_lines.geojson")
with open(lines_geojson_path, "r") as f:
    lines_data = json.load(f)

# Add lines to the map
for feature in lines_data["features"]:
    folium.GeoJson(
        feature,
        style_function=lambda x: {
            "color": x["properties"]["color"],
            "weight": 3,
            "opacity": 0.7,
        },
        tooltip=folium.GeoJsonTooltip(fields=["line_name"], aliases=["Line: "]),
    ).add_to(m)

# Save the map as an HTML file
output_path = os.path.join(os.path.dirname(__file__), "stcp_lines_and_stops_map.html")
m.save(output_path)

print(f"Map has been saved to {output_path}")
print("Open this file in your web browser to view the map.")
