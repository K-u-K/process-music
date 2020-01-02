#!/usr/bin/env python3

import os
import sys

import mido
from mido import MidiFile

import utils

# TODO: add double dotted notes
# TODO: search for further bugs
# TODO: code documentation
# TODO: measure not properly defined

if __name__ == '__main__':
    filename   = sys.argv[1] if len(sys.argv) > 1 else ""
    measures   = sys.argv[2] if len(sys.argv) > 2 else 1
    output_dir = sys.argv[3] if len(sys.argv) > 3 else ""

    if not os.path.exists(filename):
        print(f"file '{filename}' not found")
        sys.exit(1)

    if output_dir == "":
        output_dir = os.path.splitext(filename)[0].lower()

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    mid = MidiFile(filename, clip=True)

    for i, track in enumerate(mid.tracks):
        state   = {}
        results = []

        default = lambda: {"key": "", "msg": None}
        prev    = default()
        chord   = default()

        order       = 1
        case_number = 1    
        ticks       = 0
        is_first    = True

        # assume default time signature is 4/4
        ticks_lower, ticks_upper = utils.get_default_time_signature_ticks(mid.ticks_per_beat, measures)

        # analyse meta tracks in terms of time_signature / set_tempo
        if all([msg.is_meta for msg in track]):
            time_signatures = [*filter(lambda msg: msg.type == "time_signature", track)]

            # multiple time_signatures are uncommon but technically possible (take the last ticks)
            for time_signature in time_signatures:
                 ticks_lower, ticks_upper = utils.get_time_signature_ticks(time_signature, mid.ticks_per_beat, measures)
                 
            continue

        # process main tracks
        for msg in track:
            if __debug__ == True:
                print(msg)

            if msg.type == "time_signature":
                ticks_lower, ticks_upper = utils.get_time_signature_ticks(msg, mid.ticks_per_beat, measures)

            if msg.type not in ['note_on', 'note_off']:
                continue

            # prepend pauses
            if msg.type == "note_on" and msg.time != 0 and msg.velocity != 0:
                results.append({
                    "case":     case_number,
                    "key":      "Pause",
                    "type":     utils.get_note_type(msg.time, mid.ticks_per_beat),
                    "order":    order,
                    "is_chord": False,
                })

            ticks = ticks + msg.time
            if ticks_lower <= ticks <= ticks_upper:
                case_number = case_number + 1
                ticks       = 0

            if msg.velocity == 0 or msg.type == 'note_off':
                key  = utils.get_key(msg.note)
                time = msg.time

                if state[key]["is_chord"]:
                    if time == 0:
                        time = chord["msg"].time
                    else: 
                        chord = {
                            "key": key,
                            "msg": msg
                        }
                
                state[key]["type"] = utils.get_note_type(time, mid.ticks_per_beat)
                
                results.append(state[key])
                prev = default()
                del state[key]
                continue

            is_chord = False
            if prev["msg"] is not None and prev["msg"].type == "note_on" and msg.time == 0 and not is_first:
                is_chord = True
                state[prev["key"]]["is_chord"] = True
                order = order - 1

            key = utils.get_key(msg.note)
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

        with open(f"{output_dir}/track_{i}.csv", "w") as fh:
            fh.write("Case_ID;Event;Type;Order;Is_Chord\n")
            for result in results:
                fh.write("{};{};{};{};{}\n".format(
                    result["case"],
                    result["key"],
                    result["type"],
                    result["order"],
                    result["is_chord"]
                ))

    print(f"Midi file '{filename}' processed. Track logfiles generated in directory '{output_dir}'")