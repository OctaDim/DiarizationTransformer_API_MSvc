def count_interruptions_by_types(
        recognised_segments: list[dict[str, str | float]]
) -> dict[str, int]:
    sorted_segments = sorted(recognised_segments, key=lambda sgm: sgm["start"])
    operator_segments = []
    caller_segments = []
    others_segments = []
    for cur_segment in sorted_segments:
        cur_speaker = cur_segment["speaker"]
        if cur_speaker == "operator":
            operator_segments.append(cur_segment)
        elif cur_speaker == "caller":
            caller_segments.append(cur_segment)
        else:
            others_segments.append(cur_segment)

    caller_interrupts_operator = 0
    operator_interrupts_caller = 0
    others_interrupts_operator = 0
    operator_interrupts_others = 0

    for cur_operator_segment in operator_segments:
        cur_operator_start = cur_operator_segment["start"]
        cur_operator_end = cur_operator_segment["end"]

        for cur_caller_segment in caller_segments:
            cur_caller_start = cur_caller_segment["start"]
            cur_caller_end = cur_caller_segment["end"]
            if (cur_caller_start > cur_operator_end
                    or cur_caller_end < cur_operator_start):
                continue
            if cur_operator_start <= cur_caller_start <= cur_operator_end:
                caller_interrupts_operator += 1

        for cur_others_segment in others_segments:
            cur_others_start = cur_others_segment["start"]
            cur_others_end = cur_others_segment["end"]
            if (cur_others_start > cur_operator_end
                    or cur_others_end < cur_operator_start):
                continue
            if cur_operator_start <= cur_others_start <= cur_operator_end:
                others_interrupts_operator += 1

    for cur_caller_segment in caller_segments:
        cur_caller_start = cur_caller_segment["start"]
        cur_caller_end = cur_caller_segment["end"]

        for cur_operator_segment in operator_segments:
            cur_operator_start = cur_operator_segment["start"]
            cur_operator_end = cur_operator_segment["end"]
            if (cur_operator_start > cur_caller_end
                    or cur_operator_end < cur_caller_start):
                continue
            if cur_caller_start < cur_operator_start < cur_caller_end:
                operator_interrupts_caller += 1

    for cur_others_segment in others_segments:
        cur_others_start = cur_others_segment["start"]
        cur_others_end = cur_others_segment["end"]

        for cur_operator_segment in operator_segments:
            cur_operator_start = cur_operator_segment["start"]
            cur_operator_end = cur_operator_segment["end"]
            if (cur_operator_start > cur_others_end
                    or cur_operator_end < cur_others_start):
                continue
            if cur_others_start < cur_operator_start < cur_others_end:
                operator_interrupts_others += 1
    interrupts_by_types = {
        "operator_by_caller": caller_interrupts_operator,
        "caller_by_operator": operator_interrupts_caller,
        "operator_by_others": others_interrupts_operator,
        "others_by_operator": operator_interrupts_others}
    return interrupts_by_types
