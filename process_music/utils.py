import mido
import constants

import numpy as np

import sys

def _get_note_type(ticks, ticks_per_beat, note_types):
    ratio = ticks / ticks_per_beat
    if ratio < constants.NOTE_LOWER_BOUND:
        return (0, "unknown")

    i = 1
    adapted = False
    while True:
        adapted_ratio = ratio / i
        typez = [*filter(lambda x: note_types[x][0] < adapted_ratio <= note_types[x][1], note_types.keys())]
        if len(typez) > 0:
            return (i, typez[0])

        i = i + 1

        # adjust tick ratio 
        if i > constants.MAX_ATTEMPTS_ADAPTATION:
            if adapted == True:
                print("could not adapt ratio correctly")
                sys.exit(1)

            bounds    = list(note_types.values())
            old_ticks = ticks
            old_ratio = ratio 

            for bound in bounds:
                middle = (bound[0] + bound[1]) / 2
                if middle * 0.9 <= ratio <= middle * 1.1:
                    ticks = ticks_per_beat * middle
                    ratio = ticks / ticks_per_beat

            if __debug__:
                print(f"adapt tick-ratio [old, new] \t tracks [{old_ratio}, {ratio}] \t ticks [{old_ticks}, {ticks}]")

            adapted = True
            i       = 1
            continue

            # # find the differences to all ratios of ticks by factoring them with the average bound per note
            # differences = np.array([*map(lambda bounds: (((bounds[0] + bounds[1]) / 2) * ticks_per_beat) - ticks, bounds)])

            # # the difference should be lower than the smallest lower bound
            # candidates  = np.where(np.logical_and(0 < differences, differences < (ticks_per_beat * constants.NOTE_LOWER_BOUND)))[0]

            # if len(candidates) == 0:
            #     print(ticks_per_beat * constants.NOTE_LOWER_BOUND)
            #     print(ticks)
            #     print(ratio)
            #     print(differences)
            #     sys.exit(1)
            #     if ratio < constants.NOTE_LOWER_BOUND:
            #         print(f"this case should not occur")
            #         sys.exit(1)

            #     j = j + 1
            #     i = 1
            #     ticks = ticks / (j + 1)
            #     ratio = ticks / ticks_per_beat
            #     continue
            
            # candidate = candidates[0]
            # ticks     = ticks_per_beat * ((bounds[candidate][0] + bounds[candidate][1]) / 2)

            # old_ratio = ratio
            # ratio     = ticks / ticks_per_beat
            
            # i = 1
            # j = 0

            # if __debug__:
            #     print(f"adapt tick-ratio old_ratio={old_ratio} new_ratio={ratio} new_ticks={ticks}")


def get_note_type(ticks, ticks_per_beat):
    return _get_note_type(ticks, ticks_per_beat, constants.NOTE_TYPES)

def get_note_type_pause(ticks, ticks_per_beat):
    note_types = constants.NOTE_TYPES.copy()

    del note_types[f"double dotted {constants.NOTE_WHOLE}"]
    del note_types[f"dotted {constants.NOTE_WHOLE}"]
    
    return _get_note_type(ticks, ticks_per_beat, note_types)

def get_key(note):
    notes   = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
    name    = notes[note % 12]

    # int implicitely floors the value
    octave  = int(note / 12) - 1
    return f"{name}{octave}"

def get_time_signature_ticks(time_signature, ticks_per_beat, measures):
    numerator   = time_signature.numerator
    denominator = time_signature.denominator

    if not denominator in constants.SIGNATURE_UNIT.keys():
        print(f"invalid denominator / signature: {time_signature}")
        sys.exit(1)

    unit        = constants.SIGNATURE_UNIT[denominator]
    ratio_lower = constants.NOTE_TYPES[unit][0]

    return ticks_per_beat * ratio_lower * numerator * measures

def get_default_time_signature_ticks(ticks_per_beat, measures):
    meta = mido.MetaMessage("time_signature", numerator=4, denominator=4)
    return get_time_signature_ticks(meta, ticks_per_beat, measures)
