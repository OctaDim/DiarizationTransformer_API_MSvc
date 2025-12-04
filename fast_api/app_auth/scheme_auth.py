from pydantic import BaseModel


class AuthDataDiarize(BaseModel):
    username: str
    password: str
    # username: str = "temp_zxc"  # DEBUG ONLY
    # password: str = "temp_123"  # DEBUG ONLY
