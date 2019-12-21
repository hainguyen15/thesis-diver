# pylint: disable=no-member
import re
from email.utils import parseaddr
from rest_framework.exceptions import MethodNotAllowed

from .constants import (
    MSG_EMAIL_INVALID,
    MSG_EMAIL_NOT_EMPTY,
    MSG_USER_NOT_EMPTY,
    MSG_USERNAME_SHORT,
    STC_MIN_LEN_USERNAME
)

def validate_username(username):
    if username is None or len(username) == 0:
        return False, MSG_USER_NOT_EMPTY
    if len(username) < STC_MIN_LEN_USERNAME:
        return False, MSG_USERNAME_SHORT
    return True, None

def validate_email(email):
    if email is None or len(email) == 0:
        return False, MSG_EMAIL_NOT_EMPTY
    if parseaddr(email)[1] == '':
        #email is invalid
        return False, MSG_EMAIL_INVALID
    return True, None

class MethodSerializerView(object):
    '''
    Utility class for get different serializer class by method.
    For example:
    method_serializer_classes = {
        ('GET', ): MyModelListViewSerializer,
        ('PUT', 'PATCH'): MyModelCreateUpdateSerializer
    }
    '''
    method_serializer_classes = None

    def get_serializer_class(self):
        assert self.method_serializer_classes is not None, (
            f'Expected view {self.__class__.__name__} should contain method_serializer_classes '
            'to get right serializer class.' 
        )
        for methods, serializer_cls in self.method_serializer_classes.items():
            if self.request.method in methods:
                return serializer_cls

        raise MethodNotAllowed(self.request.method)
