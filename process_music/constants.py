import numpy as np

SIGNATURE_UNIT = {
    2: "half note",
    4: "quarter note",
    8: "eighth note",
    16: "sixteenth note",
    32: "thirty-second note",
    64: "sixty-fourth note",
    128: "a hundred and twenty-eighth note"
}

NOTES = [
    "whole note",
    "half note",
    "quarter note",
    "eighth note",
    "sixteenth note",
    "thirty-second note",
    "sixty-fourth note",
    "a hundred and twenty-eighth note"
]

BASE_RATIO = 4.0
DEVIATION  = 0.1
BASE       = np.array([BASE_RATIO - DEVIATION, BASE_RATIO + DEVIATION])

NOTE_TYPES = {}
NOTE_TYPES[f"double dotted whole note"]  = BASE * 1.75
NOTE_TYPES[f"dotted whole note"]         = BASE * 1.5

for i, note in enumerate(NOTES):
    bounds                = (BASE * (0.5 ** i))
    NOTE_TYPES[f"{note}"] = bounds
    if (i + 1) == len(NOTES):
        break

    NOTE_TYPES[f"double dotted {NOTES[i+1]}"]  = bounds * 0.875
    NOTE_TYPES[f"dotted {NOTES[i+1]}"]         = bounds * 0.75

NOTE_LOWER_BOUND = np.min(list(NOTE_TYPES.values()))