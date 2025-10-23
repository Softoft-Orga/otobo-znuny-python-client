from pydantic import BaseModel, SecretStr


class SafeBaseModel(BaseModel):
    def model_dump(self, *args, with_secrets: bool = False, **kwargs):
        data = super().model_dump(*args, **kwargs)
        if with_secrets:
            for k, v in data.items():
                if isinstance(v, SecretStr):
                    data[k] = v.get_secret_value()
        return data
