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
scenario = 'foz2_m'

# G = osm.to_graph(porto_nodes, porto_edges2, graph_type='networkx', node_id_col='osmid', network_type='all')
G = osm.to_graph(porto_nodes, porto_edges, graph_type='networkx', node_id_col='osmid', network_type='driving')

# list nodes
nodes = list(G.nodes(data=True))

# metro node example
# ('5791', {'osmid': '5791', 'id': '5791', 'timestamp': Timestamp('2024-11-16 14:13:07.127000'), 'tags': 'metro', 'visible': True, 'version': 1, 'x': -8.60224, 'y': 41.18326, 'changeset': 1, 'geometry': <POINT (-8.602 41.183)>})

# add a new node id 6001
# create a point geometry
# geometry = Point((-8.60224, 41.18326))
# G.add_node('6001', id='6001', osmid='6001', x=-8.60224, y=41.18326, tags='metro', visible=True,
#            timestamp=pd.Timestamp('2024-11-16 14:13:07.127000'), geometry=geometry)
# print(G.nodes['6001'])
# print(geometry)

new_nodes_coords = [
    # [ # trindade
    #     -8.610526799195668,
    #     41.15064938367473
    # ],
    [
        -8.626072564053771,
        41.15254993731568
    ],
    [
        -8.634412995283611,
        41.15294592151821
    ],
    [
        -8.647277000065401,
        41.15464985619218
    ],
    [
        -8.655672208229305,
        41.15526653943448
    ],
    [
        -8.664642371037758,
        41.15713908990193
    ],
    [
        -8.671895081061137,
        41.16107847856583
    ],
    [
        -8.678077335285252,
        41.1660460498326
    ]
]

metro_nodes = [node for node, data in G.nodes(data=True) if data.get('tags') == 'metro']
# Create a subgraph with only the metro nodes
G_metro = G.subgraph(metro_nodes).copy()
# closest node to           [
#             -8.636418929431528,
#             41.165480773996194
#           ],

# node = ox.distance.nearest_nodes(G_metro,   -8.610526799195668,  41.15064938367473) # 5726
# print(node)
# exit()
# CASA DA MÙSICA -> '5706'
# SÂO BENTO -> '5778'

new_nodes = []
for i, coord in enumerate(new_nodes_coords):
    node_id = str(6200 + i)
    G.add_node(node_id, id=node_id, osmid=node_id, x=coord[0], y=coord[1], tags='metro', visible=True,
               timestamp=pd.Timestamp('2024-11-16 14:13:07.127000'), geometry=Point(coord))
    new_nodes.append(node_id)

metro_edges = G_metro.edges(data=True)

# edge example
# ('5768', '5775', {'u': '5768', 'v': '5775', 'key': 0, 'mode': 'metro',  'tags': None, 'osm_type': None, 'length': 672.6245058849787, 'travel_time_seconds': 60.0, 'tag': None, 'geometry': <LINESTRING (-8.604 41.161, -8.598 41.165)>})

metro_velocity = 7.5
# refactor
new_line = [
    '5726', *new_nodes
]

new_line_coords = [(G.nodes[node]['x'], G.nodes[node]['y']) for node in new_line]
print(new_line_coords)

# print 5711 node
# print(G.nodes['5711'])
# exit()
for i in range(len(new_line) - 1):

    tag_name = scenario
    node = new_line[i]
    next_node = new_line[i + 1]
    geometry = LineString([[G.nodes[node]['x'], G.nodes[node]['y']], [G.nodes[next_node]['x'], G.nodes[next_node]['y']]])

    dist = haversine_distance(osmium.geom.Coordinates(G.nodes[node]['x'], G.nodes[node]['y']),
                              osmium.geom.Coordinates(G.nodes[next_node]['x'], G.nodes[next_node]['y']))
    G.add_edge(node, next_node, mode='metro', length=dist, travel_time_seconds=dist / metro_velocity, tag=tag_name, geometry=geometry)
    G.add_edge(next_node, node, mode='metro', length=dist, travel_time_seconds=dist / metro_velocity, tag=tag_name, geometry=geometry)

# print(G.edges(data=True))

# ox.plot_graph(G, edge_color=['#ddcc11' if d.get('tag') == 'bus_nearest_metro' else 'pink' if d.get('tag') == 'metro_nearest_bus' else 'blue' if d.get('mode')=='walking' else 'red' if d.get('mode')=='metro' else 'gray' for u,v,d in G.edges(data=True)], edge_linewidth=0.5)

# plot only the bus lines and the metro lines
ox.plot_graph(G, edge_color=['black' if d.get('tag') == 'bus_nearest_metro' else 'black' if d.get('tag') == 'metro_nearest_bus' else 'blue' if d.get('mode') == 'walking' else 'red' if d.get('mode') == 'metro' else 'gray' for u, v, d in G.edges(data=True)], edge_linewidth=0.5)

# store the new nodes and edges as gpkg
nodes_gdf = ox.graph_to_gdfs(G, nodes=True, edges=False)
# drop id column
nodes_gdf.drop(columns=['id'], inplace=True)
nodes_gdf.rename(columns={'osmid': 'id'}, inplace=True)

edges_gdf = ox.graph_to_gdfs(G, nodes=False, edges=True)

nodes_gdf.to_file(data_folder + f"porto_nodes_{scenario}.gpkg", driver="GPKG")
edges_gdf.to_file(data_folder + f"porto_edges_{scenario}.gpkg", driver="GPKG")
