class OTOBOError(Exception):
    """
    Exception raised for errors returned by the OTOBO Webservice API.

    Attributes:
        code (str): The error code returned by OTOBO.
        message (str): A human-readable description of the error.
    """

    def __init__(self, code: str, message: str):
        """
        Initialize a new OTOBOError.

        Args:
            code (str): The error code from the API response.
            message (str): The accompanying error message.
        """
        super().__init__(f"{code}: {message}")
        self.code = code
        self.message = message
