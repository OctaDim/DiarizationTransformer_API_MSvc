# import asyncio
# from functools import partial
import base64

from fastapi import (
    APIRouter, HTTPException, status)
from fastapi.responses import JSONResponse

from configs.console_colors import CONSOLE_COLORS
from configs.settings import DIARIZE_OPTIONS
from diarize_via_remote_api.api_functions.api_diarize_audio_funcs import (
    test_api, get_result_by_job_id)
from fast_api.app_auth.funcs_auth import verify_prod_username_password
from fast_api.app_auth.scheme_auth import AuthDataDiarize
from fast_api.get_dialog_statistics.func_get_dialog_statistics import (
    calc_dialog_statistics)
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

    if not all([operator_job_id, caller_job_id, all_speakers_job_id]):
        log_text = (f"REQUEST JOB IDS EMPTY VALUE(S) [ERROR]:\n"
                    f"operator_job_id: {operator_job_id}\n"
                    f"caller_job_id: {caller_job_id}\n"
                    f"all_speakers_job_id: {all_speakers_job_id}\n")
        print(log_text)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=log_text)

    operator_resp_data = get_result_by_job_id(
        api_token_key=pyannote_api_token,
        api_job_id=operator_job_id)
    print(f"\nFUNC RETURN: operator_resp_data: {operator_resp_data}\n")

    operator_job_output = operator_resp_data["job_output"]
    operator_job_status = operator_resp_data["job_status"]
    operator_job_message = operator_resp_data["job_message"]
    operator_job_error = operator_resp_data["job_error"]
    operator_status_code = operator_resp_data["statusCode"]

    if operator_job_status in ["created", "running"]:
        log_text = (f"GETTING API OPERATOR OUTPUT IN PROCESS [WAIT.....]:\n"
                    f"dialog_statistics: {None}\n"
                    f"full_dialog_report: {None}\n"
                    f"operator_job_output: {operator_job_output}\n"
                    f"operator_job_status: {operator_job_status}\n"
                    f"operator_job_message: {operator_job_message}\n"
                    f"operator_job_error: {operator_job_error}\n"
                    f"operator_status_code: {operator_status_code}\n")
        print(log_text)
        raise HTTPException(status_code=status.HTTP_102_PROCESSING,
                            detail=log_text)

    if not operator_job_output:
        log_text = (f"API EMPTY OPERATOR OUTPUT ANSWER [ERROR]:\n"
                    f"dialog_statistics: {None}\n"
                    f"full_dialog_report: {None}\n"
                    f"operator_job_output: {operator_job_output}\n"
                    f"operator_job_status: {operator_job_status}\n"
                    f"operator_job_message: {operator_job_message}\n"
                    f"operator_job_error: {operator_job_error}\n"
                    f"operator_status_code: {operator_status_code}\n")
        print(log_text)
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,
                            detail=log_text)

    operator_diarization = operator_job_output["diarization"]
    operator_first_segment = operator_diarization[0]
    operator_first_start = operator_first_segment["start"]
    print(f"\noperator_first_segment: {operator_first_segment}\n")
    print(f"\noperator_first_segment_start: {operator_first_start}\n")

    caller_resp_data = get_result_by_job_id(
        api_token_key=pyannote_api_token,
        api_job_id=caller_job_id)
    print(f"\nFUNC RETURN: caller_resp_data: {caller_resp_data}\n")

    caller_job_output = caller_resp_data["job_output"]
    caller_job_status = caller_resp_data["job_status"]
    caller_job_message = caller_resp_data["job_message"]
    caller_job_error = caller_resp_data["job_error"]
    caller_status_code = caller_resp_data["statusCode"]

    if caller_job_status in ["created", "running"]:
        log_text = (f"GETTING API CALLER OUTPUT IN PROCESS [WAIT.....]:\n"
                    f"dialog_statistics: {None}\n"
                    f"full_dialog_report: {None}\n"
                    f"caller_job_output: {caller_job_output}\n"
                    f"caller_job_status: {caller_job_status}\n"
                    f"caller_job_message: {caller_job_message}\n"
                    f"caller_job_error: {caller_job_error}\n"
                    f"caller_status_code: {caller_status_code}\n")
        print(log_text)
        raise HTTPException(status_code=status.HTTP_102_PROCESSING,
                            detail=log_text)

    if not caller_job_output:
        log_text = (f"API EMPTY CALLER OUTPUT ANSWER [ERROR]:\n"
                    f"dialog_statistics: {None}\n"
                    f"full_dialog_report: {None}\n"
                    f"caller_job_output: {caller_job_output}\n"
                    f"caller_job_status: {caller_job_status}\n"
                    f"caller_job_message: {caller_job_message}\n"
                    f"caller_job_error: {caller_job_error}\n"
                    f"caller_status_code: {caller_status_code}\n")
        print(log_text)
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,
                            detail=log_text)

    caller_diarization = caller_job_output["diarization"]
    caller_first_segment = caller_diarization[0]
    caller_first_start = caller_first_segment["start"]
    print(f"\ncaller_first_segment: {caller_first_segment}\n")
    print(f"\ncaller_first_segment_start: {caller_first_start}\n")

    all_speakers_resp_data = get_result_by_job_id(
        api_token_key=pyannote_api_token,
        api_job_id=all_speakers_job_id)
    print(f"\nFUNC RETURN: all_speakers_resp_data: {all_speakers_resp_data}\n")

    all_speakers_job_output = all_speakers_resp_data["job_output"]
    all_speakers_job_status = all_speakers_resp_data["job_status"]
    all_speakers_job_message = all_speakers_resp_data["job_message"]
    all_speakers_job_error = all_speakers_resp_data["job_error"]
    all_speakers_status_code = all_speakers_resp_data["statusCode"]

    if all_speakers_job_status in ["created", "running"]:
        log_text = (f"GETTING API ALL SPEAKERS OUTPUT IN PROCESS [WAIT.....]:\n"
                    f"dialog_statistics: {None}\n"
                    f"full_dialog_report: {None}\n"
                    f"all_speakers_job_output: {all_speakers_job_output}\n"
                    f"all_speakers_job_status: {all_speakers_job_status}\n"
                    f"all_speakers_job_message: {all_speakers_job_message}\n"
                    f"all_speakers_job_error: {all_speakers_job_error}\n"
                    f"all_speakers_status_code: {all_speakers_status_code}\n")
        print(log_text)
        raise HTTPException(status_code=status.HTTP_102_PROCESSING,
                            detail=log_text)

    if not all_speakers_job_output:
        log_text = (f"API EMPTY ALL SPEAKERS OUTPUT ANSWER [ERROR]:\n"
                    f"dialog_statistics: {None}\n"
                    f"full_dialog_report: {None}\n"
                    f"all_speakers_job_output: {all_speakers_job_output}\n"
                    f"all_speakers_job_status: {all_speakers_job_status}\n"
                    f"all_speakers_job_message: {all_speakers_job_message}\n"
                    f"all_speakers_job_error: {all_speakers_job_error}\n"
                    f"all_speakers_status_code: {all_speakers_status_code}\n")
        print(log_text)
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,
                            detail=log_text)

    all_speakers_diarization = all_speakers_job_output["diarization"]
    print(f"\nall_speakers_diarization: {all_speakers_diarization}\n")
    all_speakers_first_segm_speaker = all_speakers_diarization[0]["speaker"]
    print(f"\nall_speakers_first_segment_speaker: {all_speakers_first_segm_speaker}\n")

    dialog_statistics = await calc_dialog_statistics(
        operator_diarization=operator_diarization,
        caller_diarization=caller_diarization,
        all_speakers_diarization=all_speakers_diarization)

    response_message = "call statistics were obtained successfully [OK]"
    pyannote_api_job_ids = pyannote_api_job_ids.model_dump()
    full_dialog_report = dialog_statistics.get("full_dialog_report")
    dialog_statistics.pop("full_dialog_report")
    report_base64 = base64.b64encode(full_dialog_report.encode('utf-8')).decode('utf-8')

    try:
        json_content = {
            "message": response_message,
            "pyannote_api_job_ids": pyannote_api_job_ids,
            "dialog_statistics": dialog_statistics,
            "full_dialog_report": full_dialog_report,
            # "report_file": {"content": report_base64,
            #                 "filename": "full_dialog_report.txt",
            #                 "mime_type": "text/plain"},
            # "operator_job_id": caller_job_id,
            # "caller_job_id": caller_job_id,
            # "all_speakers_job_id": all_speakers_job_id,
            "username": auth_data.username}

        json_response = JSONResponse(
            content=json_content,
            status_code=status.HTTP_200_OK)

        green_color = CONSOLE_COLORS.BRIGHT_GREEN
        blue_color = CONSOLE_COLORS.BRIGHT_BLUE
        reset_color = CONSOLE_COLORS.RESET
        print(f"Response message: {response_message}\n"
              f"full_dialog_report: {green_color}{full_dialog_report}{reset_color}\n"
              f"dialog_statistics: {blue_color}{dialog_statistics}{reset_color}\n"
              f"pyannote_api_job_ids: {pyannote_api_job_ids}\n"
              f"operator_job_id: {operator_job_id}\n"
              f"caller_job_id: {caller_job_id}\n"
              f"all_speakers_job_id: {all_speakers_job_id}\n"
              f"username: {auth_data.username}\n")
        return json_response
    except Exception as error:
        log_text = f"Getting call statistics router [ERROR]: error: {error}"
    print(log_text)
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=log_text)
