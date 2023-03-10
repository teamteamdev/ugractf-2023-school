FROM imachug/kyzylborda_lib
RUN apk add --no-cache socat gawk

COPY log.csv isolate_binaries.sh start.sh task.py lost_souls.txt /app/
RUN /app/isolate_binaries.sh
WORKDIR /app
CMD ["/app/start.sh"]
