# pip install pyannote.audio
import json
import os
import time
from os import PathLike
from typing import Literal, Union

import requests
from pydub import AudioSegment
from requests import Response

from configs.settings import DIARIZE_OPTIONS
from utils_common.validate_dir_file import check_create_dir_by_file_name


def convert_audio_file(
        incoming_audio_file_path: Union[str, PathLike],
        outgoing_audio_file_path: Union[str, PathLike],
        to_audio_format: Union[str, Literal["ogg", "wav", "mp3"]] = "mp3",
        start_time_secs: int = None,
        end_time_secs: int = None,
        channel_left_right: Union[None, Literal["left", "right"]] = None
) -> str | PathLike:
    check_create_dir_by_file_name(outgoing_audio_file_path)

    _, file_extension = os.path.splitext(incoming_audio_file_path)
    audio_file_format = file_extension.lstrip(".").lower()

    audio = AudioSegment.from_file(file=incoming_audio_file_path,
                                   format=audio_file_format)
    audio_length = len(audio)
    if start_time_secs is None or start_time_secs < 0:
        start_time_secs = 0
    elif start_time_secs > audio_length:
        start_time_secs = 0
        print(f"start_time_msec ({start_time_secs})"
              f"> audio_length ({audio_length}) [WARNING]:\n"
              f"start_time_msec => 0\n")

    if end_time_secs is None or end_time_secs < 0:
        end_time_secs = audio_length
    elif end_time_secs > audio_length:
        prev_end_time_secs = end_time_secs
        end_time_secs = audio_length
        print(f"end_time_secs ({prev_end_time_secs})"
              f"> audio_length ({audio_length}) [WARNING]:\n"
              f"end_time_secs => audio_length ({audio_length})\n")

    audio = audio[start_time_secs:end_time_secs]

    if channel_left_right and audio.channels == 2:
        split_2_mono_audio = audio.split_to_mono()
        if channel_left_right == "left":
            audio = split_2_mono_audio[0]
        elif channel_left_right == "right":
            audio = split_2_mono_audio[1]

    audio = audio.set_frame_rate(16000).set_channels(1)
    audio.export(outgoing_audio_file_path, format=to_audio_format)
    print(f"Converted [OK]: \n"
          f"incoming_audio_file_path: {incoming_audio_file_path}\n"
          f"outgoing_audio_file_path: {outgoing_audio_file_path}\n")
    return outgoing_audio_file_path


def test_api(
        api_token_key: str
) -> Response:
    api_test_result = requests.get(
        url='https://api.pyannote.ai/v1/test',
        headers={'Authorization': f'Bearer {api_token_key}',
                 'Content-Type': 'application/json'})
    return api_test_result


def upload_audio_file(
        input_full_local_fpath: str,
        api_tmp_file_obj_key: str,
        api_token_key: str
) -> str:
    presigned_url = None
    try:
        response = requests.post(
            url='https://api.pyannote.ai/v1/media/input',
            headers={'Authorization': f'Bearer {api_token_key}',
                     'Content-Type': 'application/json'},
            json={'url': f'media://{api_tmp_file_obj_key}'})
        response.raise_for_status()
        presigned_url = response.json()['url']

        with open(input_full_local_fpath, 'rb') as file:
            file_data = file.read()
        response = requests.put(
            url=presigned_url,
            data=file_data,
            headers={'Content-Type': 'application/octet-stream'})
        response.raise_for_status()
        print(f'File uploaded [OK]')
        return presigned_url
    except requests.exceptions.RequestException as error:
        print(f'Uploading file [ERROR]: \n'
              f'input_path: {input_full_local_fpath}\n'
              f'presigned_url: {presigned_url}\n')
        raise error


def diarize_wav_by_object_key(
        api_token_key: str,
        api_tmp_file_obj_key: str,
        speakers_number: Union[1, 2, int]
) -> str:
    try:
        response = requests.post(
            url="https://api.pyannote.ai/v1/diarize",
            headers={"Authorization": f"Bearer {api_token_key}",
                     "Content-Type": "application/json"},
            json={"url": f"media://{api_tmp_file_obj_key}",
                  "numSpeakers": speakers_number})
        response.raise_for_status()
        response_json = response.json()
        print(f"response_json: {response}")
        print(f"response_json['jobId']: {response_json["jobId"]}")
        print(f"response_json['status']: {response_json["status"]}\n")
        return response_json["jobId"]
    except requests.exceptions.RequestException as error:
        print(f"Creating diarization job [ERROR]: "
              f"error: {error}\n"
              f"object_key: {api_tmp_file_obj_key}\n"
              f"api_key: {api_token_key}\n")
        raise error


def get_result_by_job_id(
        api_token_key: str,
        api_job_id: str
) -> dict | None:
    while True:
        response = requests.get(
            url=f"https://api.pyannote.ai/v1/jobs/{api_job_id}",
            headers={"Authorization": f"Bearer {api_token_key}"})
        response_status_code = response.status_code
        response_json = response.json()
        response_text = json.loads(response.text)

        cur_job_output = response_json.get("output", None) if response_json else None
        cur_job_status = response_json.get("status", None) if response_json else None
        cur_job_message = response_text.get("message", None) if response_text else None
        cur_job_error = response_text.get("error", None) if response_text else None
        response_data = {"job_output": cur_job_output,
                         "job_status": cur_job_status,
                         "job_message": cur_job_message,
                         "job_error": cur_job_error,
                         "statusCode": response_status_code}

        if response_status_code != 200:
            print(f"Get job result by job id [ERROR]:\n"
                  f"response.status_code: {response.status_code}\n"
                  f"response.text: {response.text}\n")
            return response_data

        print(f"\n{'>' * 75}\n"
              f"response_status_code: {response_status_code}\n"
              f"cur_job_status: {cur_job_status}\n"
              f"cur_job_output: {cur_job_output}"
              f"response_text (json): {response.text}\n"
              "response_json (dict): {response_json}\n")

        immediate_response_flag = DIARIZE_OPTIONS.PYANNOTE_API_IMMEDIATE_RESPONSE
        if cur_job_status in ["created", "running"]:
            if immediate_response_flag:
                print(f"CURRENT JOB STATUS [WAIT.....]: '{cur_job_status}'\n")
                return response_data
            print(f"CURRENT JOB STATUS [WAITING.....]: '{cur_job_status}'\n")
            time.sleep(DIARIZE_OPTIONS.PYANNOTE_API_REQUEST_PAUSE)
            continue
        elif cur_job_status in ["failed", "canceled"]:
            print(f"CURRENT JOB STATUS [ERROR]: '{cur_job_status}'\n")
            return response_data
        elif cur_job_status == "succeeded":
            print(f"CURRENT JOB STATUS [OK]: '{cur_job_status}'\n")
            return response_data
