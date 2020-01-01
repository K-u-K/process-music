#!/usr/bin/env python3

import os
import sys

import mido
from mido import MidiFile

# TODO: add double dotted notes
# TODO: consider rests as own entries
# TODO: search for further bugs
# TODO: code documentation
# TODO: multiple tracks foo
# TODO: measure not properly defined

NOTE_UPPER_BOUND = 6.0
NOTE_LOWER_BOUND = 0.015625

NOTE_TYPES = {
    "dotted whole note":                        [4.0, 6.0],
    "whole note":                               [3.5, 4.0],
    "dotted half note":                         [2.0, 3.5],
    "half note":                                [1.5, 2.0],
    "dotted quarter note":                      [1.0, 1.5],
    "quarter note":                             [0.75, 1.0],
    "dotted eighth note":                       [0.5, 0.75],
    "eighth note":                              [0.375, 0.5],
    "dotted sixteenth note":                    [0.25, 0.375],
    "sixteenth note":                           [0.1875, 0.25],
    "dotted thirty-second note":                [0.125, 0.1875],
    "thirty-second note":                       [0.09375, 0.125],
    "dotted sixty-fourth note":                 [0.0625, 0.09375],
    "sixty-fourth note":                        [0.046875, 0.0625],
    "dotted a hundred and twenty-eights note":  [0.03125, 0.046875],
    "a hundred and twenty-eighth note":         [0.015625, 0.03125]
}

SIGNATURE_UNIT = {
    2: "half note",
    4: "quarter note",
    8: "eighth note",
    16: "sixteenth note",
    32: "thirty-second note",
    64: "sixty-fourth note",
    128: "a hundred and twenty-eighth note"
}

def get_note_type(ticks, ticks_per_beat):
    ratio = ticks / ticks_per_beat
    if ratio < NOTE_LOWER_BOUND:
        return "unknown"

    i = 1
    while True:
        adapted_ratio = ratio / i
        typez = [*filter(lambda x: NOTE_TYPES[x][0] < adapted_ratio <= NOTE_TYPES[x][1], NOTE_TYPES.keys())]
        if len(typez) > 0:
            return (f"{i}-times " if i > 1 else "") + typez[0]

        i = i + 1

def get_note_number(note):
    note -= 21
    notes = ["A", "A#", "B", "C", "C#", "D", "D#", "E", "F", "F#", "G", "G#"]
    octave = note / 12 + 1
    name = notes[note % 12]
    return f"{name}{str(int(octave))}"

if __name__ == '__main__':
    filename = sys.argv[1] if len(sys.argv) > 1 else ""
    measures = sys.argv[2] if len(sys.argv) > 2 else 1
    output   = sys.argv[3] if len(sys.argv) > 3 else "process_music.csv"

    if not os.path.exists(filename):
        print(f"file {filename} not found")
        sys.exit(1)
    
    mid = MidiFile(filename, clip=True)

    state   = {}
    results = []

    default = lambda: {"key": "", "msg": None}
    prev    = default()
    chord   = default()

    order       = 1
    case_number = 1
    is_first    = True

    time_signature = [*filter(lambda msg: msg.type == "time_signature", mid.tracks[0])]
    if len(time_signature) == 0:
        print(f"invalid midi file, not time signature message found")
        sys.exit(1)
    
    numerator   = time_signature[0].numerator
    denominator = time_signature[0].denominator

    if not denominator in SIGNATURE_UNIT.keys():
        print(f"invlaid denominator / signature {time_signature[0]}")
        sys.exit(1)

    unit                     = SIGNATURE_UNIT[denominator]
    ratio_lower, ratio_upper = NOTE_TYPES[unit]

    ticks_upper = mid.ticks_per_beat * ratio_upper * numerator * measures
    ticks_lower = mid.ticks_per_beat * ratio_lower * numerator * measures

    ticks = 0
    for msg in mid.tracks[0]:
        if msg.type not in ['note_on', 'note_off']:
            continue

        ticks = ticks + msg.time
        if ticks_lower <= ticks <= ticks_upper:
            case_number = case_number + 1
            ticks       = 0

        if msg.velocity == 0 or msg.type == 'note_off':
            key       = get_note_number(msg.note)
            note_type = get_note_type(msg.time, mid.ticks_per_beat)

            time = msg.time
            if state[key]["is_chord"]:
                if time == 0:
                    time = chord["msg"].time
                else: 
                    chord = {
                        "key": key,
                        "msg": msg
                    }
            
            state[key]["type"] = get_note_type(time, mid.ticks_per_beat)
            
            results.append(state[key])
            prev = default()
            del state[key]
            continue

        is_chord = False
        if prev["msg"] is not None and prev["msg"].type == "note_on" and msg.time == 0 and not is_first:
            is_chord = True
            state[prev["key"]]["is_chord"] = True
            order = order - 1

        key = get_note_number(msg.note)
        state[key] = {
            "case":     case_number,
            "key":      key,
            "type":     "",
            "order":    order,
            "is_chord": is_chord,
        }

        prev = {
            "key": key,
            "msg": msg
        }
        order    = order + 1
        is_first = False

    with open(output, "w") as fh:
        fh.write("Case_ID;Event;Type;Order;Is_Chord\n")
        for result in results:
            fh.write("{};{};{};{};{}\n".format(
                result["case"],
                result["key"],
                result["type"],
                result["order"],
                result["is_chord"]
            ))

    print(f"Logfile generated at {output}")