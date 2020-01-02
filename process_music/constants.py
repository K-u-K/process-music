import numpy as np

NOTE_UPPER_BOUND = 6.0
NOTE_LOWER_BOUND = 0.045703125

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

NOTE_TYPES = {}

BASE = np.array([3.9, 4.1])
NOTE_TYPES[f"double dotted whole note"]  = (BASE * 1.75).tolist()
NOTE_TYPES[f"dotted whole note"]         = (BASE * 1.5).tolist()

for i, note in enumerate(NOTES):
    bounds = (BASE * (0.5 ** i))
    if (i + 1) == len(NOTES):
        break

    NOTE_TYPES[f"{note}"]                      = bounds.tolist()
    NOTE_TYPES[f"double dotted {NOTES[i+1]}"]  = (bounds * 0.875).tolist()
    NOTE_TYPES[f"dotted {NOTES[i+1]}"]         = (bounds * 0.75).tolist()

SIGNATURE_UNIT = {
    2: "half note",
    4: "quarter note",
    8: "eighth note",
    16: "sixteenth note",
    32: "thirty-second note",
    64: "sixty-fourth note",
    128: "a hundred and twenty-eighth note"
}