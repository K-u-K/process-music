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