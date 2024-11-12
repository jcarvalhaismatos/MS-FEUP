all: prepare run

INPUT_FILE="../openstreetmap data/freguesias_municipios.geojson"
OUTPUT_FILE="../data/freguesias.json"
OUTPUT_FREGUESIAS_FILE="../data/freguesias.json"
OUTPUT_MUNICIPIO_FILE="../data/municipio_porto.json"

prepare:
	mkdir -p ../data

run: run_stcp run_freguesias

run_stcp:
	bash extract_route_stops.sh

run_freguesias:
	bash freguesias.sh $(INPUT_FILE) $(OUTPUT_FILE)
	python3 municipio_do_porto.py $(OUTPUT_FILE) $(OUTPUT_FREGUESIAS_FILE) $(OUTPUT_MUNICIPIO_FILE)
	python3 paragens.py
	python3 graph.py
