import os
import sys

# Add the parent directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

import folium
from folium import plugins
import json
import geopandas as gpd
from get_municipio_centrality import load_transport_data, get_file_paths


def create_stop_heatmap():
    # Create a map centered on Porto
    m = folium.Map(location=[41.15, -8.61], zoom_start=12)

    # Get file paths
    file_paths = get_file_paths()

    # Load municipality boundaries
    municipalities_gdf = gpd.read_file(file_paths["municipalities"])

    # Filter for Porto municipality
    porto_municipality = municipalities_gdf[
        (municipalities_gdf["admin_level"] == "7")
        & (municipalities_gdf["name"] == "Porto")
    ]

    # Get freguesias within Porto and project to appropriate CRS
    freguesias_gdf = municipalities_gdf[municipalities_gdf["admin_level"] == "8"].copy()
    freguesias_gdf = freguesias_gdf.to_crs(epsg=3763)
    porto_municipality = porto_municipality.to_crs(epsg=3763)

    # Calculate centroids and filter for Porto freguesias
    porto_boundary = porto_municipality.iloc[0].geometry
    freguesias_gdf["centroid"] = freguesias_gdf.geometry.centroid
    freguesias_gdf["is_in_porto"] = freguesias_gdf["centroid"].apply(
        lambda x: porto_boundary.contains(x)
    )
    freguesias_gdf = freguesias_gdf[freguesias_gdf["is_in_porto"]]

    # Project back to WGS84 for the map and remove centroid column
    freguesias_gdf = freguesias_gdf.to_crs(epsg=4326)
    freguesias_gdf = freguesias_gdf.drop(columns=["centroid"])

    # Add freguesias boundaries
    folium.GeoJson(
        freguesias_gdf,
        style_function=lambda x: {
            "fillColor": "#000000",
            "color": "#000000",
            "fillOpacity": 0.1,
            "weight": 2,
        },
        popup=folium.GeoJsonPopup(fields=["name"]),
    ).add_to(m)

    # Load transport stops
    stops_gdf = load_transport_data(file_paths["metro"], file_paths["bus"])
    
    # Project stops to same CRS as Porto boundary for accurate containment check
    stops_gdf = stops_gdf.to_crs(epsg=3763)
    
    # Create two separate GeoDataFrames for stops inside and outside Porto
    stops_gdf['is_in_porto'] = stops_gdf.geometry.apply(lambda x: porto_boundary.contains(x))
    porto_stops = stops_gdf[stops_gdf['is_in_porto']].copy()
    outside_stops = stops_gdf[~stops_gdf['is_in_porto']].copy()
    
    # Project back to WGS84 for the map
    porto_stops = porto_stops.to_crs(epsg=4326)
    outside_stops = outside_stops.to_crs(epsg=4326)
    
    # Create feature groups for the heatmaps
    porto_heatmap = folium.FeatureGroup(name='Porto Stops Heatmap')
    outside_heatmap = folium.FeatureGroup(name='Outside Stops Heatmap', show=False)
    
    # Add Porto heatmap
    heat_data_porto = [[row["lat"], row["lon"]] for _, row in porto_stops.iterrows()]
    plugins.HeatMap(
        heat_data_porto,
        radius=45,
        blur=45,
        max_zoom=13,
        min_opacity=0.2,
        gradient={
            0.0: '#FFFFFF',
            0.2: '#FFB6C1',
            0.4: '#FF4040',
            0.6: '#FF0000',
            0.8: '#B22222',
            1.0: '#800000',
        },
    ).add_to(porto_heatmap)
    
    # Add outside Porto heatmap with different colors
    heat_data_outside = [[row["lat"], row["lon"]] for _, row in outside_stops.iterrows()]
    plugins.HeatMap(
        heat_data_outside,
        radius=45,
        blur=45,
        max_zoom=13,
        min_opacity=0.2,
        gradient={
            0.0: '#FFFFFF',
            0.2: '#B0E0E6',  # Light blue
            0.4: '#87CEEB',  # Sky blue
            0.6: '#4682B4',  # Steel blue
            0.8: '#0000CD',  # Medium blue
            1.0: '#000080',  # Navy
        },
    ).add_to(outside_heatmap)
    
    # Add feature groups to map
    porto_heatmap.add_to(m)
    outside_heatmap.add_to(m)
    
    # Add layer control
    folium.LayerControl().add_to(m)

    # Add a legend
    legend_html = """
    <div style="position: fixed; 
                bottom: 50px; right: 50px; width: 150px;
                border:2px solid grey; z-index:9999; background-color:white;
                opacity:0.8;
                padding: 10px">
                <p style="text-align: center;"><b>Stop Density</b></p>
                <div style="display: flex; flex-direction: column;">
                    <div style="background: linear-gradient(to right, #FFFFFF, #FFB6C1, #FF4040, #FF0000, #B22222, #800000);
                               height: 20px; margin-bottom: 5px;"></div>
                    <div style="display: flex; justify-content: space-between;">
                        <span>Low</span>
                        <span>High</span>
                    </div>
                </div>
    </div>
    """
    m.get_root().html.add_child(folium.Element(legend_html))

    # Save the map
    output_path = os.path.join(current_dir, "stop_density_heatmap.html")
    m.save(output_path)
    print(f"Heatmap has been saved to {output_path}")


if __name__ == "__main__":
    create_stop_heatmap()
