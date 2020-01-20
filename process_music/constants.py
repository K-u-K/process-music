import numpy as np

UNKNOWN_NOTE_TYPE = "unknown"

NOTE_WHOLE                            = "whole note"
NOTE_HALF                             = "half note"
NOTE_QUARTER                          = "quarter note"
NOTE_EIGHTH                           = "eighth note"
NOTE_SIXTEENTH                        = "sixteenth note"
NOTE_THIRTY_SECOND                    = "thirty-second note"
NOTE_SIXTY_FOURTH                     = "sixty-fourth note"
NOTE_A_HUNDRED_AND_TWENTY_EIGHTH_NOTE = "a hundred and twenty-eighth note"

NOTES = [
    NOTE_WHOLE,
    NOTE_HALF,
    NOTE_QUARTER,
    NOTE_EIGHTH,
    NOTE_SIXTEENTH,
    NOTE_THIRTY_SECOND
]

PITCH_C         = "C"
PITCH_C_SHARP   = "C#"
PITCH_D_FLAT    = "Db"
PITCH_D         = "D"
PITCH_D_SHARP   = "D#"
PITCH_E_FLAT    = "Eb"
PITCH_E         = "E"
PITCH_F_FLAT    = "Fb"
PITCH_F         = "F"
PITCH_F_SHARP   = "F#"
PITCH_G_FLAT    = "Gb"
PITCH_G         = "G"
PITCH_G_SHARP   = "G#"
PITCH_A_FLAT    = "Ab"
PITCH_A         = "A"
PITCH_A_SHARP   = "A#"
PITCH_B_FLAT    = "Bb"
PITCH_B         = "B"

PITCHES = [
    PITCH_C,
    PITCH_C_SHARP,
    PITCH_D,
    PITCH_D_SHARP,
    PITCH_E,
    PITCH_F,
    PITCH_F_SHARP,
    PITCH_G,
    PITCH_G_SHARP,
    PITCH_A,
    PITCH_A_SHARP,
    PITCH_B
]

NOTE_OFF = "note_off"
NOTE_ON  = "note_on"

NOTE_EVENTS = [
    NOTE_ON,
    NOTE_OFF
]

META_SET_TEMPO      = "set_tempo"
META_TIME_SIGNATUR  = "time_signature"

def calculate_ratios(base_ratio, deviation, notes):
    note_types = {}
    base       = np.array([base_ratio - deviation, base_ratio + deviation])

    for i, note in enumerate(notes):
        bounds = (base * (0.5 ** i))

        note_types[f"double dotted {note}"] = bounds * 1.75
        note_types[f"dotted {note}"]        = bounds * 1.5
        note_types[f"{note}"]               = bounds

        if note in [NOTE_HALF, NOTE_QUARTER, NOTE_EIGHTH, NOTE_SIXTEENTH]:
            prev_note = NOTES[i-1]

            note_types[f"triplet {note}"] = note_types[prev_note] * (1/3)
            # note_types[f"quintuplet {prev_note}"] = note_types[prev_note] * (1/5)
            # note_types[f"septuplets {prev_note}"] = note_types[prev_note] * (1/7)

    return note_types

def calculate_signature_denominators(base_ratio, notes):
    return {(base_ratio / (base_ratio * 0.5 ** i)): note for i, note in enumerate(notes)}

# base ratio between MIDI's ticks_per_beat (in quarter notes) and a whole note
# deviation is for things like MuseScore's strange tick numbering
BASE_RATIO = 4.0
DEVIATION  = 0.01

# calculate all ratios and include dotted + double dotted type notes
NOTE_TYPES       = calculate_ratios(BASE_RATIO, DEVIATION, NOTES)
NOTE_LOWER_BOUND = np.min(list(NOTE_TYPES.values()))
NOTE_UPPER_BOUND = np.max(list(NOTE_TYPES.values()))

# calculate time signature lookup
SIGNATURE_UNIT = calculate_signature_denominators(BASE_RATIO, NOTES)

MAX_ATTEMPTS_ADAPTATION = 100 