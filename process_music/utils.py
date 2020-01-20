import mido
import constants

import numpy as np

import sys

def order_note_types(note_types, ticks, ticks_per_beat, threshold):
    note_types_ordered = []

    while len(note_types) > 0:
        target = None

        # assume the note_types are ordered. therefore, for all note_types fulfilling the condition and
        # exceeding the current measure, take the smallest one
        for i, note_type in enumerate(note_types):
            time = ticks_per_beat * (constants.NOTE_TYPES[note_type][0] + constants.NOTE_TYPES[note_type][1]) / 2
            
            if threshold <= (ticks + time):
                target = (i, note_type, time) 

        if target is not None:
            # append found target note and remove it from the set
            # additionally, adapt ticks by measure threshold
            note_types_ordered.append(target[1])

            ticks      = (ticks + target[2]) % threshold
            note_types = note_types[0:target[0]] + note_types[target[0]+1:]
        else:
            # when no target is found is means there is no note exceeding the measure by its own
            # this doesn't exclude a combination of such single note. therefore, take only the first
            # note - same assumption as above - remove it from the set and repeat the cycle
            first = note_types[0]
            note_types_ordered.append(first)
            
            time  = ticks_per_beat * (constants.NOTE_TYPES[first][0] + constants.NOTE_TYPES[first][1]) / 2
            ticks = ticks + time

            note_types = note_types[1:]

    return note_types_ordered

def _adapt_ratio(ratio, ticks, ticks_per_beat, note_types):
    bounds    = list(note_types.values())
    old_ticks = ticks
    old_ratio = ratio 

    middles = []
    for bound in bounds:
        middle = (bound[0] + bound[1]) / 2
        if middle * 0.9 <= ratio <= middle * 1.1:
            middles.append(middle)

    if len(middles) > 0:
        minimum_difference = np.argmin(np.abs(np.array(middles) - ratio))
        ticks              = ticks_per_beat * middles[minimum_difference]
        ratio              = ticks / ticks_per_beat

        if __debug__:
            print(f"adapt tick-ratio [old, new] \t tracks [{old_ratio}, {ratio}] \t ticks [{old_ticks}, {ticks}]")

    return ratio

def _get_note_type_pause(ticks, ticks_per_beat, note_types):
    ratio = ticks / ticks_per_beat
    if ratio < constants.NOTE_LOWER_BOUND:
        return ["unknown"]

    if ratio > np.max(list(note_types.values())):
        typez = []

        while True:
            if ratio < constants.NOTE_LOWER_BOUND:
                break

            for key, bound in note_types.items():
                if "dotted" in key:
                    continue

                middle = bound[0]
                if (ratio - middle) >= 0:
                    ratio = ratio - middle
                    typez.append(key)
                    break

        return typez

    adapted_ratio = _adapt_ratio(ratio, ticks, ticks_per_beat, note_types)
    typez = [*filter(lambda x: note_types[x][0] < adapted_ratio <= note_types[x][1], note_types.keys())]
    if len(typez) > 0:
        return [typez[0]]

    print(f"could not determine note type for ticks - ratio: {ticks} - {ratio}")

    # i = 1
    # adapted = False
    # while True:
    #     adapted_ratio = ratio / i
    #     typez = [*filter(lambda x: note_types[x][0] < adapted_ratio <= note_types[x][1], note_types.keys())]
    #     if len(typez) > 0:
    #         return (i, typez[0])

    #     i = i + 1

    #     # adjust tick ratio 
    #     if i > constants.MAX_ATTEMPTS_ADAPTATION:
    #         if adapted == True:
    #             print(f"could not adapt ratio correctly for ratio {ratio}")
    #             sys.exit(1)

    #         ratio   = _adapt_ratio(ratio, ticks, ticks_per_beat, note_types)
    #         adapted = True
    #         i       = 1
    #         continue

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
                print(f"could not adapt ratio correctly for ratio {ratio}")
                sys.exit(1)

            bounds    = list(note_types.values())
            old_ticks = ticks
            old_ratio = ratio 

            middles = []
            for bound in bounds:
                middle = (bound[0] + bound[1]) / 2
                if middle * 0.9 <= ratio <= middle * 1.1:
                    middles.append(middle)
            if len(middles) > 0:
                minimum_difference = np.argmin(np.abs(np.array(middles) - ratio))
                ticks              = ticks_per_beat * middles[minimum_difference]
                ratio              = ticks / ticks_per_beat

            if __debug__:
                print(f"adapt tick-ratio [old, new] \t tracks [{old_ratio}, {ratio}] \t ticks [{old_ticks}, {ticks}]")

            adapted = True
            i       = 1
            continue

def get_note_type(ticks, ticks_per_beat):
    return _get_note_type(ticks, ticks_per_beat, constants.NOTE_TYPES)

def get_note_type_pause(ticks, ticks_per_beat):
    note_types = constants.NOTE_TYPES.copy()

    del note_types[f"double dotted {constants.NOTE_WHOLE}"]
    del note_types[f"dotted {constants.NOTE_WHOLE}"]
    
    return _get_note_type_pause(ticks, ticks_per_beat, note_types)

def get_note_before(note):
    notes = np.array(constants.NOTES)
    
    search = np.where(notes == note)
    if len(search) == 0:
        return note

    index = search[0][0]
    index = max(0, index - 1)
    return notes[index]

def get_note_after(note):
    notes = np.array(constants.NOTES)
    
    search = np.where(notes == note)
    if len(search) == 0:
        return note

    index = search[0][0]
    index = min(len(notes) - 1, index + 1)
    return notes[index]

def get_key(note):
    # int implicitely floors the value
    name    = constants.PITCHES[note % 12]
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

def adapt_iso_time(now):
    # small bug in python: with zero microseconds, the identifier will not be printed resulting in an inconsistent
    # timestamp. solve by using the default value
    iso = now.isoformat()
    if "." not in iso:
        iso = f"{iso}.000000"
    return iso
