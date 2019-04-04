if [[ $1 ]]
then
  TODAY=$1
else
  TODAY=$(date -I)
fi
SESSIONS=$(grep $TODAY revision.csv | cut -f 1 -d ',' --complement)
if [[ $SESSIONS ]]
then
  echo "revision schedule for $TODAY"
  sed q revision.csv | cut -f 1 -d ',' --complement | awk '{gsub(",", "\t", $0); print}'
  echo $SESSIONS | awk '{gsub(",", "\t\t", $0); print}'
else
  echo "Nothing on today :)"
fi
