from yaml import full_load

from diarize_common_funcs.durations_by_speakers import (
    calc_durations_by_speakers)
from diarize_common_funcs.get_recognized_segments import (
    get_recognized_segments)
from diarize_common_funcs.interruptions_by_types import (
    count_interruptions_by_types)
from diarize_common_funcs.overlaps_by_types import (
    calc_overlaps_by_types)
from diarize_common_funcs.overlaps_ratios import (
    calc_overlaps_ratios)
from diarize_common_funcs.ratios_by_speakers import (
    calc_ratios_by_speakers)


async def calc_dialog_statistics(
        operator_diarization: str,
        caller_diarization: str,
        all_speakers_diarization: str
):
    full_dialog_report = ""

    recognised_data = get_recognized_segments(
        operator_segments=operator_diarization,
        caller_segments=caller_diarization,
        all_speakers_segments=all_speakers_diarization)
    recognised_diarization = recognised_data["recognized_diary"]
    first_speaker = recognised_data["first_speaker"]

    report_association = {"operator": "оператор",
                          "caller": "заявитель",
                          "others": "другие"}
    first_speaker_label = report_association.get(first_speaker, first_speaker)
    log_msg = (f"\nДневник разговора:\n"
               f"\tразговор начал: {first_speaker_label}\n"
               f"\tхронология (сек:cек):\n")
    full_dialog_report += log_msg
    print(log_msg[:-1])

    call_report = ""
    for cur_num, cur_segment in enumerate(recognised_diarization):
        cur_speaker = cur_segment["speaker"]
        cur_speaker_lbl = report_association.get(cur_speaker, cur_speaker)
        cur_segment_start = cur_segment["start"]
        cur_segment_end = cur_segment["end"]
        cur_log_msg = (f"\t{cur_num}\t {cur_speaker_lbl}:\t "
                       f"[{cur_segment_start} : {cur_segment_end}]\n")
        call_report += cur_log_msg
    print(call_report[:-1])
    full_dialog_report += call_report

    speakers_durations = calc_durations_by_speakers(
        recognized_segments=recognised_diarization)
    operator_duration = speakers_durations["operator"]
    caller_duration = speakers_durations["caller"]
    other_duration = speakers_durations["others"]
    total_without_silence_dur = speakers_durations["total_without_silence_dur"]
    total_with_silence_dur = speakers_durations["total_with_silence_dur"]

    call_ratios = calc_ratios_by_speakers(
        durations_by_speakers=speakers_durations)
    operator_ratio = call_ratios["operator"]
    caller_ratio = call_ratios["caller"]
    others_ratio = call_ratios["others"]
    total_ratio = call_ratios["total"]

    log_msg = (
        f"\nДлительность речи (сек, %):\n"
        f"\toператор: {operator_duration} ({operator_ratio}%)\n"
        f"\tзаявитель: {caller_duration} ({caller_ratio}%)\n"
        # f"\tдругие: {other_duration} ({others_ratio}%)\n"
        f"\tВсего без тишины: {total_without_silence_dur} ({total_ratio}%)\n"
        f"\tВсего c тишиной: {total_with_silence_dur}\n")

    full_dialog_report += log_msg
    print(log_msg)

    interruptions = count_interruptions_by_types(
        recognised_segments=recognised_diarization)
    caller_interrupts_operator = interruptions["operator_by_caller"]
    operator_interrupts_caller = interruptions["caller_by_operator"]
    others_interrupt_operator = interruptions["operator_by_others"]
    operator_interrupts_others = interruptions["others_by_operator"]

    log_msg = (
        f"\nПеребивания (раз):\n"
        f"\tоператор перебил заявителя: {operator_interrupts_caller}\n"
        f"\tзаявитель перебил оператора: {caller_interrupts_operator}\n"
        # f"\tоператор перебил других: {operator_interrupts_others}\n"
        # f"\tдругие перебили оператора: {others_interrupt_operator}\n"
    )

    full_dialog_report += log_msg
    print(log_msg)

    overlaps_durations = calc_overlaps_by_types(
        recognised_segments=recognised_diarization)
    oper_caller_over = overlaps_durations["operator_caller"]
    oper_others_over = overlaps_durations["operator_others"]
    oper_caller_others_over = overlaps_durations["operator_caller_others"]

    overlaps_ratios = calc_overlaps_ratios(
        speakers_durations=speakers_durations,
        overlaps_durations=overlaps_durations)
    oper_caller_over_ratio = overlaps_ratios["operator_caller"]
    oper_others_over_ratio = overlaps_ratios["operator_others"]
    oper_caller_others_over_ratio = overlaps_ratios["operator_caller_others"]

    log_msg = (
        f"\nОдновременная речь (сек, %):\n"
        f"\tоператор-заявитель: {oper_caller_over} ({oper_caller_over_ratio})%\n"
        # f"\tоператор-другие: {oper_others_over} ({oper_others_over_ratio})%\n"
        # f"\tоператор-заявитель-другие: {oper_caller_others_over} ({oper_caller_others_over_ratio})%\n"
    )

    full_dialog_report += log_msg
    print(log_msg)

    dialog_statistics = {
        "full_dialog_report": full_dialog_report,
        "first_speaker_label": first_speaker_label,
        "operator_duration": operator_duration,
        "caller_duration": caller_duration,
        "other_duration": other_duration,
        "total_without_silence_dur": total_without_silence_dur,
        "total_with_silence_dur": total_with_silence_dur,
        "operator_ratio": operator_ratio,
        "caller_ratio": caller_ratio,
        "others_ratio": others_ratio,
        "total_ratio": total_ratio,
        "caller_interrupts_operator": caller_interrupts_operator,
        "operator_interrupts_caller": operator_interrupts_caller,
        "others_interrupt_operator": others_interrupt_operator,
        "operator_interrupts_others": operator_interrupts_others,
        "oper_caller_over": oper_caller_over,
        "oper_others_over": oper_others_over,
        "oper_caller_others_over": oper_caller_others_over,
        "oper_caller_over_ratio": oper_caller_over_ratio,
        "oper_others_over_ratio": oper_others_over_ratio,
        "oper_caller_others_over_ratio": oper_caller_others_over_ratio}

    # print(full_dialog_report)
    return dialog_statistics
