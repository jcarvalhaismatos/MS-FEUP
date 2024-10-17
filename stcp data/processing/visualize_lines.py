import folium
import json

# Create a map centered on Porto
m = folium.Map(location=[41.15, -8.61], zoom_start=13)

# Load the lines JSON file
lines_json_path = "stcp data/processing/stcp_lines.json"
with open(lines_json_path, "r", encoding="utf-8") as f:
    lines_data = json.load(f)

# Dictionary to store unique routes
unique_routes = {}

# Process lines data
for line in lines_data["lines"]:
    line_name = line["line_name"]
    if line_name not in unique_routes:
        coordinates = [(stop["lat"], stop["lon"]) for stop in line["stops"]]
        color = line["color"]  # Use the color provided in the JSON file
        unique_routes[line_name] = {
            "coordinates": coordinates,
            "color": color
        }

# Add unique routes to the map
for line_name, route_data in unique_routes.items():
    folium.PolyLine(
        locations=route_data["coordinates"],
        color=route_data["color"],
        weight=7,
        opacity=0.8,
        popup=f"Line: {line_name}",
    ).add_to(m)

# Save the map as an HTML file
output_path = "stcp data/results/stcp_lines_map.html"
m.save(output_path)

print(f"Map has been saved to {output_path}")
print("Open this file in your web browser to view the map.")

# Print information about unique lines
print("\nUnique lines detected:")
for line_name, route_data in unique_routes.items():
    print(f"Line: {line_name}")
    print(f"  Color: {route_data['color']}")
    print(f"  Number of stops: {len(route_data['coordinates'])}")
    print()

# Print total number of unique lines
print(f"Total number of unique lines: {len(unique_routes)}")
