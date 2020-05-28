#!/bin/sh

STAGING_SERVER="139.162.117.244"
USER="epa_ro"
PASSWORD='qRdk~i!_3c'
DB="epa"

LOCAL_SERVER="192.168.11.11"
LOCAL_USER="epa"
LOCAL_PASSWORD='epa'
LOCAL_DB="epa"


while [[ $# -gt 0 ]]; do
    case "$1" in
        -s|--start)
            START=$2
            shift
            shift
            ;;
        -e|--end)
            END=$2
            shift
            shift
            ;;
        *)
            echo "Use -s/--start, -e/--end for start time, end time"
            exit -1
            ;;
    esac
done


PYTHON_TIME=$(cat <<-END
import datetime as dt
t = dt.datetime.now() - dt.timedelta(days=7)
print(t.strftime("%Y-%m-%d %H:%M:%S"))
END
)

START=${START:-$(python3 -c "${PYTHON_TIME}")}
END=${END:-$(date "+%Y-%m-%d %H:%M:%S")}

mysqldump -h ${STAGING_SERVER} \
          -u ${USER} \
          -p${PASSWORD} \
          --compress \
          --skip-lock-tables \
          --where "_created_at>='${START}'" \
          --where "_created_at<='${END}'" \
          ${DB} | \
    mysql -h ${LOCAL_SERVER} \
          -u ${LOCAL_USER} \
          -p${LOCAL_PASSWORD} \
          ${LOCAL_DB}
