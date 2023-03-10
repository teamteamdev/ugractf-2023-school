#!/usr/bin/env ash
set -e

export flag_user=$(tail -n +2 log.csv | cut -f4 -d',' | grep -v -f lost_souls.txt | shuf -n1)
for i in `seq 1 100`; do
    str=$(shuf -i 6-10000 -n 1)
    gawk -i inplace -v s=$str -v u=$flag_user -v OFS=',' -F, 'NR==s { sub($4, u); sub($5, "false") }; 1' log.csv
done

chmod -R 700 /app
adduser -h /home/user -s /bin/ash -D user 

cp /app/log.csv /home/user/log.csv
chown user:user /home/user/log.csv

export PYTHONUNBUFFERED=1
exec socat -T30 unix-l:/tmp/app.sock,mode=0666,fork exec:"$PWD/task.py $1"