all: prepare run

INPUT_FILE="../openstreetmap data/freguesias_municipios.geojson"
OUTPUT_FILE="../data/freguesias.json"
OUTPUT_FREGUESIAS_FILE="../data/freguesias.json"
OUTPUT_MUNICIPIO_FILE="../data/municipio_porto.json"

prepare:
	mkdir -p ../data

run: run_freguesias

run_freguesias:
	bash freguesias.sh $(INPUT_FILE) $(OUTPUT_FILE)
	python3 municipio_do_porto.py $(OUTPUT_FILE) $(OUTPUT_FREGUESIAS_FILE) $(OUTPUT_MUNICIPIO_FILE)
