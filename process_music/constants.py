import numpy as np

NOTE_WHOLE                            = "whole note"
NOTE_HALF                             = "half note"
NOTE_QUARTER                          = "quater note"
NOTE_EIGHTH                           = "eighth note"
NOTE_SIXTEENTH                        = "sixteenth note"
NOTE_THIRTY_SECOND                    = "thirty-second note"
NOTE_SIXTY_FOURTH                     = "sixty-fourth note"
NOTE_A_HUNDRED_AND_TWENTY_EIGHTH_NOTE = "a hundred and twenty-eighth note"

SIGNATURE_UNIT = {
    1:   NOTE_WHOLE
    2:   NOTE_HALF,
    4:   NOTE_QUARTER,
    8:   NOTE_EIGHTH,
    16:  NOTE_SIXTEENTH,
    32:  NOTE_THIRTY_SECOND,
    64:  NOTE_SIXTY_FOURTH,
    128: NOTE_A_HUNDRED_AND_TWENTY_EIGHTH_NOTE
}

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

# base ratio between MIDI's ticks_per_beat (in quarter notes) and a whole note
BASE_RATIO = 4.0

# deviation is for things like MuseScore's strange tick numbering
DEVIATION  = 0.025
BASE       = np.array([BASE_RATIO - DEVIATION, BASE_RATIO + DEVIATION])

# calculate all ratios and include dotted + double dotted type notes
NOTE_TYPES = {}
for i, note in enumerate(NOTES):
    bounds = (BASE * (0.5 ** i))

    NOTE_TYPES[f"double dotted {note}"] = bounds * 1.75
    NOTE_TYPES[f"dotted {note}"]        = bounds * 1.5
    NOTE_TYPES[f"{note}"]               = bounds
    
NOTE_LOWER_BOUND = np.min(list(NOTE_TYPES.values()))