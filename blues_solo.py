"""Synthesizes a blues solo algorithmically."""

import atexit
import os
from random import choice

from psonic import *

# The sample directory is relative to this source file's directory.

SAMPLES_DIR = os.path.join(os.path.dirname(__file__), "samples")

SAMPLE_FILE = os.path.join(SAMPLES_DIR, "bass_D2.wav")
SAMPLE_NOTE = D2  # the sample file plays at this pitch
BACKING_TRACK = os.path.join(SAMPLES_DIR, "backing.wav")
sample(BACKING_TRACK, amp=2)
sleep(2.25)  # delay the solo to match up with backing track

def play_note(note, beats=1, bpm=60, amp=1):
    """Plays note for `beats` beats. Returns when done."""
    # `note` is this many half-steps higher than the sampled note
    half_steps = note - SAMPLE_NOTE
    # An octave higher is twice the frequency. There are twelve half-steps per octave. Ergo,
    # each half step is a twelth root of 2 (in equal temperament).
    rate = (2 ** (1 / 12)) ** half_steps
    assert os.path.exists(SAMPLE_FILE)
    # Turn sample into an absolute path, since Sonic Pi is executing from a different working directory.
    sample(os.path.realpath(SAMPLE_FILE), rate=rate, amp=amp)
    sleep(beats * 60 / bpm)
    


def stop():
    """Stops all tracks."""
    msg = osc_message_builder.OscMessageBuilder(address='/stop-all-jobs')
    msg.add_arg('SONIC_PI_PYTHON')
    msg = msg.build()
    synthServer.client.send(msg)

atexit.register(stop)  # stop all tracks when the program exits normally or is interrupted

# These are the piano key numbers for a 3-octave blues scale in A. See: http://en.wikipedia.org/wiki/Blues_scale
blues_scale = [40, 43, 45, 46, 47, 50, 52, 55, 57, 58, 59, 62, 64, 67, 69, 70, 71, 74, 76]
beats_per_minute = 45				# Let's make a slow blues solo

# play_note(blues_scale[0], beats=1, bpm=beats_per_minute)



curr_note = 0
play_note(blues_scale[curr_note], 1, beats_per_minute)
licks = [[(1, 0.5), (1, 0.5), (1, 0.5), (1, 0.5)],
         [(-1, 0.5), (-1, 0.5), (-1, 0.5), (-1, 0.5)],
         [(1, 0.6), (1, 0.4), (-1, 0.6), (-2, 0.4)],#Swung
         [(2, 0.4), (-1, 0.2), (-1, 0.6), (1, 0.8)]
         ]
lowest_change = 0
highest_change = 0
lowest_licks = [] #keeps track of licks that go lowest and highest
highest_licks = []
for i,lick in enumerate(licks):
    current_change = 0
    low_lick = False #Flags to indicate if licks go low or high
    lowest_lick = False
    high_lick = False
    highest_lick = False
    #Checks each note to see how much the pitch changes
    #To be used later to prevent going over top or under bottom
    #Chosing different licks instead of holding note out.
    for note in lick:
        current_change += note[0]
        #Update low/high flags
        if current_change<lowest_change:
            lowest_change=current_change
        if current_change <0:
            low_lick = True
        if current_change>highest_change:
            highest_change = current_change
        if current_change>0:
            high_lick = True
    if high_lick == True:
        highest_licks.append(i)#add to list of lowest
    if low_lick == True:
        lowest_licks.append(i)

#Make list of acceptable licks, and remove unacceptable ones
acceptable_for_low = list(range(len(licks)))
for bad_lick in lowest_licks:
    acceptable_for_low.remove(bad_lick)


acceptable_for_high = list(range(len(licks)))
for bad_lick in highest_licks:
    acceptable_for_high.remove(bad_lick)


for _ in range(10):
    if curr_note >= len(blues_scale)-1-highest_change:
        #
        lick = licks[choice(acceptable_for_high)];
    elif curr_note <= -lowest_change:
        lick = licks[choice(acceptable_for_low)]
    else:
        lick = licks[choice(range(len(licks)))]
    for note in lick:
        curr_note += note[0]
        print(curr_note)
        play_note(blues_scale[curr_note], note[1], beats_per_minute)

