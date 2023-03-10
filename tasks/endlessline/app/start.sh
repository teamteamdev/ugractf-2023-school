#!/bin/bash

rm -f /tmp/app.sock
socat UNIX-LISTEN:/tmp/app.sock,fork,mode=0666 TCP4-CONNECT:127.0.0.1:6666 &
cargo run