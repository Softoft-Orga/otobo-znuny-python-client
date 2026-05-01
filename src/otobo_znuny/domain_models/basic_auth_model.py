from pydantic import SecretStr

from otobo_znuny.util.safe_base_model import SafeBaseModel


class BasicAuth(SafeBaseModel):
    user_login: str
    password: SecretStr
