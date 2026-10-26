"""Translate domain failures at the REST boundary without leaking exception internals."""
from django.core.exceptions import ValidationError
from django.db import OperationalError, IntegrityError
from rest_framework.response import Response
from rest_framework.views import exception_handler
from SPDWEBAPP_CORE.domain import Conflict


def domain_exception_handler(exc, context):
    if isinstance(exc, ValidationError):
        errors = exc.message_dict if hasattr(exc, 'message_dict') else {'detail': exc.messages}
        return Response(errors, status=400)
    if isinstance(exc, (OperationalError, IntegrityError)):
        return Response({'detail': 'The data could not be saved. Refresh to check its state before retrying.'}, status=409)
    if isinstance(exc, Conflict):
        return Response({'detail': str(exc)}, status=409)
    return exception_handler(exc, context)
