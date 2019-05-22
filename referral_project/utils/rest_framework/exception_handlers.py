from django.core.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST
from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if isinstance(exc, ValidationError):
        if response is None:
            response = Response()
        response.data = {'detail': exc.message_dict['__all__']}
        response.status_code = HTTP_400_BAD_REQUEST

    return response
