#!/usr/bin/env bash
if [ -d frames ]; then
    rm -r frames
fi
mkdir frames

ffmpeg -ss 47.0 -i "$1" -r 10 frames/%06d.png 2>/dev/null
for frame in frames/*; do
    if [ -e tmp.png ]; then
        rm tmp.png
    fi
    # echo "$frame" >&2
    convert "$frame" -crop 50%x80%+225+50 -modulate 50 tmp.png
    ./jabcode/src/jabcodeReader/bin/jabcodeReader tmp.png
done | grep -v "JABCode Error:" | uniq | base64 -d >flag.png
