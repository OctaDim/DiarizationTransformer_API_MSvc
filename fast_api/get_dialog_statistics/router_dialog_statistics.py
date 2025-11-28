# import asyncio
# from functools import partial

from fastapi import (
    APIRouter, HTTPException, status)
from fastapi.responses import JSONResponse

from configs.console_colors import CONSOLE_COLORS
from configs.settings import DIARIZE_OPTIONS
from diarize_common_funcs.durations_by_speakers import calc_durations_by_speakers
from diarize_common_funcs.get_recognized_segments import get_recognized_segments
from diarize_common_funcs.interruptions_by_types import count_interruptions_by_types
from diarize_common_funcs.overlaps_by_types import calc_overlaps_by_types
from diarize_common_funcs.overlaps_ratios import calc_overlaps_ratios
from diarize_common_funcs.ratios_by_speakers import calc_ratios_by_speakers
from diarize_via_remote_api.api_functions.api_diarize_audio_funcs import test_api, get_result_by_job_id
from fast_api.app_auth.funcs_auth import verify_prod_username_password
from fast_api.app_auth.scheme_auth import AuthDataDiarize
from fast_api.get_dialog_statistics.func_get_dialog_statistics import calc_dialog_statistics
from fast_api.get_dialog_statistics.scheme_dialog_statistics import (
    PyannoteApiData, PyannoteApiJobIds)

diarize_base_url_name = DIARIZE_OPTIONS.DIARIZE_API_URL_BASE_NAME
router_get_dialog_statistics = APIRouter(prefix=f"/{diarize_base_url_name}",
                                         tags=[DIARIZE_OPTIONS.PYANNOTE_API_ROUTERS_TAG])


@router_get_dialog_statistics.post(path="/dialog_statistics/",
                                   # TODO: Describe responses here
                                   response_model=None)
