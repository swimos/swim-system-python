#  Copyright 2015-2020 SWIM.AI inc.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import sys
from typing import Callable
from urllib.parse import urlparse, ParseResult


def after_started(function: 'Callable') -> 'Callable':
    """
    Decorator that allows for a given client method to be executed only after the client has been started.
    The client should have an `has_started` flag set to True.

    :param function:        - Decorated client method.
    :return:                - The return value of the decorated client method.
    """

    def wrapper(*args, **kwargs):
        if args[0]._has_started:
            return function(*args, **kwargs)
        else:
            try:
                raise Exception(f'Cannot execute "{args[1].__name__}" before the client has been started!')
            except Exception:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                args[0]._handle_exception(exc_value, exc_traceback)

    return wrapper


class _URI:

    @staticmethod
    def _normalise_warp_scheme(uri: str) -> str:
        """
        Normalise all different representations of the WARP scheme to a websocket connection.

        :param uri:             - URI to normalise.
        :return:                - URI with `ws` scheme.
        """
        uri = urlparse(uri)
        if _URI._has_valid_scheme(uri):
            uri = uri._replace(scheme='ws')
            return uri.geturl()
        else:
            raise TypeError(f'Invalid scheme "{uri.scheme}" for Warp URI!')

    @staticmethod
    def _has_valid_scheme(uri: ParseResult) -> bool:
        """
        Check if a URI has a WARP compatible scheme.

        :param uri:             - URI to check.
        :return:                - True if the given URI has a scheme that is WARP compatible. False otherwise.
        """
        scheme = uri.scheme
        return scheme == 'ws' or scheme == 'warp'
