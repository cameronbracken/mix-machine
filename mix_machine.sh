#!/bin/bash

mp3_dir="tracks"
fixed_dir="fixed_tracks"
final_mix="mixed.mp3"
api_key=$ECHO_NEST_API_KEY

################
# OPTIONS
################

# order the tracks automatically or keep order based on file names
# note the file name order is based on the unix convention, not the 
# mac finder convention
order=yes

# x-fade between songs
transition=20

# Convert files to mp3 before any analysis. This really converts 
# <file> -> wav -> mp3, fixing some mp3 files that pyechonest/remix would 
# otherwise crash on (due to poorly constructed ffmpeg calls). If you have 
# files in any other format (m4a for example), or you are getting crashes, 
# this is recommended.
convert=yes

# Upload the tracks directly to echonest using curl on the command line, 
# sometimes the python script times out, not sure why 
upload=yes

outputV0=yes








##############################
### Dont change below here ###      
##############################

# set up flag for ordering tracks
if [ "$order" = "yes" ]; then
    order_flag="-o"
else
    order_flag=""
fi

echo "Converting music files..." 
# echonest will crash on some files
if [ "$convert" = "yes" ]; then
    ./mp3tomp3.sh "$mp3_dir" "$fixed_dir"
else 
    cp -r "$mp3_dir" "$fixed_dir"
fi


if [ "$upload" = "yes" ]; then
i=0
for f in "${fixed_dir}"/*
do
    let i=i+1
    echo $f
    curl --silent -F "api_key=$api_key" -F "filetype=mp3" -F "track=@${f}" "http://developer.echonest.com/api/v4/track/upload" &
done

echo "Uploading..."
wait
rm *.wav
fi

# mix, fade and beatmatch
export PYTHONDONTWRITEBYTECODE=1
python mix_machine.py -a $api_key -m -v -e $order_flag -x $transition "${fixed_dir}"/*

# convert to V0
if [ "$outputV0" = "yes" ]; then
    ffmpeg -loglevel quiet -i capsule.mp3 -q:a 0 "$final_mix"
else
    cp capsule.mp3 "$final_mix"
fi

#clean up 
rm -rf "$fixed_dir"
rm capsule.mp3
