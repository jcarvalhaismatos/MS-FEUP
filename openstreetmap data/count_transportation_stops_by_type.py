import json

# Load the GeoJSON data with UTF-8 encoding
with open("porto_municipality_transport_stops.geojson", encoding='utf-8') as f:
    data = json.load(f)

# Initialize counters
bus_count = 0
metro_count = 0
neither = 0

for feature in data["features"]:
    properties = feature["properties"]

    if properties.get("bus") == "yes":
        bus_count += 1

    # Check if the stop is a metro (light_rail)
    elif properties.get("light_rail") == "yes":
        metro_count += 1

    else:
        neither += 1

# Output the results
print(f"Number of bus stops: {bus_count}")
print(f"Number of metro stops: {metro_count}")
print(f"Number of neither: {neither}")
