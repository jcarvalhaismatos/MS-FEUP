import geopandas as gpd
import pandas as pd
import networkx as nx
import osmnx as ox
import contextily as cx
import numpy as np
import joblib
import math
from pyrosm import OSM, get_data
import matplotlib.pyplot as plt
# fold
import functools

from osmium.geom import haversine_distance
import osmium
from shapely import Point, LineString

data_folder = "../openstreetmap data/"

porto_nodes = gpd.read_file(data_folder + "porto_nodes_time.gpkg")
porto_edges = gpd.read_file(data_folder + "porto_edges_time.gpkg")

porto_nodes.crs = "EPSG:4326"
porto_edges.crs = "EPSG:4326"
osm_fp = "../openstreetmap data/porto.osm.pbf"
osm = OSM(osm_fp)
scenario = 'foz_b'

# G = osm.to_graph(porto_nodes, porto_edges2, graph_type='networkx', node_id_col='osmid', network_type='all')
G = osm.to_graph(porto_nodes, porto_edges, graph_type='networkx', node_id_col='osmid', network_type='driving')

# list nodes
nodes = list(G.nodes(data=True))
# print(nodes)
# exit()
# bus node example
#  ('IFOZ2', {'osmid': 'IFOZ2', 'id': 'IFOZ2', 'timestamp': Timestamp('2024-11-16 14:31:45.227000'), 'tags': 'bus', 'visible': True, 'version': 1, 'x': -8.66960728536792, 'y': 41.1483465643572, 'changeset': 1, 'geometry': <POINT (-8.67 41.148)>})


new_nodes_coords = [
    # francos
    [
        -8.641944619168527,
        41.15968115886852
    ],
    [
        -8.643899973611553,
        41.154519081291255
    ],
    [
        -8.649695194396088,
        41.153403524564396
    ],
    [
        -8.652930752681073,
        41.151968621549486
    ],
    [
        -8.657909399133331,
        41.150872663066764
    ],
    [
        -8.662360241627283,
        41.15082211038478
    ],
    [
        -8.667091809347511,
        41.150944807188864
    ],
    [
        -8.670324843209556,
        41.15276725053698
    ],
    [
        -8.67302676500077,
        41.15473980817322
    ],
    [
        -8.676255475449778,
        41.15644136657204
    ],
    [
        -8.678172560330694,
        41.15858869329139
    ],
    [
        -8.68101446226251,
        41.161391792230944
    ],
    [
        -8.681462894901415,
        41.16616487365823
    ],
]
x_values = [coord[0] for coord in new_nodes_coords]
y_values = [coord[1] for coord in new_nodes_coords]

bus_nodes = [node for node, data in G.nodes(data=True) if data.get('tags') == 'bus']
# Create a subgraph with only the bus nodes
G_bus = G.subgraph(bus_nodes).copy()


node = ox.distance.nearest_nodes(G_bus, -8.636418929431528, 41.165480773996194) # SDP1
# print(node)
# exit()
# CASA DA MÙSICA -> '5706'
# SÂO BENTO -> '5778'

# new_nodes = []
# for i, coord in enumerate(new_nodes_coords):
#     node_id = str(6100 + i)
#     G.add_node(node_id, id=node_id, osmid=node_id, x=coord[0], y=coord[1], tags='bus', visible=True,
#                timestamp=pd.Timestamp('2024-11-16 14:13:07.127000'), geometry=Point(coord))
#     new_nodes.append(node_id)

bus_edges = G_bus.edges(data=True)
# print(bus_edges)
# edge example
# ('5768', '5775', {'u': '5768', 'v': '5775', 'key': 0, 'mode': 'bus',  'tags': None, 'osm_type': None, 'length': 672.6245058849787, 'travel_time_seconds': 60.0, 'tag': None, 'geometry': <LINESTRING (-8.604 41.161, -8.598 41.165)>})

bus_velocity = 7.5

nearest_bus_nodes = ox.nearest_nodes(G_bus, x_values, y_values)

# refactor
new_line = [
    *nearest_bus_nodes
]

for i in range(len(new_line) - 1):

    tag_name = scenario
    node = new_line[i]
    next_node = new_line[i + 1]
    geometry = LineString([[G.nodes[node]['x'], G.nodes[node]['y']], [G.nodes[next_node]['x'], G.nodes[next_node]['y']]])

    dist = haversine_distance(osmium.geom.Coordinates(G.nodes[node]['x'], G.nodes[node]['y']),
                              osmium.geom.Coordinates(G.nodes[next_node]['x'], G.nodes[next_node]['y']))
    G.add_edge(node, next_node, mode=f"bus_{tag_name}", length=dist, travel_time_seconds=dist / bus_velocity, tag=tag_name, geometry=geometry)
    G.add_edge(next_node, node, mode=f"bus_{tag_name}", length=dist, travel_time_seconds=dist / bus_velocity, tag=tag_name, geometry=geometry)

# print(G.edges(data=True))

# ox.plot_graph(G, edge_color=['#ddcc11' if d.get('tag') == 'bus_nearest_bus' else 'pink' if d.get('tag') == 'bus_nearest_bus' else 'blue' if d.get('mode')=='walking' else 'red' if d.get('mode')=='bus' else 'gray' for u,v,d in G.edges(data=True)], edge_linewidth=0.5)

# plot only the bus lines and the bus lines
ox.plot_graph(G, edge_color=['yellow' if d.get('mode') == f"bus_{scenario}" else 'black' if d.get('tag') == 'bus_nearest_bus' else 'black' if d.get('tag') == 'bus_nearest_bus' else 'blue' if d.get('mode') == 'walking' else 'red' if d.get('mode') == 'metro' else 'gray' for u, v, d in G.edges(data=True)], edge_linewidth=0.5)

# store the new nodes and edges as gpkg
nodes_gdf = ox.graph_to_gdfs(G, nodes=True, edges=False)
# drop id column
nodes_gdf.drop(columns=['id'], inplace=True)
nodes_gdf.rename(columns={'osmid': 'id'}, inplace=True)

edges_gdf = ox.graph_to_gdfs(G, nodes=False, edges=True)

nodes_gdf.to_file(data_folder + f"porto_nodes_{scenario}.gpkg", driver="GPKG")
edges_gdf.to_file(data_folder + f"porto_edges_{scenario}.gpkg", driver="GPKG")
