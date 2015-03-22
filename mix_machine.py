#!/usr/bin/env python
# encoding: utf=8

"""
mix_machine.py based on capsule.py

accepts songs on the commandline, order them, beatmatch them, and output an audio file

Created by Cameron Bracken

Originally created by Tristan Jehan and Jason Sundram.
"""

import os
import sys
reload(sys)
sys.setdefaultencoding('utf8')
from optparse import OptionParser

from pyechonest import config

from echonest.remix.action import render, make_stereo
from echonest.remix.action import display_actions
from echonest.remix.action import Crossfade, Playback, Crossmatch, Fadein, Fadeout, humanize_time
from echonest.remix.audio import LocalAudioFile
from echonest.remix import audio
from pyechonest import util


import mix_machine_utils
reload(mix_machine_utils)
from mix_machine_utils import *


#from multiprocessing import Pool
from multiprocessing.dummy import Pool as ThreadPool

def do_work(audio_files, options):

    if(len(audio_files) < 3):
        raise Exception('Cant make a mix with less than 3 songs.')

    api_key = options.apikey
    xfade = int(options.crossfade)
    fadeonly = bool(options.fadeonly)
    order = bool(options.order)
    equal = bool(options.equalize)
    verbose = bool(options.verbose)
    mp = bool(options.multiprocessing)

    config.ECHO_NEST_API_KEY=api_key
    
    # Get pyechonest/remix objects
    def analyze(filename):
        la = LocalAudioFile(filename, verbose=verbose, sampleRate = 44100, numChannels = 2)
        return(la)

    if mp == True:
        p = ThreadPool()
        tracks = p.map(analyze, audio_files)
        p.close()
        p.join()
    else:
        tracks = map(analyze, audio_files)

    # decide on an initial order for those tracks
    if order == True:
        if verbose: print "Ordering tracks..."
        tracks = order_tracks(tracks)
    
    if verbose:
        display_tempos(tracks)

    if equal == True:
        equalize_tracks(tracks)
        if verbose:
            display_volume(tracks)
    
    # first playback the first track to start the mix,
    # cross fade with the second track
    t1,t2 = (tracks[0],tracks[1])
    mix = [start_mix(t1,t2,xfade,fadeonly)]

    # a triple is centered on track 2 of a triple,
    # the goal is to fade t1 and t2 and playback t2 but 
    # we need to know when the fade starts with t3
    #   1. it xfades track 1,2 and tracks 2,3
    #   2. plays 2 back
    for (t1,t2,t3) in tuples(tracks,n=3):
        mix.extend(fade_and_play(t1,t2,t3,xfade,fadeonly))
    
    # last fade and playback
    mix.extend(end_mix(t2,t3,xfade,fadeonly))
        

    #import pdb; pdb.set_trace()
    #reload(sys)
    #sys.setdefaultencoding('utf8')
    return mix

def get_options(warn=False):
    usage = "usage: %s [options] <list of mp3s>" % sys.argv[0]
    parser = OptionParser(usage=usage)
    parser.add_option("-a", "--apikey", help="EchoNest API key (required)")
    parser.add_option("-x", "--crossfade", default=10, help=" xfadeition between songs default=10")
    parser.add_option("-f", "--fadeonly", action="store_true", help="beatmatch and fade only, don't temposhift and beatmatch tracks")
    parser.add_option("-o", "--order", action="store_true", help="automatically order tracks")
    parser.add_option("-e", "--equalize", action="store_true", help="automatically adjust volumes")
    parser.add_option("-v", "--verbose", action="store_true", help="show results on screen")        
    parser.add_option("-m", "--multiprocessing", action="store_true", help="Use the multiprocessing module to run taskes in parallel.")
    
    (options, args) = parser.parse_args()
    if warn and len(args) < 2: 
        parser.print_help()
    return (options, args)
    
def main():
    options, args = get_options(warn=True);
    actions = do_work(args, options)
    verbose = bool(options.verbose)
    
    if verbose:
        display_actions(actions)
        display_songlist(actions)
        print "Output Duration = %.3f sec" % sum(act.duration for act in actions)
    
        print "Rendering..."
    # Send to renderer
    #import pdb; pdb.set_trace()
    render(actions, 'capsule.mp3', verbose)
    return 1
    
if __name__ == "__main__":
    main()
