from pydantic import SecretStr

from otrs_gi_core.util.safe_base_model import SafeBaseModel


class BasicAuth(SafeBaseModel):
    user_login: str
    password: SecretStr
