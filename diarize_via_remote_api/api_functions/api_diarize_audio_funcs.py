# pip install pyannote.audio

import os
import time
from os import PathLike
from typing import Literal, Union

import requests
from pydub import AudioSegment
from requests import Response

from utils_common.validate_dir_file import check_create_dir_by_file_name


def convert_audio_file(
        incoming_audio_file_path: Union[str, PathLike],
        outgoing_audio_file_path: Union[str, PathLike],
        to_audio_format: Union[str, Literal["ogg", "wav", "mp3"]] = "mp3",
        start_time_msec: int = None,
        end_time_msec: int = None,
        channel_left_right: Union[None, Literal["left", "right"]] = None
) -> str | PathLike:
    """ Convert audio file
    :param incoming_audio_file_path: str or PathLike: full .ogg file path including filename with extension
    :param outgoing_audio_file_path: str or PathLike: full .wav file path including filename with extension
    :param to_audio_format: Literal["ogg", "wav", "mp3"]: outgoing audio format
    :param start_time_msec: int: e.g. 7000. Converted file starts from 7 sec
    :param end_time_msec: int: e.g. 60000. Converted file ends in 1 min
    :param channel_left_right: None|Literal["left", "right"]: only left or right channel
    :return: None (save .wav file into to_wav_file_path path)"""
    check_create_dir_by_file_name(outgoing_audio_file_path)

    _, file_extension = os.path.splitext(incoming_audio_file_path)
    audio_file_format = file_extension.lstrip(".").lower()

    audio = AudioSegment.from_file(file=incoming_audio_file_path,
                                   format=audio_file_format)
    audio = audio[start_time_msec:end_time_msec]

    if audio.channels == 2:
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
        if response.status_code != 200:
            print(f"Get job result by job id [ERROR]:\n"
                  f"response.status_code: {response.status_code}\n"
                  f"response.text: {response.text}\n")
            break
        response_json = response.json()
        response_status = response_json["status"]
        response_output = response_json["output"]
        print("\n>>>>>>>>>>>>>>>>>>>>>>>>")
        print(f"response_status: {response_status}")
        print(f"response_json: {response_json}")
        print(f"response_output: {response_output}")
        if response_status == "created":
            print(f"CURRENT JOB STATUS: '{response_status}' ==> waiting...\n")
            time.sleep(5)
            continue
        elif response_status in ["failed", "canceled"]:
            print(f"CURRENT JOB STATUS: '{response_status}' ==> broken\n")
            break
        elif response_status == "succeeded":
            print(f"CURRENT JOB STATUS: '{response_status}' ==> succeeded\n")
            return response_output
