#!/bin/python3

import sys
import json
from typing import TypedDict

FREGUESIAS_DO_PORTO: list[str] = [
    "Aldoar, Foz do Douro e Nevogilde",
    "Cedofeita, Santo Ildefonso, Sé, Miragaia, São Nicolau e Vitória",
    "Lordelo do Ouro e Massarelos",
    "Bonfim",
    "Campanhã",
    "Paranhos",
    "Ramalde",
]


class Freguesia(TypedDict):
    id: int
    name: str
    type: str
    geometry: list[list[float]]


def main():
    assert len(sys.argv) == 4, "This script receives three arguments"
    assert type(sys.argv[1]) is str, \
        f"Argument of invalid type: {sys.argv[1]} is {type(sys.argv[1])}"
    assert type(sys.argv[2]) is str, \
        f"Argument of invalid type: {sys.argv[2]} is {type(sys.argv[2])}"
    assert type(sys.argv[3]) is str,  \
        f"Argument of invalid type: {sys.argv[3]} is {type(sys.argv[3])}"

    input_file: str = sys.argv[1]
    output_freguesias_file: str = sys.argv[2]
    output_municipio_file: str = sys.argv[3]
    output_freguesia: list[Freguesia] = []
    municipio_porto: Freguesia | None = None

    with open(f"{input_file}", 'r') as readfile:
        data: list[Freguesia] = json.loads(readfile.read())
        for obj in data:
            if obj["type"] == "freguesia":
                if obj["name"] in FREGUESIAS_DO_PORTO:
                    del obj["type"]
                    obj["geometry"] = obj["geometry"][0]
                    output_freguesia.append(obj)
            elif obj["type"] == "município":
                if municipio_porto is None and obj["name"] == "Porto":
                    del obj["type"]
                    obj["geometry"] = obj["geometry"][0]
                    municipio_porto = obj
            else:
                print("Unknow type", obj["type"])

    with open(output_freguesias_file, "w") as out_file:
        out_file.write("[\n" +
                       ",\n".join(
                           map(
                               lambda x: json.dumps(
                                   x, ensure_ascii=False),
                               output_freguesia))
                       + "\n]")

    with open(output_municipio_file, "w") as out_file:
        out_file.write(json.dumps(municipio_porto, ensure_ascii=True))


if __name__ == "__main__":
    main()
