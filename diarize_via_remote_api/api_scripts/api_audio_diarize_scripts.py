import os.path
import uuid

from diarize_common_funcs.durations_by_speakers import calc_durations_by_speakers
from diarize_common_funcs.get_recognized_segments import get_recognized_segments
from diarize_common_funcs.interruptions_by_types import count_interruptions_by_types
from diarize_common_funcs.overlaps_by_types import calc_overlaps_by_types
from diarize_common_funcs.overlaps_ratios import calc_overlaps_ratios
from diarize_common_funcs.ratios_by_speakers import calc_ratios_by_speakers
from diarize_via_remote_api.api_functions.api_diarize_audio_funcs import (
    get_result_by_job_id, test_api, convert_audio_file, upload_audio_file, diarize_wav_by_object_key)

api_key = "sk_0d466286b6784130a2d669e1a1ab481f"

ogg_full_fpath = r"/home/octadim/PycharmProjects/DiarizationTransformer_API_MSvc/audio_samples/ogg/1.ogg"
wav_full_fpath = r"/home/octadim/PycharmProjects/DiarizationTransformer_API_MSvc/audio_samples/wav/1.wav"
mp3_full_fpath = r"/home/octadim/PycharmProjects/DiarizationTransformer_API_MSvc/audio_samples/mp3/1.mp3"
ogg_full_fpath = os.path.normpath(ogg_full_fpath)
wav_full_fpath = os.path.normpath(wav_full_fpath)

api_connection_test = test_api(api_key)
print(f"\nFUNC RETURN: api_connection_test: {api_connection_test}\n")

operator_object_key = f"{uuid.uuid4()}"
operator_converted_fpath = convert_audio_file(
    incoming_audio_file_path=ogg_full_fpath,
    # outgoing_audio_file_path=ogg_full_fpath,
    outgoing_audio_file_path=mp3_full_fpath,
    # outgoing_audio_file_path=wav_full_fpath,
    to_audio_format="mp3",
    start_time_secs=7000,
    end_time_secs=60000,
    channel_left_right="right")
print(f"\nFUNC RETURN: operator_converted_fpath: "
      f"{operator_converted_fpath}\n")

operator_presigned_url = upload_audio_file(
    input_full_local_fpath=operator_converted_fpath,
    api_tmp_file_obj_key=operator_object_key,
    api_token_key=api_key)
print(f"\nFUNC RETURN: operator_presigned_url: "
      f"{operator_presigned_url}\n")

operator_job_id = diarize_wav_by_object_key(
    api_tmp_file_obj_key=operator_object_key,
    api_token_key=api_key,
    speakers_number=1)
print(f"\nFUNC RETURN: operator_job_id: {operator_job_id}\n")

# operator_job_id = "0dd61b85-ff4a-4272-a459-ddd76e999fea"
operator_resp_output = get_result_by_job_id(
    api_token_key=api_key,
    api_job_id=operator_job_id)
print(f"\nFUNC RETURN: operator_resp_output: {operator_resp_output}\n")

operator_diarization = operator_resp_output["diarization"]
operator_first_segment = operator_diarization[0]
operator_first_start = operator_first_segment["start"]
print(f"\noperator_first_segment: {operator_first_segment}\n")
print(f"\noperator_first_segment_start: {operator_first_start}\n")

caller_object_key = f"{uuid.uuid4()}"
caller_converted_fpath = convert_audio_file(
    incoming_audio_file_path=ogg_full_fpath,
    # outgoing_audio_file_path=ogg_full_fpath,
    outgoing_audio_file_path=mp3_full_fpath,
    # outgoing_audio_file_path=wav_full_fpath,
    to_audio_format="mp3",
    start_time_secs=7000,
    end_time_secs=60000,
    channel_left_right="left")

caller_presigned_url = upload_audio_file(
    input_full_local_fpath=caller_converted_fpath,
    api_tmp_file_obj_key=caller_object_key,
    api_token_key=api_key)
print(f"\nFUNC RETURN: caller_presigned_url: {caller_presigned_url}\n")

caller_job_id = diarize_wav_by_object_key(
    api_tmp_file_obj_key=caller_object_key,
    api_token_key=api_key,
    speakers_number=1)
print(f"\nFUNC RETURN: caller_job_id: {caller_job_id}\n")

# caller_job_id = "0348cd3f-84ee-45eb-a8e0-b9226550f46f"
caller_resp_output = get_result_by_job_id(
    api_token_key=api_key,
    api_job_id=caller_job_id)
print(f"\nFUNC RETURN: caller_resp_output: {caller_resp_output}\n")

