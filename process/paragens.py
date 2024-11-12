#!/bin/python3

from typing import TypedDict
from enum import Enum
import json


class TransportType(Enum):
    BUS = 0
    METRO = 1


class TransportStop(TypedDict):
    id: int
    name: str
    zone: str
    location: list[float]
    bus: bool
    metro: bool


def pnpoly(verts: list[list[float]], testp: list[float]) -> bool:
    nvert: int = len(verts)
    testx = testp[0]
    testy = testp[1]

    i: int = 0
    j: int = nvert - 1
    c: bool = False

    while i < nvert:
        vertx_i = verts[i][0]
        verty_i = verts[i][1]
        vertx_j = verts[j][0]
        verty_j = verts[j][1]

        if ((verty_i > testy) != (verty_j > testy)) and \
                (testx < (vertx_j - vertx_i)
                 * (testy - verty_i) / (verty_j - verty_i) + vertx_i):
            c = not c
        j = i
        i = i + 1

    return c


def write_to_new_file(filename: str, filecontent: str):
    with open(filename, "w+") as file:
        file.write(filecontent)


def new_stop(
    id: int,
    name: str,
    zone: str,
    location: list[float],
    trans_type: TransportType
) -> TransportStop:
    return {
        "id": id,
        "name": name,
        "zone": zone,
        "location": list(map(lambda x: float(x), location)),
        "bus": trans_type == TransportType.BUS,
        "metro": trans_type == TransportType.METRO,
    }


def main():
    stops: list[TransportStop] = []

    # stcp
    with open("./stcp_data/stops.csv") as stops_file:
        header = True
        for line in stops_file.readlines():
            if header:
                header = False
                continue

            content: list[str] = line.split(',')

            stop: TransportStop = new_stop(
                id=content[0],
                name=content[1],
                zone=content[4].replace("\n", ""),
                location=[content[2], content[3]],
                trans_type=TransportType.BUS
            )

            stops.append(stop)

    # metro
    with open("../metro data/stops.txt") as stops_file:
        header = True
        for line in stops_file.readlines():
            if header:
                header = False
                continue

            content: list[str] = line.split(',')

            stop: TransportStop = new_stop(
                id=content[0],
                name=content[2],
                zone=content[6],
                location=[content[4], content[5]],
                trans_type=TransportType.METRO
            )

            stops.append(stop)

    write_to_new_file(
        "../data/all_stops.json",
        "[\n" + ",\n".join(list(
            map(lambda x: json.dumps(x, ensure_ascii=False), stops)
        )) + "\n]"
    )

    # check in with parish they belong
    # BUG: freguesias have the latitude and longitude switched
    parishes = {}
    with open("../data/freguesias.json") as file:
        data = json.loads(file.read())

        for li in data:
            li["geometry"] = list(map(lambda x: [x[1], x[0]], li["geometry"]))
            parishes[li["name"]] = li

    stops_in_parish: dict[str, list[TransportStop]] = {}
    stops_located = set()
    for par in parishes.keys():
        stops_in_parish[par] = []

        for stop in stops:
            if pnpoly(parishes[par]["geometry"], stop["location"]):
                stops_in_parish[par].append(stop["id"])
                stops_located.add(stop["id"])

    # write what stops are in each parish
    write_to_new_file(
        "../data/stops_per_parish.json",
        json.dumps(stops_in_parish, ensure_ascii=False)
    )

    print("Stops not in any parish:", len(list(
        filter(lambda x: x["id"] not in stops_located, stops)
    )))

    stops_in_porto: list[TransportStop] = []
    print("all stops", len(stops))
    for st in stops:
        if st["id"] in stops_located:
            stops_in_porto.append(st)
    print("stops in porto", len(stops_in_porto))

    write_to_new_file(
        "../data/stops_in_porto.json",
        "[\n" + ",\n".join(list(
            map(lambda x: json.dumps(x, ensure_ascii=False), stops_in_porto)
        )) + "\n]"
    )


if __name__ == "__main__":
    main()
