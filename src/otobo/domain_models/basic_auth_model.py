from pydantic import SecretStr

from util.safe_base_model import SafeBaseModel


class BasicAuth(SafeBaseModel):
    user_login: str
    password: SecretStr
