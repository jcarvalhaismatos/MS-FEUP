import json
import geopandas as gpd
import pandas as pd
import numpy as np
import os
from shapely.geometry import Point
from shapely.ops import unary_union

def get_file_paths():
    """Get absolute paths to required files"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    return {
        'metro': os.path.join(current_dir, 'metro_lines.json'),
        'bus': os.path.join(current_dir, 'stcp_lines.json'),
        'municipalities': os.path.join(current_dir, 'freguesias_municipios.geojson')
    }

def load_transport_data(metro_file, bus_file):
    """Load and combine metro and bus stops"""
    # Load metro data with UTF-8 encoding
    with open(metro_file, encoding='utf-8') as f:
        metro_data = json.load(f)
    
    # Load bus data with UTF-8 encoding
    with open(bus_file, encoding='utf-8') as f:
        bus_data = json.load(f)
    
    # Extract all metro stops
    metro_stops = []
    for line in metro_data['lines']:
        for stop in line['stops']:
            metro_stops.append({
                'name': stop['name'],
                'lat': stop['lat'],
                'lon': stop['lon'],
                'type': 'metro'
            })
    
    # Extract all bus stops
    bus_stops = []
    for line in bus_data['lines']:
        for stop in line['stops']:
            bus_stops.append({
                'name': stop['name'],
                'lat': stop['lat'],
                'lon': stop['lon'],
                'type': 'bus'
            })
    
    # Combine and convert to GeoDataFrame
    all_stops = metro_stops + bus_stops
    stops_gdf = gpd.GeoDataFrame(
        all_stops,
        geometry=[Point(x['lon'], x['lat']) for x in all_stops],
        crs="EPSG:4326"
    )
    
    return stops_gdf

def calculate_municipality_centrality(municipalities_gdf, stops_gdf):
    """Calculate centrality metrics for each municipality"""
    
    # Reproject to a metric CRS for area calculations
    municipalities_gdf = municipalities_gdf.to_crs("EPSG:3763")
    stops_gdf = stops_gdf.to_crs("EPSG:3763")

    results = []
    
    for idx, municipality in municipalities_gdf.iterrows():
        # Get stops within municipality
        stops_in_mun = stops_gdf[stops_gdf.intersects(municipality.geometry)]
        
        # Calculate metrics
        area_km2 = municipality.geometry.area / 1000000  # Convert to km²
        num_stops = len(stops_in_mun)
        num_metro = len(stops_in_mun[stops_in_mun['type'] == 'metro'])
        num_bus = len(stops_in_mun[stops_in_mun['type'] == 'bus'])
        
        # Calculate stop density
        stop_density = num_stops / area_km2 if area_km2 > 0 else 0
        
        # Calculate coverage (area within 500m of any stop)
        stops_buffer = unary_union(stops_in_mun.buffer(500))
        coverage_area = stops_buffer.intersection(municipality.geometry).area
        coverage_percent = (coverage_area / municipality.geometry.area) * 100
        
        # Calculate transport diversity (ratio of metro to total stops)
        transport_diversity = num_metro / num_stops if num_stops > 0 else 0
        
        results.append({
            'municipality': municipality['name'],
            'area_km2': area_km2,
            'num_stops': num_stops,
            'num_metro': num_metro,
            'num_bus': num_bus,
            'stop_density': stop_density,
            'coverage_percent': coverage_percent,
            'transport_diversity': transport_diversity
        })
    
    return pd.DataFrame(results)

def normalize_and_combine_metrics(df):
    """Normalize metrics and calculate final centrality score"""
    # Columns to normalize
    metrics = ['stop_density', 'coverage_percent', 'transport_diversity']
    
    # Min-max normalization
    for metric in metrics:
        min_val = df[metric].min()
        max_val = df[metric].max()
        df[f'{metric}_normalized'] = (df[metric] - min_val) / (max_val - min_val)
    
    # Calculate final centrality score (weighted average)
    weights = {
        'stop_density_normalized': 0.4,
        'coverage_percent_normalized': 0.4,
        'transport_diversity_normalized': 0.2
    }
    
    df['centrality_score'] = sum(df[metric] * weight 
                                for metric, weight in weights.items())
    
    return df

def main():
    file_paths = get_file_paths()
    
    municipalities_gdf = gpd.read_file(file_paths['municipalities'])
    municipalities_gdf = municipalities_gdf[municipalities_gdf['admin_level'] == '7']
    
    print(municipalities_gdf)
    
    stops_gdf = load_transport_data(file_paths['metro'], file_paths['bus'])
 
    centrality_df = calculate_municipality_centrality(municipalities_gdf, stops_gdf)
 
    final_df = normalize_and_combine_metrics(centrality_df)
    
    final_df = final_df.sort_values('centrality_score', ascending=False)
    
    # Save results
    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'municipality_centrality.csv')
    final_df.to_csv(output_path, index=False)
    
    # Print top 5 most central municipalities
    print("\nMunicipality Metrics:")
    print("Municipality | Centrality Score | Stop Density | Coverage % | Transport Diversity")
    print("-" * 85)
    for _, row in final_df.iterrows():
        print(f"{row['municipality'][:30]:<30} | {row['centrality_score']:15.3f} | {row['stop_density']:10.2f} | {row['coverage_percent']:9.2f} | {row['transport_diversity']:10.2f}")

if __name__ == "__main__":
    main()
