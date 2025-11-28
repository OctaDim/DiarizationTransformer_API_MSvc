# import asyncio
# from functools import partial
import os
import uuid
from typing import Annotated

from fastapi import (
    APIRouter, File, Form, HTTPException, UploadFile, status)
from fastapi.responses import JSONResponse

from configs.console_colors import CONSOLE_COLORS
from configs.settings import DIARIZE_OPTIONS, BASE_DIR
from diarize_via_remote_api.api_functions.api_diarize_audio_funcs import (
    test_api, convert_audio_file, upload_audio_file,
    diarize_wav_by_object_key)
from fast_api.app_auth.funcs_auth import verify_prod_username_password
from utils_common.get_file_name_extra_part import (
    get_file_name_with_extra_part)
from utils_common.normalized_path import (
    get_full_file_normal_path, get_full_dir_normal_path)
from utils_common.validate_dir_file import (
    check_create_dir_by_file_name)

diarize_base_url_name = DIARIZE_OPTIONS.DIARIZE_API_URL_BASE_NAME
router_upload_audio_file = APIRouter(
    prefix=f"/{diarize_base_url_name}",
    tags=[DIARIZE_OPTIONS.PYANNOTE_API_ROUTERS_TAG])


@router_upload_audio_file.post(path="/upload_audio_file/",
                               # TODO: Describe responses here
                               response_model=None)
