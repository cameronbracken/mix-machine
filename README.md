## The Mix Machine

The Mix Machine is a collection of scripts to automatically make DJ mixes. 

Given a collection of mp3's The Mix Machine will beatmatch or crossfade tracks, 
and spit out a single mp3 file with a continuous mix.  At the heart of 
The Mix Machine is a python script (`mix_machine.py`) that utilizes the 
EchoNest remix package and API to do audio analysis. Parallel processing is 
used wherever possible to speed things up. 

The Mix Machine can do the following:

1. Convert your music files to a common mp3 format (remix will barf on some music files)
2. Upload your files to EchoNest
3. Order the music files in terms of tempo
4. Mix the files, beatmatching where appropriate, or fading when the tempos are off

## Requirements 

1. Set your EchoNest API key `export ECHO_NEST_API_KEY="your api key"`
2. The remix python package `pip install remix`

## Usage

1. Put your mp3's in a directory 
2. Edit the variables at the top `mix_machine.sh`, including your Echonest API Key
3. `./mix_machine.sh`

## Output quality 

By default remix will output 120k mp3's, and to my knowledge there 
is not a way to change this. I had to hack the remix source to 
allow for 320k files. 

## `mix_machine.py`

`mix_machine.py` is a standalone script that does most of the work of 
putting together the mix. It can be used separately from The Mix Machine
shell scripts.

Usage: mix_machine.py [options] <list of mp3s>

Options:
  -h, --help            show this help message and exit
  -a APIKEY, --apikey=APIKEY
                        EchoNest API key (required)
  -x CROSSFADE, --crossfade=CROSSFADE
                         fade between songs default=10
  -f, --fadeonly        beatmatch and fade only, don't temposhift and
                        beatmatch tracks
  -o, --order           automatically order tracks
  -e, --equalize        automatically adjust volumes
  -v, --verbose         show results on screen
  -m, --multiprocessing
                        Use the multiprocessing module to run taskes in
                        parallel.

## Discalimer

Does The Mix Machine make human DJs obsolete? Heck no! 

The Mix Machine can only do so much with what it has, if two songs don't match
up well, the trasition will be weird, no matter what. It takes a lot of thought 
to put together songs that will flow well, and no amout of software will replace 
a good DJ. 

## History

The Mix Machine is heavily based on the remix example `capsule.py`. Originally
The Mix Machine was just a hacked version of that script. `capsule.py` was 
basically inteded to make power hour mixes, and so had some subtle differences
from the application of making a DJ mix, where we want to include as much 
of the song as possible. It ended up being easier to re-write most of the code 
to be sure everything was working correctly. 