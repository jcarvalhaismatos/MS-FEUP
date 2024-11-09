#!/bin/python3

from typing import TypedDict
from enum import Enum
import sys
import json
import math


class TransportType(Enum):
    BUS = 0
    METRO = 1


class TransportStop(TypedDict):
    id: str
    name: str
    zone: str
    location: list[float]
    bus: bool
    metro: bool


class StopNode:
    incoming: list[tuple[str, TransportType]]
    outgoing: list[tuple[str, TransportType]]


def write_to_new_file(filename: str, filecontent: str):
    with open(filename, "w+") as file:
        file.write(filecontent)


def geo_distance(origin, destination):
    lat1, lon1 = origin
    lat2, lon2 = destination
    radius = 6371  # km

    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) * math.sin(dlat / 2) +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon / 2) * math.sin(dlon / 2))
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    d = radius * c

    return d


def gather_bus_edges(stop_keys: set[str]) -> list[tuple[str, str]]:
    edges: list[tuple[str, str]] = []
    with open("./stcp_data/route_stops.csv") as file:
        seq = -1
        last_stop = ""
        for line in file.readlines()[1:]:
            line = line.replace("\n", "").replace("\"", "")
            content = line.split(',')

            cur_stop = content[2]
            new_seq = int(content[6])
            if new_seq == seq + 1:
                seq = new_seq
                if new_seq > 1:
                    edges.append((last_stop, cur_stop))
                last_stop = cur_stop
            else:
                edges.append((last_stop, cur_stop))
                last_stop = cur_stop
                seq = new_seq
                last_stop = cur_stop

    # TODO: Add transfers

    # remove stops not in porto municipality
    edges = list(
        filter(lambda x: x[0] in stop_keys and x[1] in stop_keys, edges)
    )

    return edges


def gather_metro_edges(stop_keys: set[str]) -> list[tuple[str, str]]:
    edges: list[tuple[str, str]] = []
    with open("../metro data/stop_times.csv") as file:
        seq = -1
        last_stop = ""
        just_changed = True
        for line in file.readlines()[1:]:
            line = line.replace("\n", "").replace("\"", "")
            content = line.split(';')

            cur_stop = content[3]
            new_seq = int(content[4])
            if new_seq == seq + 1:
                seq = new_seq
                if not just_changed:
                    edges.append((last_stop, cur_stop))
                else:
                    just_changed = False
                last_stop = cur_stop
            else:
                edges.append((last_stop, cur_stop))
                last_stop = cur_stop
                seq = new_seq
                last_stop = cur_stop
                just_changed = True

    # removed repeated edges
    _edges = edges.copy()
    edges = []
    for edge in _edges:
        if edge not in edges:
            edges.append(edge)

    # remove stops not in porto municipality
    edges = list(
        filter(lambda x: x[0] in stop_keys and x[1] in stop_keys, edges)
    )

    return edges


def floyd_warshall(verts: list[str], edges: list[tuple[str, str, float]]):
    nverts = len(verts)
    vert_idx = {}
    for i in range(len(verts)):
        vert_idx[verts[i]] = i

    dist = [[sys.float_info.max for _ in range(nverts)] for _ in range(nverts)]

    for (u, v, w) in edges:
        dist[vert_idx[u]][vert_idx[v]] = w
    for v in verts:
        dist[vert_idx[v]][vert_idx[v]] = 0
    for k in range(1, nverts):
        print(
            f"Calculating the distances: {round((k-1)/(nverts-2)*100, 2)}%\r",
            end="",
            flush=True
        )

        for i in range(1, nverts):
            for j in range(1, nverts):
                if dist[i][j] > (dist[i][k] + dist[k][j]):
                    dist[i][j] = dist[i][k] + dist[k][j]
    print()

    edges: list[tuple[str, str, float]] = []

    for i in range(len(dist)):
        for j in range(i+1, len(dist)):
            if dist[i][j] < sys.float_info.max:
                edges.append((verts[i], verts[j], dist[i][j]))

    return edges


def main():
    stops: list[TransportStop] = []
    stop_keys: set[str] = set()

    graph: dict[str, StopNode] = {}

    # stcp
    with open("../data/stops_in_porto.json") as stops_file:
        stops: list[TransportStop] = json.load(stops_file)
        for stop in stops:
            graph[stop["id"]] = stop
            stop_keys.add(stop["id"])

    # gather edges
    bus_edges = gather_bus_edges(stop_keys)
    print("bus edges", len(bus_edges))

    metro_edges = gather_metro_edges(stop_keys)
    print("metro edges", len(metro_edges))

    # merge edges
    all_edges: list[tuple[str, str, TransportType]] = []
    print(graph[bus_edges[0][0]]["location"])
    all_edges.extend(
        map(lambda x: (x[0], x[1],
                       geo_distance(
                           graph[x[0]]["location"],
                           graph[x[1]]["location"])),
            bus_edges)
    )
    all_edges.extend(
        map(lambda x: (x[0], x[1],
                       geo_distance(
                           graph[x[0]]["location"],
                           graph[x[1]]["location"])),
            metro_edges)
    )

    edges = floyd_warshall(list(graph.keys()), all_edges)

    write_to_new_file("../data/graph.json",
                      json.dumps(edges, ensure_ascii=False))


if __name__ == "__main__":
    main()
