#  Copyright 2015-2019 SWIM.AI inc.
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

from urllib.parse import urlparse, ParseResult


class URI:

    @staticmethod
    def normalise_warp_scheme(uri: str) -> str:
        """
        Normalise all different representations of the WARP scheme to a websocket connection.

        :param uri:             - URI to normalise.
        :return:                - URI with `ws` scheme.
        """
        uri = urlparse(uri)
        if URI.has_valid_scheme(uri):
            uri = uri._replace(scheme='ws')
            return uri.geturl()
        else:
            raise TypeError('Invalid scheme for URI!')

    @staticmethod
    def has_valid_scheme(uri: ParseResult) -> bool:
        """
        Check if a URI has a WARP compatible scheme.

        :param uri:             - URI to check.
        :return:                - True if the given URI has a scheme that is WARP compatible. False otherwise.
        """
        scheme = uri.scheme
        return scheme == 'ws' or scheme == 'warp'
