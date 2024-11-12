#!/bin/bash

INPUT_FILE="$1"
OUTPUT_FILE="$2"

cat "$INPUT_FILE"

cat "$INPUT_FILE" | jq -r ".features[] | {id: .properties.id, name: .properties.name, type: .properties.border_type, geometry: .geometry.coordinates[0]}" | jq -s > "$OUTPUT_FILE"

