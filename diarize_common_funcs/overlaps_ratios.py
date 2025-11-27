def calc_overlaps_ratios(
        speakers_durations: dict[str, float | int],
        overlaps_durations: dict[str, float | int]):
    oper_duration = speakers_durations["operator"]
    caller_duration = speakers_durations["caller"]
    other_duration = speakers_durations["others"]
    oper_caller_overlap = overlaps_durations["operator_caller"]
    oper_others_overlap = overlaps_durations["operator_others"]
    oper_caller_others_overlap = overlaps_durations["operator_caller_others"]

    oper_caller_overlap_ratio = (
            oper_caller_overlap / (oper_duration + caller_duration) * 100)

    oper_others_overlap_ratio = (
            oper_others_overlap / (oper_duration + other_duration) * 100)

    all_speakers_duration = oper_duration + caller_duration + other_duration
    oper_caller_others_overlap_ratio = (
            oper_caller_others_overlap / all_speakers_duration * 100)

    overlaps_ratios = {
        "operator_caller": round(oper_caller_overlap_ratio, 2),
        "operator_others": round(oper_others_overlap_ratio, 2),
        "operator_caller_others": round(oper_caller_others_overlap_ratio, 2)}
    return overlaps_ratios
