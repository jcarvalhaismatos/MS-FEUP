import osmnx as ox
import geopandas as gpd

# Configure the project
ox.config(use_cache=True, log_console=True)

# Define the area of interest (Porto municipality)
place_name = "Porto, Portugal"
place_query = {'city': 'Porto', 'admin_level': '7', 'country': 'Portugal'}

# Download the data
city = ox.geocode_to_gdf(place_query)

# Get the street network
street_network = ox.graph_from_polygon(city.geometry.iloc[0], network_type="all")

# Get buildings
#buildings = ox.features_from_polygon(city.geometry.iloc[0], tags={"building": True})

# Get points of interest
pois = ox.features_from_polygon(city.geometry.iloc[0], tags={"amenity": True})

# Get transportation stops
transport_stops = ox.features_from_polygon(city.geometry.iloc[0], tags={
    "public_transport": ["stop_position", "platform", "station"],
    "highway": "bus_stop"
})

# Save the data
city.to_file("porto_municipality_boundary.geojson", driver="GeoJSON")
ox.save_graph_geopackage(street_network, filepath="porto_municipality_street_network.gpkg")
#buildings.to_file("porto_municipality_buildings.geojson", driver="GeoJSON")
pois.to_file("porto_municipality_pois.geojson", driver="GeoJSON")
transport_stops.to_file("porto_municipality_transport_stops.geojson", driver="GeoJSON")

print("OpenStreetMap data for Porto municipality has been downloaded and saved.")
