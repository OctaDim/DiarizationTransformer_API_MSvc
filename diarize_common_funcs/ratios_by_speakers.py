def calc_ratios_by_speakers(
        durations_by_speakers: dict[str, float | int]
) -> dict[str, float | int]:
    operator_duration = durations_by_speakers["operator"]
    caller_duration = durations_by_speakers["caller"]
    others_duration = durations_by_speakers["others"]
    total_duration = durations_by_speakers["total_without_silence_dur"]

    if total_duration:
        speakers_rates = {
            "operator": round(operator_duration / total_duration * 100, 1),
            "caller": round(caller_duration / total_duration * 100, 1),
            "others": round(others_duration / total_duration * 100, 1),
            "total": 100.0}
    else:
        speakers_rates = {
            "operator": 0.0,
            "caller": 0.0,
            "others": 0.0,
            "total": 0.0}
    return speakers_rates