async def upload_ogg_file_get_job_id(
        upload_file: Annotated[UploadFile, File(
            description="file .ogg, mp3 or .wav")],
        username: Annotated[str, Form()],
        password: Annotated[str, Form()],
        pyannote_api_token: Annotated[str, Form()],
        # account_id: Annotated[str, Form()],
        # account_username: Annotated[str, Form()],
) -> JSONResponse:
    verify_prod_username_password(username=username,
                                  password=password)

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

    print("\nAudio file extension and format verifying:")
    ALLOWED_FILE_EXTENSIONS = ("ogg", "wav", "mp3")
    ALLOWED_FILE_MIME_TYPES = (
        "audio/ogg", "application/ogg",  # .ogg
        "audio/wav", "audio/x-wav", "audio/wave",  # .wav
        "audio/mpeg")  # .mp3

    OPERATOR_TEMP_AUDIO_START = DIARIZE_OPTIONS.OPERATOR_TMP_AUDIO_START_SEC
    OPERATOR_TEMP_AUDIO_END = DIARIZE_OPTIONS.OPERATOR_TMP_AUDIO_END_SEC
    CALLER_TEMP_AUDIO_START = DIARIZE_OPTIONS.CALLER_TMP_AUDIO_START_SEC
    CALLER_TEMP_AUDIO_END = DIARIZE_OPTIONS.CALLER_TMP_AUDIO_END_SEC
    ALL_SPEAKERS_TMP_AUDIO_START = DIARIZE_OPTIONS.ALL_SPEAKERS_TMP_AUDIO_START_SEC
    ALL_SPEAKERS_TMP_AUDIO_END = DIARIZE_OPTIONS.ALL_SPEAKERS_TMP_AUDIO_END_SEC

    if not upload_file:
        log_text = (f"Audio file {ALLOWED_FILE_EXTENSIONS} not passed [ERROR]: "
                    f"upload_file: {upload_file}")
        print(log_text)
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,
                            detail=log_text)

    if not pyannote_api_token:
        log_text = (f"Empty PyAnnote API token [ERROR]: "
                    f"pyannote_api_token: {pyannote_api_token}")
        print(log_text)
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,
                            detail=log_text)

    if upload_file.content_type not in ALLOWED_FILE_MIME_TYPES:
        log_text = (f"Unsupported file MIME content type [ERROR]: "
                    f"upload_file.content_type: {upload_file.content_type}, "
                    f"allowed MIME types: {ALLOWED_FILE_MIME_TYPES}")
        print(log_text)
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,
                            detail=log_text)

    allowed_extensions = ALLOWED_FILE_EXTENSIONS
    audio_file_name = os.path.basename(upload_file.filename)
    origin_file_name, file_extension = os.path.splitext(audio_file_name)
    file_extension = file_extension.lower()

    if not audio_file_name.lower().endswith(allowed_extensions):
        log_text = (f"File extension not in {allowed_extensions} [ERROR]:\n"
                    f"upload_file.filename: {upload_file.filename}\n"
                    f"file extension: {file_extension}\n"
                    f"allowed extensions: {allowed_extensions}\n")
        print(log_text)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=log_text)

    orig_audio_file_path = get_full_file_normal_path(
        all_dir_str_parts=[BASE_DIR, DIARIZE_OPTIONS.TEMPORARY_AUDIO_FILES_DIR],
        file_name_with_ext=audio_file_name)

    tmp_audio_f_name_prefix = DIARIZE_OPTIONS.TEMPORARY_AUDIO_FILE_PREFIX
    tmp_audio_f_extra_name_path = get_file_name_with_extra_part(
        orig_file_full_path=orig_audio_file_path,
        filename_prefix=tmp_audio_f_name_prefix)

    try:
        check_create_dir_by_file_name(
            full_file_path=tmp_audio_f_extra_name_path)

        upload_content = await upload_file.read()
        uploaded_file_size = len(upload_content)
        if 0 <= uploaded_file_size <= 100:
            log_text = ("Uploaded file is zero bytes or too small [ERROR]:"
                        "uploaded_file_size: {uploaded_file_size}\n")
            print(log_text)
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail=log_text)

        with open(tmp_audio_f_extra_name_path, "wb") as audio_file:
            audio_file.write(upload_content)
        print(f"Temporary audio file created [OK]: "
              f"{tmp_audio_f_extra_name_path}")

        audio_file_extra_name = os.path.basename(tmp_audio_f_extra_name_path)
        file_extra_name, file_extension = os.path.splitext(audio_file_extra_name)

        converted_files_dir_path = get_full_dir_normal_path(
            all_dir_str_parts=[BASE_DIR, DIARIZE_OPTIONS.CONVERTED_AUDIO_FILES_DIR])
        check_create_dir_by_file_name(
            full_file_path=converted_files_dir_path)

        audio_type_for_api = DIARIZE_OPTIONS.CONVERTED_AUDIO_TYPE_FOR_API
        right_channel_audio_f_path = get_full_file_normal_path(
            all_dir_str_parts=[converted_files_dir_path],
            file_name_with_ext=f"{file_extra_name}_(RIGHT).{audio_type_for_api}")
        left_channel_audio_f_path = get_full_file_normal_path(
            all_dir_str_parts=[converted_files_dir_path],
            file_name_with_ext=f"{file_extra_name}_(LEFT).{audio_type_for_api}")
        stereo_channel_audio_f_path = get_full_file_normal_path(
            all_dir_str_parts=[converted_files_dir_path],
            file_name_with_ext=f"{file_extra_name}_(STEREO).{audio_type_for_api}")

        operator_object_key = f"{uuid.uuid4()}"
        operator_converted_fpath = convert_audio_file(
            incoming_audio_file_path=tmp_audio_f_extra_name_path,
            outgoing_audio_file_path=right_channel_audio_f_path,
            to_audio_format=audio_type_for_api,
            start_time_secs=OPERATOR_TEMP_AUDIO_START,
            end_time_secs=OPERATOR_TEMP_AUDIO_END,
            channel_left_right="right")
        print(f"\nFUNC RETURN: operator_converted_fpath: "
              f"{operator_converted_fpath}\n")

        operator_presigned_url = upload_audio_file(
            input_full_local_fpath=operator_converted_fpath,
            api_tmp_file_obj_key=operator_object_key,
            api_token_key=pyannote_api_token)
        print(f"\nFUNC RETURN: operator_presigned_url: "
              f"{operator_presigned_url}\n")

        operator_job_id = diarize_wav_by_object_key(
            api_tmp_file_obj_key=operator_object_key,
            api_token_key=pyannote_api_token,
            speakers_number=None)
        print(f"\nFUNC RETURN: operator_job_id: {operator_job_id}\n")

        caller_object_key = f"{uuid.uuid4()}"
        caller_converted_fpath = convert_audio_file(
            incoming_audio_file_path=tmp_audio_f_extra_name_path,
            outgoing_audio_file_path=left_channel_audio_f_path,
            to_audio_format=audio_type_for_api,
            start_time_secs=CALLER_TEMP_AUDIO_START,
            end_time_secs=CALLER_TEMP_AUDIO_END,
            channel_left_right="left")

        caller_presigned_url = upload_audio_file(
            input_full_local_fpath=caller_converted_fpath,
            api_tmp_file_obj_key=caller_object_key,
            api_token_key=pyannote_api_token)
        print(f"\nFUNC RETURN: caller_presigned_url: {caller_presigned_url}\n")

        caller_job_id = diarize_wav_by_object_key(
            api_tmp_file_obj_key=caller_object_key,
            api_token_key=pyannote_api_token,
            speakers_number=None)
        print(f"\nFUNC RETURN: caller_job_id: {caller_job_id}\n")

        all_speakers_object_key = f"{uuid.uuid4()}"
        all_speakers_converted_fpath = convert_audio_file(
            incoming_audio_file_path=tmp_audio_f_extra_name_path,
            outgoing_audio_file_path=stereo_channel_audio_f_path,
            to_audio_format=audio_type_for_api,
            start_time_secs=ALL_SPEAKERS_TMP_AUDIO_START,
            end_time_secs=ALL_SPEAKERS_TMP_AUDIO_END,
            channel_left_right=None)

        all_speakers_presigned_url = upload_audio_file(
            input_full_local_fpath=all_speakers_converted_fpath,
            api_tmp_file_obj_key=all_speakers_object_key,
            api_token_key=pyannote_api_token)
        print(f"\nFUNC RETURN: all_speakers_presigned_url: "
              f"{all_speakers_presigned_url}\n")

        all_speakers_job_id = diarize_wav_by_object_key(
            api_tmp_file_obj_key=all_speakers_object_key,
            api_token_key=pyannote_api_token,
            speakers_number=None)
        print(f"\nFUNC RETURN: all_speakers_job_id: {all_speakers_job_id}\n")

        response_message = "Audio file was uploaded successfully [OK]"
        pyannote_api_job_ids = {
            "operator_job_id": operator_job_id,
            "caller_job_id": caller_job_id,
            "all_speakers_job_id": all_speakers_job_id}

        operator_frame_str = f"[{OPERATOR_TEMP_AUDIO_START}:{OPERATOR_TEMP_AUDIO_END}]"
        caller_frame_str = f"[{CALLER_TEMP_AUDIO_START}:{CALLER_TEMP_AUDIO_END}]"
        all_speakers_frame_str = f"[{ALL_SPEAKERS_TMP_AUDIO_START}:{ALL_SPEAKERS_TMP_AUDIO_END}]"

        json_content = {
            "message": response_message,
            "pyannote_api_job_ids": pyannote_api_job_ids,
            # "operator_job_id": operator_job_id,
            # "caller_job_id": caller_job_id,
            # "all_speakers_job_id": all_speakers_job_id,
            "operator audio frame": operator_frame_str,
            "caller audio frame": caller_frame_str,
            "all speakers audio frame": all_speakers_frame_str,
            "uploaded file content type": upload_file.content_type,
            "uploaded file name": upload_file.filename,
            "allowed file mime types": ALLOWED_FILE_MIME_TYPES,
            "allowed file extensions": ALLOWED_FILE_EXTENSIONS,
            "username": username, }

        json_response = JSONResponse(
            content=json_content,
            status_code=status.HTTP_202_ACCEPTED)

        green_color = CONSOLE_COLORS.BRIGHT_GREEN
        blue_color = CONSOLE_COLORS.BRIGHT_BLUE
        reset_color = CONSOLE_COLORS.RESET
        print(f"Response message: {response_message}\n"
              f"pyannote_api_job_ids: {green_color}{pyannote_api_job_ids}{reset_color}\n"
              f"operator_job_id: {blue_color}{operator_job_id}{reset_color}\n"
              f"caller_job_id: {blue_color}{caller_job_id}{reset_color}\n"
              f"all_speakers_job_id: {blue_color}{all_speakers_job_id}{reset_color}\n"
              f"operator audio frame: {operator_frame_str}\n"
              f"caller audio frame: {caller_frame_str}\n"
              f"all speakers audio frame: {all_speakers_frame_str}\n"
              f"operator temp audio file: {right_channel_audio_f_path}\n"
              f"caller temp audio file: {left_channel_audio_f_path}\n"
              f"all speakers temp audio: {stereo_channel_audio_f_path}\n"
              f"upload_file.content_type: {upload_file.content_type}\n"
              f"upload_file.filename: {upload_file.filename}\n"
              f"username: {username}\n")
        print("PRELIMINARY 202 RESPONSE AFTER AUDIO FILES UPLOADED")
        return json_response
    except Exception as error:
        log_text = f"Upload audio file router [ERROR]: error: {error}"
    print(log_text)
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=log_text)
