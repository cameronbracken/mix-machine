#!/usr/bin/env python
# encoding: utf=8

"""
mix_machine_utils.py

Created by Cameron Bracken
"""

from echonest.remix.action import Crossfade, Playback, Crossmatch, humanize_time
from numpy import argmin, amax, absolute, array, argsort

LOUDNESS_THRESH = -8
TEMPO_THRESH = 0.1

def beatmatch(t1, t2, xfade):
    """
    cross fades between two tracks with beatmatching
    """
    
    b1 = t1.analysis.beats
    b2 = t2.analysis.beats

    beat_starts1 = array([x.start for x in b1])
    beat_starts2 = array([x.start for x in b2])

    # find the beat index that is closest to the xfade time
    time1 = argmin(absolute(beat_starts1 - amax(beat_starts1) + xfade))
    nbeats = len(range(time1,len(b1)))

    fade_out_beats = b1[-(nbeats+1):-1]
    fade_in_beats = b2[0:nbeats]
            
    l1 = [(s.start,s.duration) for s in fade_out_beats]
    l2 = [(s.start,s.duration) for s in fade_in_beats]

    #end_t1 = fade_out_beats[0].start
    #start_t2 = fade_in_beats[-1].start

    start_fade_t1, end_fade_t1 = l1[0][0], sum(l1[-1])
    start_fade_t2, end_fade_t2 = l2[0][0], sum(l2[-1])

    #import pdb; pdb.set_trace()
    #reload(sys)
    #sys.setdefaultencoding('utf8')

    return (Crossmatch((t1,t2), (l1,l2)), start_fade_t1, end_fade_t2)


def cross_fade_match(t1, t2, xfade, start_beat_t2=2):
    """
    Returns times to start crossfading two tracks based on the beats
    matches the closest beat to the xfade time from the beginning or 
    ending of the track
    """
    beat_times1 = array([x.start for x in t1.analysis.beats])
    beat_times2 = array([x.start for x in t2.analysis.beats])

    duration1 = t1.analysis.duration

    time1 = argmin(absolute(beat_times1 - amax(beat_times1) + xfade))
    time2 = start_beat_t2

    # move a few beats back so we arent starting right at the 
    start_fade_t1 = beat_times1[time1-1]
    start_fade_t2 = beat_times2[time2]

    # if we want to beatmatch exactly, we can only have 
    # a target xfade duration
    end_fade_t2 = start_fade_t2 + xfade

    cf = Crossfade([t1, t2], (start_fade_t1, start_fade_t2), xfade)
    return (cf, start_fade_t1, end_fade_t2)

def fade_and_play(t1,t2,t3,xfade):
    """
    Crossmatch or if the tempo difference is too great, Crossfade between 
    track 1 and 2, and playback 2, need the track 3 to determine where to 
    stop playing track 2
    """
    force_fade = check_tempos(t1,t2)

    if fadeonly or force_fade:
        (crossfade_t12, end_t1, start_t2) = cross_fade_match(t1,t2, xfade)
        (crossfade_t23, end_t2, start_t3) = cross_fade_match(t2,t3, xfade)
        fade = crossfade_t12
    else:
        (beatmatch_t12, end_t1, start_t2) = beatmatch(t1,t2,xfade)
        (beatmatch_t23, end_t2, start_t3) = beatmatch(t2,t3,xfade)
        fade = beatmatch_t12
    pb = Playback(t2, start_t2, end_t2 - start_t2)

    return (fade, pb)

def equalize_tracks(tracks):
    
    def db_2_volume(loudness):
        return (1.0 - LOUDNESS_THRESH * (LOUDNESS_THRESH - loudness) / 100.0)
    
    for track in tracks:
        loudness = track.analysis.loudness
        track.gain = db_2_volume(loudness)

def order_tracks(tracks):
    """ 
    Finds the smoothest ordering between tracks, based on tempo only.

    TODO: sorting shapes
    """
    tempos = [track.analysis.tempo['value'] for track in tracks]
    
    order = argsort(tempos)
    return [tracks[i] for i in order]

def check_tempos(t1,t2):
    """
    Returns True if the percent difference between the two tempos is 
    greater than the threshold, meaning the tempos are different 
    enough that beat matching may sound funny
    """
    tempo1 = t1.analysis.tempo['value']
    tempo2 = t1.analysis.tempo['value']
    percent_diff = abs(tempo1 - tempo2)/(tempo1 + tempo2)

    if(percent_diff > TEMPO_THRESH):
        return True
    else:
        return False

def display_songlist(actions):
    total = 0
    print
    print "Time - Artist - Song - Album"
    for a in actions:
        if "Playback" in unicode(a):
            m = a.track.analysis.metadata
            print "%s - %s - %s - %s" % (humanize_time(total),m['artist'], m['title'], m['album'])
        total += a.duration
    print

def display_volume(tracks):
    print
    print "Volume Adjustments:"
    for track in tracks:
        print "Vol = %.0f%%\t%s" % (track.gain*100.0, track.filename)
    print

def display_tempos(tracks):
    print
    print "BPM (confidence):"
    for track in tracks:
        m = track.analysis.metadata
        tempo = track.analysis.tempo
        print "%s(%3d%%)\t %s\t %s" % (tempo['value'],tempo['confidence']*100.0,m['artist'], m['title'])
    print

def tuples(l, n=2):
    """ returns n-tuples from l.
        e.g. tuples(range(4), n=2) -> [(0, 1), (1, 2), (2, 3)]
    """
    return zip(*[l[i:] for i in range(n)])