caller_diarization = caller_resp_output["diarization"]
caller_first_segment = caller_diarization[0]
caller_first_start = caller_first_segment["start"]
print(f"\ncaller_first_segment: {caller_first_segment}\n")
print(f"\ncaller_first_segment_start: {caller_first_start}\n")

all_speakers_object_key = f"{uuid.uuid4()}"
all_speakers_converted_fpath = convert_audio_file(
    incoming_audio_file_path=ogg_full_fpath,
    # outgoing_audio_file_path=ogg_full_fpath,
    outgoing_audio_file_path=mp3_full_fpath,
    # outgoing_audio_file_path=wav_full_fpath,
    to_audio_format="mp3",
    start_time_secs=7000,
    end_time_secs=None,
    channel_left_right=None)

all_speakers_presigned_url = upload_audio_file(
    input_full_local_fpath=all_speakers_converted_fpath,
    api_tmp_file_obj_key=all_speakers_object_key,
    api_token_key=api_key)
print(f"\nFUNC RETURN: all_speakers_presigned_url: "
      f"{all_speakers_presigned_url}\n")

all_speakers_job_id = diarize_wav_by_object_key(
    api_tmp_file_obj_key=all_speakers_object_key,
    api_token_key=api_key,
    speakers_number=2)
print(f"\nFUNC RETURN: all_speakers_job_id: {all_speakers_job_id}\n")

# all_speakers_job_id = "47a6aae2-897c-4f7f-8dd3-499028f489d9"
all_speakers_resp_output = get_result_by_job_id(
    api_token_key=api_key,
    api_job_id=all_speakers_job_id)
print(f"\nFUNC RETURN: all_speakers_resp_output: {all_speakers_resp_output}\n")
all_speakers_diarization = all_speakers_resp_output["diarization"]
print(f"\nall_speakers_diarization: {all_speakers_diarization}\n")
all_speakers_first_segm_speaker = all_speakers_diarization[0]["speaker"]
print(f"\nall_speakers_first_segment_speaker: {all_speakers_first_segm_speaker}\n")

recognised_data = get_recognized_segments(
    operator_segments=operator_diarization,
    caller_segments=caller_diarization,
    all_speakers_segments=all_speakers_diarization)
recognised_diarization = recognised_data["recognized_diary"]
first_speaker = recognised_data["first_speaker"]
print(f"\nДневник разговора:\n"
      f"\tпервым заговорил: {first_speaker}\n"
      f"\tхронология: {recognised_diarization}\n")

speakers_durations = calc_durations_by_speakers(
    recognized_segments=recognised_diarization)
operator_duration = speakers_durations["operator"]
caller_duration = speakers_durations["caller"]
other_duration = speakers_durations["others"]
total_all_speakers_dur = speakers_durations["total_all_speakers_dur"]
total_with_silence_dur = speakers_durations["total_with_silence_dur"]

call_ratios = calc_ratios_by_speakers(
    durations_by_speakers=speakers_durations)
operator_ratio = call_ratios["operator"]
caller_ratio = call_ratios["caller"]
others_ratio = call_ratios["others"]
total_ratio = call_ratios["total"]

print(f"\nДлительность речи (сек, %):\n"
      f"\toператор: {operator_duration} ({operator_ratio}%)\n"
      f"\tзаявитель: {caller_duration} ({caller_ratio}%)\n"
      f"\tдругие: {other_duration} ({others_ratio}%)\n"
      f"\tВсего речь: {total_all_speakers_dur} ({total_ratio}%)\n"
      f"\tВсего c тишиной: {total_with_silence_dur}\n")

interruptions = count_interruptions_by_types(
    recognised_segments=recognised_diarization)
caller_interrupts_operator = interruptions["operator_by_caller"]
operator_interrupts_caller = interruptions["caller_by_operator"]
others_interrupt_operator = interruptions["operator_by_others"]
operator_interrupts_others = interruptions["others_by_operator"]
print(f"\nПеребивания (раз):\n"
      f"\tоператор перебил заявителя: {operator_interrupts_caller}\n"
      f"\tзаявитель перебил оператора: {caller_interrupts_operator}\n"
      f"\tоператор перебил других: {operator_interrupts_others}\n"
      f"\tдругие перебили оператора: {others_interrupt_operator}\n")

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

print(f"\nОдновременная речь (сек, %):\n"
      f"оператор-заявитель: {oper_caller_over} ({oper_caller_over_ratio})%\n"
      f"оператор-другие: {oper_others_over} ({oper_others_over_ratio})%\n"
      f"оператор-заявитель-другие: {oper_caller_over} ({oper_caller_others_over_ratio})%\n")
