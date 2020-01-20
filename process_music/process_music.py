#!/usr/bin/env python3

"""Process Music. Explorative analysis of songs and music from the perspective of a log file

Usage:
    process_music.py [--measures MEASURES] [--output_dir OUTPUT_DIR] [--tracks TRACKS...] MIDI_FILE
    process_music.py (-h | --help)
    process_music.py (-v | --version)

Options:
    -h --help               Show help.
    -v --version            Show version information.
    --measures MEASURES     The number of measures you want to define for a case. Zero defines everything as trace / case [default: 1].
    --output_dir OUTPUT_DIR The output directory where the final XES logs of each track are stored [default: pm_tracks].
    --tracks TRACKS....     Which tracks to consider. Multiple values possible. A negative value of -1 takes all [default: -1]

Copyright:
    (c) by K-u-K (imperial Keller Patrick & royal Kocaj Alen) 2020
"""
from docopt import docopt
from schema import Schema, And, Use, Or, SchemaError
import mido

import constants
import footprint
import utils
import xes

import os
import sys
import datetime

# TODO: code documentation
# TODO: create man page <3
# TODO: chord & interval names instead of an own entry for each note in a chord
# TODO: consider special rhythm structures, quintuplets, septuplets, etc.
# TODO: make timestamp column more accurate
# TODO: make calculation of note_type more precise and powerful
# TODO: 
# TODO: put fixed strings into constants + refactor code (a lot). Convert to Class instead of main py
# TODO: fill up missing chords with pauses in other tracks
# TODO: consider notes whose duration spans more than one measure (whole note starting at 2/4 to 2/4 of new measure)
#       how should it be implemented in the log 

