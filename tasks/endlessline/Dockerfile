FROM rust:1.67.1

ENV ROCKET_ADDRESS=0.0.0.0
ENV ROCKET_PORT=6666

# Install socat
RUN apt-get update && apt-get install -y socat

RUN rustup default nightly-2023-03-09

COPY app /app
WORKDIR "/app"

RUN mkdir -p /tmp
VOLUME ["/tmp"]
RUN rm -f /tmp/app.sock
VOLUME ["/app/target"]

RUN cargo build --release

CMD ["bash", "-c", "./start.sh"]