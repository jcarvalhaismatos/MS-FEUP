DATA_FOLDER=data
ROUTE_STOPS_FILE="${DATA_FOLDER}/route_stops.csv"


ROUTE_KEYS=`cat ../routes.txt | cut -f 1 -d ',' | tail -n +2`

mkdir $DATA_FOLDER
rm "${DATA_FOLDER}/*"
echo "" > $ROUTE_STOPS_FILE
echo "lcode,dir,code,name,zone,address,sequence" > $ROUTE_STOPS_FILE

function extract_route() {
	echo "extracting route ${1}, direction ${2}"
	FETCH_DATA=`curl -s -S "https://www.stcp.pt/pt/itinerarium/callservice.php?action=linestops&lcode=${1}&ldir=${2}"`

	NUMBER_OF_RECORDS=`echo $FETCH_DATA | jq -r .recordsReturned`
	echo "Returned ${NUMBER_OF_RECORDS} records"

	if [ $NUMBER_OF_RECORDS -gt 0 ]; then
		FILENAME="${DATA_FOLDER}/${1}_${2}.csv"

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
