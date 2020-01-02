#!/usr/bin/env python3

import os
import sys

import mido
from mido import MidiFile

import utils
import xes

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
        if __debug__:
            print(f"Processing track {i} '{track.name}'")

        state   = {}
        results = []

        default = lambda: {"key": "", "msg": None}

        # prev_note_on keeps track is important when a given note_on event is part of a chord
        prev_note_on  = default()

        # prev_note_off keeps track is important when a given note_off event has a time of zero
        #               indicating that a different note_off event happened between the note_on & note_off event
        #               of the actual note
        prev_note_off = default()
        chord         = default()

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
            if msg.type == "time_signature":
                ticks_lower, ticks_upper = utils.get_time_signature_ticks(msg, mid.ticks_per_beat, measures)

            if msg.type not in ['note_on', 'note_off']:
                continue

            if __debug__:
                print(msg)

            # prepend pauses
            if msg.type == "note_on" and msg.time != 0 and msg.velocity != 0:
                note_type = utils.get_note_type(msg.time, mid.ticks_per_beat)
                
                # ignore invalid pauses (MuseScore defines strange note_on message with sufficiently low ticks) 
                if note_type != "unknown":        
                    results.append({
                        "case":     case_number,
                        "key":      "Pause",
                        "type":     note_type,
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
                else:
                    if time == 0:
                        time = prev_note_off["msg"].time
                
                state[key]["type"] = utils.get_note_type(time, mid.ticks_per_beat)
                results.append(state[key])

                prev_note_on  = default()
                prev_note_off = {
                    "key": key,
                    "msg": msg
                }

                del state[key]
                continue

            is_chord = False
            if prev_note_on["msg"] is not None and prev_note_on["msg"].type == "note_on" and msg.time == 0 and not is_first:
                is_chord = True
                state[prev_note_on["key"]]["is_chord"] = True
                order = order - 1

            key = utils.get_key(msg.note)
            state[key] = {
                "case":     case_number,
                "key":      key,
                "type":     "",
                "order":    order,
                "is_chord": is_chord,
            }

            prev_note_on = {
                "key": key,
                "msg": msg
            }
            order    = order + 1
            is_first = False

        output = f"{output_dir}/track_{i}.csv"
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
        
        # export to XES
        xes.export_to_xes(output)

    print(f"Midi file '{filename}' processed. Track logfiles and event streams generated in directory '{output_dir}'")