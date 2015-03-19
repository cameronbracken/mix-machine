#!/bin/bash

# take a directory with mp3s
# converts each mp3 to wav then back to mp3
# this can fix some problems with other software

#set -x

mkdir $2 

i=0 
for f in $1/*
do
 let i=i+1 
 echo "Processing $f"

 base=$(basename "$f")
 fn="${base%.*}"
 wav=tmp$(printf '%02d' $i).wav

 ffmpeg -loglevel quiet -y -i "$f" $wav
 ffmpeg -loglevel quiet -y -i $wav -q:a 0 "$2/$fn.mp3" &
done

echo "Converting..."
wait

i=0
for f in $1/*
do
 let i=i+1 
 wav=tmp$(printf '%02d' $i).wav
 rm $wav
done   

#set +x
