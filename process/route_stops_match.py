#!/bin/python3

import sys


def main():
    assert len(sys.argv) == 5
    stop_codes_filepath = sys.argv[1]
    stop_codes_data_filepath = sys.argv[2]
    stops_filepath = sys.argv[3]
    stop_codes_to_fetch_filepath = sys.argv[4]

    stops_info: dict[str, str | None] = {}

    with open(stop_codes_filepath) as file:
        header = True
        for line in file.readlines():
            if header is True:
                header = False
                continue
            stops_info[line.replace("\n", "")] = None

    with open(stop_codes_data_filepath) as file:
        header = True
        for line in file.readlines():
            if header is True:
                header = False
                continue
            content: list[str] = line.split(',')
            stops_info[content[1]] = ','.join(content[1:6])

    missing: list[str] = []
    towrite: list[str] = []
    for k, v in stops_info.items():
        if v is None:
            missing.append(k)
        else:
            towrite.append(v)

    with open(stops_filepath, "w+") as file:
        file.write("\n".join(towrite))
        file.write("\n")

    with open(stop_codes_to_fetch_filepath, "w+") as file:
        file.write("\n".join(missing))


if __name__ == "__main__":
    main()