async def get_dialog_statistics_by_job_ids(
        auth_data: AuthDataDiarize,
        pyannote_api_data: PyannoteApiData,
        pyannote_api_job_ids: PyannoteApiJobIds,
) -> JSONResponse:
    verify_prod_username_password(username=auth_data.username,
                                  password=auth_data.password)

    pyannote_api_token = pyannote_api_data.pyannote_api_token

    api_test_conn_resp = test_api(api_token_key=pyannote_api_token)
    pyannote_api_status_code = api_test_conn_resp.status_code
    if pyannote_api_status_code != 200:
        log_text = (f"PyAnnote API test connection [ERROR]:\n"
                    f"api_test_conn_resp: {api_test_conn_resp}\n"
                    f"status_code: {pyannote_api_status_code}\n")
        print(log_text)
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,
                            detail=log_text)
    print(f"PyAnnote API test connection [OK]: {api_test_conn_resp}")

    operator_job_id = pyannote_api_job_ids.operator_job_id
    caller_job_id = pyannote_api_job_ids.caller_job_id
    all_speakers_job_id = pyannote_api_job_ids.all_speakers_job_id
    # operator_job_id = "0dd61b85-ff4a-4272-a459-ddd76e999fea"
    # caller_job_id = "0348cd3f-84ee-45eb-a8e0-b9226550f46f"
    # all_speakers_job_id = "47a6aae2-897c-4f7f-8dd3-499028f489d9"

    operator_resp_output = get_result_by_job_id(
        api_token_key=pyannote_api_token,
        api_job_id=operator_job_id)
    print(f"\nFUNC RETURN: operator_resp_output: {operator_resp_output}\n")

    if not operator_resp_output:
        log_text = (f"Not valid operator_job_id "
                    f"(API return None) [ERROR]:\n"
                    f"operator_job_id: {operator_job_id}\n"
                    f"operator_resp_output: {operator_resp_output}\n")
        print(log_text)
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,
                            detail=log_text)

    operator_diarization = operator_resp_output["diarization"]
    operator_first_segment = operator_diarization[0]
    operator_first_start = operator_first_segment["start"]
    print(f"\noperator_first_segment: {operator_first_segment}\n")
    print(f"\noperator_first_segment_start: {operator_first_start}\n")

    caller_resp_output = get_result_by_job_id(
        api_token_key=pyannote_api_token,
        api_job_id=caller_job_id)
    print(f"\nFUNC RETURN: caller_resp_output: {caller_resp_output}\n")

    if not caller_resp_output:
        log_text = (f"Not valid caller_resp_output "
                    f"(API return None) [ERROR]:\n"
                    f"caller_job_id: {caller_job_id}\n"
                    f"caller_resp_output: {caller_resp_output}\n")
        print(log_text)
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,
                            detail=log_text)

    caller_diarization = caller_resp_output["diarization"]
    caller_first_segment = caller_diarization[0]
    caller_first_start = caller_first_segment["start"]
    print(f"\ncaller_first_segment: {caller_first_segment}\n")
    print(f"\ncaller_first_segment_start: {caller_first_start}\n")

    all_speakers_resp_output = get_result_by_job_id(
        api_token_key=pyannote_api_token,
        api_job_id=all_speakers_job_id)
    print(f"\nFUNC RETURN: all_speakers_resp_output: {all_speakers_resp_output}\n")

    if not all_speakers_resp_output:
        log_text = (f"Not valid all_speakers_resp_output "
                    f"(API return None) [ERROR]:\n"
                    f"all_speakers_job_id: {all_speakers_job_id}\n"
                    f"all_speakers_resp_output: {all_speakers_resp_output}\n")
        print(log_text)
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,
                            detail=log_text)

    all_speakers_diarization = all_speakers_resp_output["diarization"]
    print(f"\nall_speakers_diarization: {all_speakers_diarization}\n")
    all_speakers_first_segm_speaker = all_speakers_diarization[0]["speaker"]
    print(f"\nall_speakers_first_segment_speaker: {all_speakers_first_segm_speaker}\n")

    await calc_dialog_statistics(
        operator_diarization=operator_diarization,
        caller_diarization=caller_diarization,
        all_speakers_diarization=all_speakers_diarization)

    try:
        json_content = {}
        # json_content = {
        #     "message": response_message,
        #     "pyannote_api_job_ids": pyannote_api_job_ids,
        #     # "operator_job_id": operator_job_id,
        #     # "caller_job_id": caller_job_id,
        #     # "all_speakers_job_id": all_speakers_job_id,
        #     "operator audio frame": operator_frame_str,
        #     "caller audio frame": caller_frame_str,
        #     "all speakers audio frame": all_speakers_frame_str,
        #     "uploaded file content type": upload_file.content_type,
        #     "uploaded file name": upload_file.filename,
        #     "allowed file mime types": ALLOWED_FILE_MIME_TYPES,
        #     "allowed file extensions": ALLOWED_FILE_EXTENSIONS,
        #     "username": username, }

        json_response = JSONResponse(
            content=json_content,
            status_code=status.HTTP_200_OK)

        green_color = CONSOLE_COLORS.BRIGHT_GREEN
        blue_color = CONSOLE_COLORS.BRIGHT_BLUE
        reset_color = CONSOLE_COLORS.RESET
        # print(f"Response message: {response_message}\n"
        #       f"pyannote_api_job_ids: {green_color}{pyannote_api_job_ids}{reset_color}\n"
        #       f"operator_job_id: {blue_color}{operator_job_id}{reset_color}\n"
        #       f"caller_job_id: {blue_color}{caller_job_id}{reset_color}\n"
        #       f"all_speakers_job_id: {blue_color}{all_speakers_job_id}{reset_color}\n"
        #       f"operator audio frame: {operator_frame_str}\n"
        #       f"caller audio frame: {caller_frame_str}\n"
        #       f"all speakers audio frame: {all_speakers_frame_str}\n"
        #       f"operator temp audio file: {right_channel_audio_f_path}\n"
        #       f"caller temp audio file: {left_channel_audio_f_path}\n"
        #       f"all speakers temp audio: {stereo_channel_audio_f_path}\n"
        #       f"upload_file.content_type: {upload_file.content_type}\n"
        #       f"upload_file.filename: {upload_file.filename}\n"
        #       f"username: {username}\n")
        return json_response
    except Exception as error:
        log_text = f"Get call statistics router [ERROR]: error: {error}"
    print(log_text)
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=log_text)
