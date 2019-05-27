#!/bin/sh
if [ $1 ]
then
  TODAY=$1
else
  TODAY=$(date -I)
fi
SESSIONS=$(grep $TODAY revision.csv | cut -f 1 -d ',' --complement)
if [ $SESSIONS ]
then
  RED="\033[31m"
  GREEN="\033[32m"
  YELLOW="\033[33m"
  BLUE="\033[34m"
  DEFAULT="\033[39m"
  echo -n $YELLOW
  echo -n "revision schedule for: $RED"
  echo $TODAY
  echo -n $GREEN
  sed q revision.csv | cut -f 1 -d ',' --complement | awk '{gsub(",", "\t", $0); print}'
  echo -n $BLUE
  echo $SESSIONS | awk '{gsub(",", "\t\t", $0); print}'
  echo -n $DEFAULT
else
  echo "Nothing on today :)"
fi
