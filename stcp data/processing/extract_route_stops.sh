DATA_FOLDER=data
ROUTE_STOPS_FILE="${DATA_FOLDER}/route_stops.csv"
STOP_CODES_FILE="${DATA_FOLDER}/stop_codes.csv"
STOPS_FILE="${DATA_FOLDER}/stops.csv"

ROUTE_KEYS=`cat ../routes.txt | cut -f 1 -d ',' | tail -n +2`

mkdir $DATA_FOLDER
mkdir "${DATA_FOLDER}/lines"
rm "${DATA_FOLDER}/*"
echo "" > $ROUTE_STOPS_FILE
echo "lcode,dir,stop_code,name,zone,address,sequence" > $ROUTE_STOPS_FILE

echo "" > $STOPS_FILE
echo "stop_code,stop_name,stop_lat,stop_lon,zone_id" > $STOPS_FILE

function extract_route() {
	echo "extracting route ${1}, direction ${2}"
	FETCH_DATA=`curl -s -S "https://www.stcp.pt/pt/itinerarium/callservice.php?action=linestops&lcode=${1}&ldir=${2}"`

	NUMBER_OF_RECORDS=`echo $FETCH_DATA | jq -r .recordsReturned`
	echo "Returned ${NUMBER_OF_RECORDS} records"

	if [ $NUMBER_OF_RECORDS -gt 0 ]; then
		FILENAME="${DATA_FOLDER}/lines/${1}_${2}.csv"

		# put headers into file
		echo "code,name,zone,address,sequence" > $FILENAME

		echo $FETCH_DATA | jq -r ".records[] | [.code,.name,.zone,.address,.sequence] | @csv" | sort -t ',' -k5 -h | cat >> $FILENAME

		echo $FETCH_DATA | jq -r ".records[] | [.code,.name,.zone,.address,.sequence] | @csv" | sort -t ',' -k5 -h | cat >> temp

		cat temp | while read line 
		do
			echo "${1},${2},${line}" >> $ROUTE_STOPS_FILE
		done
		rm temp
	fi
}

for route in $ROUTE_KEYS
do
	extract_route $route 0
	extract_route $route 1
done

# get stop_codes
# remove duplicate stop_codes
tail $ROUTE_STOPS_FILE -n +2 | cut -f 3 -d ',' |  sort | uniq | sed 's/\"//g' | cat > $STOP_CODES_FILE

# find which routes we dont have data still
STCP_STOPS_DATA=`tail ../stops.txt -n +2 | cut -f 2 -d ',' | sort | uniq | cat`

STOP_CODES_TO_FETCH=unextracted_stop_codes.txt
echo "" > $STOP_CODES_TO_FETCH

for stop in `tail $STOP_CODES_FILE -n +2` 
do
	if `printf -- '%s\n' "${STCP_STOPS_DATA[@]}" | grep -q "^${stop}$"`; then
		echo  `tail ../stops.txt -n +2 | cat | grep ",${stop}," | cut -f 2-6 -d ','` >> $STOPS_FILE
	else
		echo "Did not find ${stop}"
		echo "${stop}" >> $STOP_CODES_TO_FETCH
	fi
done

rm $STOP_CODES_FILE

# get stops coordinates
function extract_stop_info() {
	echo "extracting stop ${1} info"

	FETCH_DATA=`curl -s -S "https://www.stcp.pt/pt/itinerarium/callservice.php?action=srchstoplines&stopcode=${1}"`

	PARSED_DATA=`echo $FETCH_DATA | jq -r ".[] | [.code,.name,.zone,.geomdesc] | @csv"`

	for line in "${PARSED_DATA[@]}"
	do
		line_data=`echo $line | sed 's/\"//g'`
		stop_code=`echo $line_data | cut -f 1 -d ','`
		stop_name=`echo $line_data | cut -f 2 -d ','`
		stop_lat=`echo $line | sed 's/\"\"/@/g' | sed 's/\"//g' | sed 's/@/\"/g' | cut -f 4- -d ',' | jq -r ".coordinates[0]"`
		stop_lon=`echo $line | sed 's/\"\"/@/g' | sed 's/\"//g' | sed 's/@/\"/g' | cut -f 4- -d ',' | jq -r ".coordinates[1]"`
		zone_id=`echo $line_data | cut -f 3 -d ','`

		echo "${stop_code},${stop_name},${stop_lat},${stop_lon},${zone_id}" >> $STOPS_FILE
	done
}


for stop_code in `cat ${STOP_CODES_TO_FETCH}`
do
	extract_stop_info $stop_code
done

rm $STOP_CODES_TO_FETCH

echo
echo
echo "The information about the routes can be found individually at: ${DATA_FOLDER}/lines"
echo "The information about the routes can be found at: ${ROUTE_STOPS_FILE}"
echo "The information about the stops can be found at: ${STOPS_FILE}"

