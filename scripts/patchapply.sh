#!/bin/bash
##======================================================================##
##  patchapply
##   # :mode=shellscript:tabSize=3:indentSize=3:
##  Fri May 13 14:48:03 PDT 2016 @950 /Internet Time/
##  Purpose: apply all unapplied patch scripts to a database.
##======================================================================##

# sensible defaults...
DBUSER=
DBNAME=
DBHOST="localhost"
DBPORT="5432"
CL_OPTS="U:d:h:p:nV?"

##======================================================================##
function logecho(){
   NOW_DATE=`date`
   local TEXT="[$NOW_DATE] $1"
   echo "$TEXT" |tee -a $LOGFPATH
}

##======================================================================##
function print_usage(){
   echo "Usage: $AGENT.sh -$CL_OPTS"
	echo " -U  [string]  = PostgreSQL user"
	echo " -d  [string]  = PostgreSQL database"
	echo " -h  [string]  = PostgreSQL host [now: $DBHOST]"
	echo " -p  [integer] = PostgreSQL service port [now: $DBPORT]"
	echo " -V  [flag]    = print version and exit"
}

##======================================================================##
## Mainlogic.
##======================================================================##
while getopts "$CL_OPTS" OPT
do
   case $OPT in
   U) DBUSER="$OPTARG";;
   d) DBNAME="$OPTARG";;
   h) DBHOST="$OPTARG";;
   p) DBPORT="$OPTARG";;
   V) echo "$AGENT v$APP_VERSION";exit 1;;
   \?) print_usage;exit 1;;
   *) print_usage;exit 1;;
   esac
done

##======================================================================##
## Apply patches.
##======================================================================##
for FILE in `ls patches/*.sql | sort -V`; do
	logecho "Applying patch: ${FILE}"
	psql -p $DBPORT -h $DBHOST -U $DBUSER -d $DBNAME -f $FILE
done;