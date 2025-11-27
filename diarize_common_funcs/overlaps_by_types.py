def calc_overlaps_by_types(
        recognised_segments: list[dict[str, str | float]]
) -> dict[str, float | int]:
    sweep_line_events = []
    for cur_segment in recognised_segments:
        cur_speaker = cur_segment["speaker"]
        sweep_line_events.append((cur_segment["start"], "start", cur_speaker))
        sweep_line_events.append((cur_segment["end"], "end", cur_speaker))

    sweep_line_events.sort(key=lambda segm_time: segm_time[0])

    active_speakers = set()
    previous_event_time = 0.0
    operator_caller_overlap = 0.0
    operator_others_overlap = 0.0
    operator_caller_others_overlap = 0.0

    for cur_event_time, cur_event_type, cur_event_speaker in sweep_line_events:
        if active_speakers and cur_event_time > previous_event_time:
            time_segment = cur_event_time - previous_event_time
            has_operator_flag = "operator" in active_speakers
            has_caller_flag = "caller" in active_speakers
            has_others_flag = "others" in active_speakers
            has_caller_others_flag = any([has_caller_flag, has_others_flag])

            if has_operator_flag and has_caller_flag:
                operator_caller_overlap += time_segment

            if has_operator_flag and has_others_flag:
                operator_others_overlap += time_segment

            if has_operator_flag and has_caller_others_flag:
                operator_caller_others_overlap += time_segment

        if cur_event_type == "start":
            active_speakers.add(cur_event_speaker)
        else:
            active_speakers.discard(cur_event_speaker)
        previous_event_time = cur_event_time

    overlaps_by_types = {
        "operator_caller": round(operator_caller_overlap, 1),
        "operator_others": round(operator_others_overlap, 1),
        "operator_caller_others": round(operator_caller_others_overlap, 1)}
    return overlaps_by_types
