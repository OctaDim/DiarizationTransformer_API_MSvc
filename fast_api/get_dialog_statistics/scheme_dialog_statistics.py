from pydantic import BaseModel


class PyannoteApiJobIds(BaseModel):
    operator_job_id: str = "f8533e6d-c8e8-44db-9b7b-8762284be390"
    caller_job_id: str = "3c8526e9-0c64-433e-8ede-00896a77cf66"
    all_speakers_job_id: str = "880ea59d-e6e1-40c4-8964-9602876b6924"

class PyannoteApiData(BaseModel):
    pyannote_api_token: str = "sk_11166286b6784130a2d669e1a1ab4333"
    # pyannote_api_token: str = "sk_0d466286b6784130a2d669e1a1ab481f"  # DEBUG ONLY, TIME LIMITED
