# pip install pyannote.audio

import os
from os import PathLike
from typing import Literal, Union

import huggingface_hub
import torch
import torchaudio
import transformers
from huggingface_hub import login
from pyannote.audio import Pipeline
from pyannote.audio.pipelines.utils.hook import ProgressHook
from pyannote.pipeline.typing import PipelineOutput
from pydub import AudioSegment

transformers.logging.set_verbosity_debug()  # Transformers logging switching on
huggingface_hub.logging.set_verbosity_debug()  # HF logging switching on

hf_token = "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"
api_token = "sk_0d466286b6784130a2d669e1a1ab481f"
login(token=hf_token)


def normalize_file_path(file_path: str):
    full_file_name_path = file_path.replace("\\", "/")  # for Windows, for Linux not necessary
    full_file_name_path = os.path.normpath(path=full_file_name_path)
    print(f"full_file_name_path: {full_file_name_path}")
    return full_file_name_path


def convert_audio_ogg_to_wav(
        from_ogg_file_path: Union[str, PathLike],
        to_wav_file_path: Union[str, PathLike],
        start_time_msec=None,
        end_time_msec=None,
        channel_left_right: Union[None, Literal["left", "right"]]=None
) -> str|PathLike:
    """Convert .ogg to .wav
    :param from_ogg_file_path: str or PathLike: full .ogg file path including filename with extension
    :param to_wav_file_path: str or PathLike: full .wav file path including filename with extension
    :param start_time_msec: int: e.g. 7000. Converted file starts from 7 sec
    :param end_time_msec: int: e.g. 60000. Converted file ends in 1 min
    :param channel_left_right: None|Literal["left", "right"]: only left or right channel
    :return: None (save .wav file into outgoing_audio_file_path path)"""
    audio = AudioSegment.from_ogg(from_ogg_file_path)
    audio = audio[start_time_msec:end_time_msec]

    if audio.channels == 2:
        if channel_left_right == "left":
            audio = audio.split_to_mono()[0]
        elif channel_left_right == "right":
            audio = audio.split_to_mono()[1]

    audio = audio.set_frame_rate(16000).set_channels(1)
    audio.export(to_wav_file_path, format="wav")
    print(f"Converted [OK]: \n"
          f"from_audio_file_path: {from_ogg_file_path}\n"
          f"outgoing_audio_file_path: {to_wav_file_path}\n")
    return to_wav_file_path


def diarize_wav_audio(
        full_wav_file_path: Union[str, PathLike],
        model_checkpoint: Union[str, Literal[
            "pyannote/speaker-diarization-3.1",
            "pyannote/speaker-diarization-community-1"]] = "pyannote/speaker-diarization-3.1",
        device_type: Union[str, Literal["cpu", "cuda"]] = "cuda",
        num_speakers: int = 2,
        use_torchaudio_load: bool = True
) -> PipelineOutput:
    print(f"full_wav_file_path {full_wav_file_path}\n")

    try:
        print(111)
        pipeline = Pipeline.from_pretrained(
            checkpoint=model_checkpoint,
            token=hf_token, )
        print(f"Pipeline.from_pretrained(): {pipeline}")
        print(222)
        pipeline = pipeline.to(torch.device(device_type))
        print(f"pipeline.to(torch.device(device_type): {pipeline}\n")
        print(333)

        if not use_torchaudio_load:
            print(444)
            model_output = pipeline(file=full_wav_file_path,
                                    num_speakers=num_speakers)
            print("444-1")
            with ProgressHook() as progress_hook:
                print("444-2")
                model_output = pipeline(file=full_wav_file_path,
                                        num_speakers=num_speakers,
                                        hook=progress_hook)
                print("444-3")
            print("444-4")
        else:
            print("555")
            waveform, sample_rate = torchaudio.load(
                uri=full_wav_file_path)
            print("555-1")
            model_output = pipeline({"waveform": waveform,
                                     "sample_rate": sample_rate})
            print("555-2")

        print(f"diarizing process [OK]:\n"
              f"model_output: {model_output}\n")
        print(666)
        return model_output
    except Exception as error:
        print(f"diarizing process [ERROR]: error: {error}\n"
              f"full_wav_file_path: {full_wav_file_path}\n"
              f"model_checkpoint: {model_checkpoint}\n"
              f"device_type: {device_type}\n"
              f"use_torchaudio_load: {use_torchaudio_load}\n")


ogg_full_fpath = r"/home/octadim/PycharmProjects/DiarizationTransformer_API_MSvc/audio_samples/ogg/1.ogg"
wav_full_fpath = r"/home/octadim/PycharmProjects/DiarizationTransformer_API_MSvc/audio_samples/wav/1.wav"
ogg_full_fpath = normalize_file_path(ogg_full_fpath)
wav_full_fpath = normalize_file_path(wav_full_fpath)

converted_wav_fpath = convert_audio_ogg_to_wav(
    from_ogg_file_path=ogg_full_fpath,
    to_wav_file_path=wav_full_fpath,
    start_time_msec=None,
    end_time_msec=None,
    channel_left_right=None)

# ######################################################################
# ############# pyannote model "speaker-diarization-3.1" ###############
# ######################################################################
print(f"\n\n{'#' * 75}")
print("PYANNOTE LOCAL MODEL: 'speaker-diarization-3.1'")
print(f"{'#' * 75}")

model_checkpoint = "pyannote/speaker-diarization-3.1"
device_name = "cuda" if torch.cuda.is_available() else "cpu"

output_model_diarization_3_1 = diarize_wav_audio(
    full_wav_file_path=converted_wav_fpath,  # WAV
    # full_wav_file_path=ogg_full_fpath,  # OGG
    model_checkpoint=model_checkpoint,
    device_type=device_name,  # "cuda" or "cpu"
    num_speakers=2,
    use_torchaudio_load=False)
print(f"output_model_diarization_3_1: "
      f"{output_model_diarization_3_1}\n")

######################################################################
########## pyannote model "speaker-diarization-community-1" ##########
######################################################################
print(f"\n\n{'#' * 75}")
print("PYANNOTE LOCAL MODEL: 'speaker-diarization-community-1'")
print(f"{'#' * 75}")

model_checkpoint = "pyannote/speaker-diarization-community-1"
device_name = "cuda" if torch.cuda.is_available() else "cpu"

output_model_community_1 = diarize_wav_audio(
    full_wav_file_path=converted_wav_fpath,  # WAV
    # full_wav_file_path=ogg_full_fpath,  # OGG
    model_checkpoint=model_checkpoint,
    device_type=device_name,  # "cuda" or "cpu"
    num_speakers=2,
    use_torchaudio_load=False)
print(f"output_model_community_1: "
      f"{output_model_community_1}\n")
