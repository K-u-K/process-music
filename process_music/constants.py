import numpy as np

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
    NOTE_THIRTY_SECOND,
    NOTE_SIXTY_FOURTH,
    NOTE_A_HUNDRED_AND_TWENTY_EIGHTH_NOTE
]

def calculate_ratios(base_ratio, deviation, notes):
    note_types = {}
    base       = np.array([base_ratio - deviation, base_ratio + deviation])

    for i, note in enumerate(notes):
        bounds = (base * (0.5 ** i))

        note_types[f"double dotted {note}"] = bounds * 1.75
        note_types[f"dotted {note}"]        = bounds * 1.5
        note_types[f"{note}"]               = bounds

    return note_types

def calculate_signature_denominators(base_ratio, notes):
    return {(base_ratio / (base_ratio * 0.5 ** i)): note for i, note in enumerate(notes)}

# base ratio between MIDI's ticks_per_beat (in quarter notes) and a whole note
# deviation is for things like MuseScore's strange tick numbering
BASE_RATIO = 4.0
DEVIATION  = 0.025

# calculate all ratios and include dotted + double dotted type notes
NOTE_TYPES       = calculate_ratios(BASE_RATIO, DEVIATION, NOTES)
NOTE_LOWER_BOUND = np.min(list(NOTE_TYPES.values()))

# calculate time signature lookup
SIGNATURE_UNIT = calculate_signature_denominators(BASE_RATIO, NOTES)