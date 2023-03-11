#!/bin/sh
set -e
exec nix run . $1 $2
