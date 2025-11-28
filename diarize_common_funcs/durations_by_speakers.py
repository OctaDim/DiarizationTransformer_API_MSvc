def calc_durations_by_speakers(
        recognized_segments: list[dict[str, str | float]]
) -> dict[str, float | int]:
    operator_duration = 0.0
    caller_duration = 0.0
    other_duration = 0.0
    total_without_silence_dur = 0.0
    total_with_silence_dur = 0.0

    for cur_segment in recognized_segments:
        cur_speaker = cur_segment["speaker"]
        cur_duration = cur_segment["end"] - cur_segment["start"]
        if cur_speaker == "operator":
            operator_duration += cur_duration
        elif cur_speaker == "caller":
            caller_duration += cur_duration
        else:
            other_duration += cur_duration
        total_without_silence_dur += cur_duration

        total_with_silence_dur = max(total_with_silence_dur, cur_segment["end"])
    speakers_durations = {
        "operator": round(operator_duration, 1),
        "caller": round(caller_duration, 1),
        "others": round(other_duration, 1),
        "total_without_silence_dur": round(total_without_silence_dur, 1),
        "total_with_silence_dur": round(total_with_silence_dur, 1)}
    return speakers_durations
