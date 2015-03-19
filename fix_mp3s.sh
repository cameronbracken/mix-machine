#!/bin/bash
set -x

mkdir $2 

for f in $1/*.mp3
do
 echo "Processing $f"
 base=$(basename "$f")
 ffmpeg -loglevel quiet -i "$f" tmp.wav
 ffmpeg -loglevel quiet -i tmp.wav -q:a 0 "mp3s_fixed/$base"
 rm tmp.wav
done

set +x