FROM rust:1.67.1

ENV ROCKET_ADDRESS=0.0.0.0
ENV ROCKET_PORT=6666

# Install socat
RUN apt-get update && apt-get install -y socat

RUN rustup default nightly-2023-03-09

RUN USER=root cargo new --bin app

WORKDIR "/app"

COPY app/Cargo.toml ./Cargo.toml
COPY app/Cargo.lock ./Cargo.lock

RUN cargo build --release && rm -rf src

COPY app/src ./src
COPY app/templates ./templates
COPY app/start.sh ./start.sh

RUN cargo build --release


RUN mkdir -p /tmp
VOLUME ["/tmp"]
RUN rm -f /tmp/app.sock
VOLUME ["/app/target"]

RUN cargo build

CMD ["bash", "-c", "./start.sh"]
