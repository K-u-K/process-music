import mido
import constants

def get_note_type(ticks, ticks_per_beat):
    ratio = ticks / ticks_per_beat
    if ratio < constants.NOTE_LOWER_BOUND:
        return "unknown"

    i = 1
    while True:
        adapted_ratio = ratio / i
        typez = [*filter(lambda x: constants.NOTE_TYPES[x][0] < adapted_ratio <= constants.NOTE_TYPES[x][1], constants.NOTE_TYPES.keys())]
        if len(typez) > 0:
            return (f"{i}-times " if i > 1 else "") + typez[0]

        i = i + 1

def get_key(note):
    note -= 21
    notes = ["A", "A#", "B", "C", "C#", "D", "D#", "E", "F", "F#", "G", "G#"]
    octave = int(note / 12) + 1
    name = notes[note % 12]
    return f"{name}{octave}"

def get_time_signature_ticks(time_signature, ticks_per_beat, measures):
    numerator   = time_signature.numerator
    denominator = time_signature.denominator

    if not denominator in constants.SIGNATURE_UNIT.keys():
        print(f"invalid denominator / signature: {time_signature}")
        sys.exit(1)

    unit                     = constants.SIGNATURE_UNIT[denominator]
    ratio_lower, ratio_upper = constants.NOTE_TYPES[unit]

    ticks_upper = ticks_per_beat * ratio_upper * numerator * measures
    ticks_lower = ticks_per_beat * ratio_lower * numerator * measures

    return [ticks_lower, ticks_upper]

def get_default_time_signature_ticks(ticks_per_beat, measures):
    meta = mido.MetaMessage("time_signature", numerator=4, denominator=4)
    return get_time_signature_ticks(meta, ticks_per_beat, measures)
