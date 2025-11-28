from typing import Dict, Union, List


def get_recognized_segments(
        operator_segments: list[dict[str, str | float]],
        caller_segments: list[dict[str, str | float]],
        all_speakers_segments: list[dict[str, str | float]]
) -> Dict[str, Union[str | List[dict[str, str | float]]]]:
    all_speakers_first_segm_speaker = all_speakers_segments[0]["speaker"]

    operator_first_start = operator_segments[0]["start"]
    caller_first_start = caller_segments[0]["start"]
    operator_is_first_flag = operator_first_start < caller_first_start
    if operator_is_first_flag:
        speech_started = "operator"
        print(f"Operator started dialog:\n"
              f"operator_is_first_flag: {operator_is_first_flag}\n"
              f"speech_started: {speech_started}\n")
    else:
        speech_started = "caller"
        print(f"Caller started dialog:\n"
              f"operator_is_first_flag: {operator_is_first_flag}\n"
              f"speech_started: {speech_started}\n")

    association_dict = {}
    if all_speakers_first_segm_speaker == "SPEAKER_01":
        if operator_is_first_flag:
            association_dict = {"SPEAKER_01": "operator",
                                "SPEAKER_00": "caller"}
        else:
            association_dict = {"SPEAKER_01": "caller",
                                "SPEAKER_00": "operator"}
    elif all_speakers_first_segm_speaker == "SPEAKER_00":
        if operator_is_first_flag:
            association_dict = {"SPEAKER_00": "operator",
                                "SPEAKER_01": "caller"}
        else:
            association_dict = {"SPEAKER_00": "caller",
                                "SPEAKER_01": "operator"}

    recognised_segments = []
    for cur_num, cur_segment in enumerate(all_speakers_segments):
        cur_speaker = cur_segment["speaker"]
        cur_speaker_label = association_dict.get(cur_speaker, cur_speaker)

        cur_segment_start = cur_segment["start"]
        cur_segment_end = cur_segment["end"]

        cur_recognized_segment = {"speaker": cur_speaker_label,
                                  "start": cur_segment_start,
                                  "end": cur_segment_end}
        recognised_segments.append(cur_recognized_segment)
        # print(f"{cur_num}\t {cur_speaker_label}:\t "
        #       f"{cur_segment_start}\t - {cur_segment_end}")
    recognized_data = {"recognized_diary": recognised_segments,
                       "first_speaker": speech_started}
    return recognized_data
