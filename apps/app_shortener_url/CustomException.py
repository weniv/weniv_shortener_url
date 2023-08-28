from rest_framework.exceptions import APIException


class CurrentException(APIException):
    def __init__(self, status_code: int, message: str):
        self.detail = message
        self.status_code = status_code
        super().__init__(detail=self.detail, code=self.status_code)
