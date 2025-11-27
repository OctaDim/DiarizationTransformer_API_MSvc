def calc_silence_data(
        total_dur_with_silence: float | int,
        all_speakers_dur: float | int,
        all_overlaps_dur: float | int,
):
    all_speakers_no_overlaps_dur = all_speakers_dur - all_overlaps_dur
    total_silence_dur = total_dur_with_silence - all_speakers_no_overlaps_dur

    silence_ratio = 0.0
    if all_speakers_no_overlaps_dur:
        silence_ratio = (total_silence_dur / all_speakers_no_overlaps_dur) * 100

    silence_data = {
        "all_speakers_no_overlaps_dur": all_speakers_no_overlaps_dur,
        "total_silence_dur": total_silence_dur,
        "silence_ratio": round(silence_ratio, 1)}
    return silence_data
