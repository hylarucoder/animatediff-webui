from fastapi import HTTPException


class ApiException(HTTPException):
    def __init__(self, message: str, code=400):
        self.status_code = code
        self.detail = message


def raise_if(
        condition: bool,
        message: str,
):
    if condition:
        raise ApiException(message)


def raise_unless(
        condition: bool,
        message: str,
):
    if not condition:
        raise ApiException(message)