def main(args):
    filename    = args["MIDI_FILE"]
    measures    = args["--measures"]
    output_dir  = args["--output_dir"]
    tracks      = args["--tracks"]

    if output_dir is None:
        output_dir = os.path.splitext(filename)[0].lower()

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    mid = mido.MidiFile(filename, clip=True)
    if tracks[0] == -1:
        tracks = [*range(len(mid.tracks))]

    if max(tracks) >= len(mid.tracks):
        print("Highest tracks does not exist in MIDI file")
        sys.exit(1) 

    if measures == 0:
        measures = sys.maxsize

    for i in tracks:
        track = mid.tracks[i]
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

        # define start datetime, assume default tempo is 500000us
        now   = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        tempo = 500000

        # assume default time signature is 4/4
        # threshold defines the number of ticks for each case
        threshold = utils.get_default_time_signature_ticks(mid.ticks_per_beat, measures)

        # analyse meta tracks in terms of time_signature / set_tempo
        if all([msg.is_meta or msg.type not in constants.NOTE_EVENTS for msg in track]):
            time_signatures = [*filter(lambda msg: msg.type == constants.META_TIME_SIGNATUR, track)]
            set_tempos      = [*filter(lambda msg: msg.type == constants.META_SET_TEMPO, track)]

            # multiple time_signatures and set_tempo events in a meta track are uncommon but technically possible (take the last ticks)
            for time_signature in time_signatures:
                threshold = utils.get_time_signature_ticks(time_signature, mid.ticks_per_beat, measures)
            for set_tempo in set_tempos:
                tempo = set_tempo.tempo

            continue

        # process main tracks
        for msg in track:
            if msg.type == constants.META_TIME_SIGNATUR:
                threshold = utils.get_time_signature_ticks(msg, mid.ticks_per_beat, measures)

            if msg.type == constants.META_SET_TEMPO:
                tempo = msg.tempo

            if msg.type not in constants.NOTE_EVENTS:
                continue

            if __debug__:
                print(f"Message type={msg.type} note={utils.get_key(msg.note)} ({msg.note}) velocity={msg.velocity} time={msg.time}")

            # prepend pauses
            if msg.type == constants.NOTE_ON and msg.time != 0 and msg.velocity != 0:
                note_types = utils.get_note_type_pause(msg.time, mid.ticks_per_beat)
                
                # ignore invalid pauses (MuseScore defines strange note_on message with sufficiently low ticks) 
                if constants.UNKNOWN_NOTE_TYPE not in note_types:
                    for note_type in note_types:
                        msg.time = mid.ticks_per_beat * (constants.NOTE_TYPES[note_type][0] + constants.NOTE_TYPES[note_type][1]) / 2 
                            
                        for _ in range(times):
                            if len(results) > 0:                        
                                now = now + datetime.timedelta(microseconds=int(1e6 * mido.tick2second(msg.time, mid.ticks_per_beat, tempo)))

                            results.append({
                                "case":     case_number,
                                "key":      "Pause",
                                "type":     note_type,
                                "order":    order,
                                "is_chord": False,
                                "time":     utils.adapt_iso_time(now)
                            })
                            order = order + 1
                            ticks = ticks + msg.time
                            if threshold <= ticks:
                                case_number = case_number + 1
                                ticks       = ticks % threshold

                    msg.time = 0    

            # if summed up ticks reach the threshold increment case number
            # => e.g. if one bar is the timespan for a case increase case number after each bar
            ticks = ticks + msg.time
            if threshold <= ticks:
                case_number = case_number + 1
                ticks       = ticks % threshold

            if msg.velocity == 0 or msg.type == constants.NOTE_OFF:
                key         = utils.get_key(msg.note)
                time        = msg.time
                update_now  = False

                if state[key]["is_chord"]:
                    if time == 0:
                        time = chord["msg"].time
                    else: 
                        chord = {
                            "key": key,
                            "msg": msg
                        }
                        update_now = True
                else:
                    if time == 0:
                        time = prev_note_off["msg"].time
                    else:
                        update_now = True
                
                times, note_type   = utils.get_note_type(time, mid.ticks_per_beat)
                state[key]["type"] = (f"{times} " if times > 1 else "") + note_type

                if update_now and len(results) > 0 and note_type != constants.UNKNOWN_NOTE_TYPE:
                    t   = mid.ticks_per_beat * times * ((constants.NOTE_TYPES[note_type][0] + constants.NOTE_TYPES[note_type][1]) / 2)
                    now = now + datetime.timedelta(microseconds=int(1e6 * mido.tick2second(t, mid.ticks_per_beat, tempo)))

                state[key]["time"] = utils.adapt_iso_time(now) 
                results.append(state[key])

                prev_note_on  = default()
                prev_note_off = {
                    "key": key,
                    "msg": msg
                }

                del state[key]
                continue

            is_chord = False
            if prev_note_on["msg"] is not None and prev_note_on["msg"].type == constants.NOTE_ON and msg.time == 0 and not is_first:
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
                "time":     ""
            }

            prev_note_on = {
                "key": key,
                "msg": msg
            }
            order    = order + 1
            is_first = False

        output = f"{output_dir}/track_{i}.csv"
        with open(output, "w") as fh:
            fh.write("Case_ID;Event;Type;Order;Is_Chord;Timestamp\n")
            for result in results:
                fh.write("{};{};{};{};{};{}\n".format(
                    result["case"],
                    result["key"],
                    result["type"],
                    result["order"],
                    result["is_chord"],
                    result["time"]
                ))
        
        # export to XES
        xes.export_to_xes(output)

        # generate and store footprint matrix
        footprint_matrix = footprint.calculate_footprint_matrix(output)
        footprint_path   = f"{output_dir}/track_{i}_footprint_matrix.txt"
        with open(footprint_path, "w") as fh:
            fh.write(footprint_matrix.to_string())

        if __debug__:
            print(footprint_matrix)

    print(f"Midi file '{filename}' processed. Track logfiles and event streams generated in directory '{output_dir}'")

if __name__ == '__main__':
    args   = docopt(__doc__, version="0.2.0")
    schema = Schema({
        "MIDI_FILE":  And(os.path.exists, error="MIDI_FILE should exist"),
        "--measures": And(Use(int), lambda x: int(x) >= 0 , error="Measure should be a positive non-zero number"),
        "--tracks": And(Use(
            lambda x: [*map(lambda a: int(a), x)]), 
            lambda x: (len(x) == 1 and -1 in x) or (sum(x) >= -1 and -1 not in x), 
            error="Tracks to examine should be a list of positive numbers or all by using -1"),
        "--output_dir": Or(None, str),
        "--version": bool,
        "--help": bool
    })

    try:
        args = schema.validate(args)
    except SchemaError as e:
        print("Warning: invalid arguments given", e, "\n")
        print(__doc__)
        sys.exit(1)

    main(args)