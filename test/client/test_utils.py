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

import unittest
from urllib.parse import urlparse

from swimai.client._utils import _URI


class TestUtils(unittest.TestCase):

    def test_uri_scheme_valid_ws(self):
        # Given
        uri = 'ws://foo_bar:9000'
        uri = urlparse(uri)
        # When
        actual = _URI._has_valid_scheme(uri)
        # Then
        self.assertTrue(actual)

    def test_uri_scheme_valid_warp(self):
        # Given
        uri = 'warp://foo_bar:9000'
        uri = urlparse(uri)
        # When
        actual = _URI._has_valid_scheme(uri)
        # Then
        self.assertTrue(actual)

    def test_uri_scheme_invalid_empty(self):
        # Given
        uri = 'foo_bar:9000'
        uri = urlparse(uri)
        # When
        actual = _URI._has_valid_scheme(uri)
        # Then
        self.assertFalse(actual)

    def test_uri_scheme_invalid_http(self):
        # Given
        uri = 'carp://foo_bar:9000'
        uri = urlparse(uri)
        # When
        actual = _URI._has_valid_scheme(uri)
        # Then
        self.assertFalse(actual)

    def test_normalise_warp_scheme_ws(self):
        # Given
        uri = 'ws://foo_bar:9000'
        expected = 'ws://foo_bar:9000'
        # When
        actual = _URI._normalise_warp_scheme(uri)
        # Then
        self.assertEqual(expected, actual)

    def test_normalise_warp_scheme_warp(self):
        # Given
        uri = 'warp://foo_bar:9000'
        expected = 'ws://foo_bar:9000'
        # When
        actual = _URI._normalise_warp_scheme(uri)
        # Then
        self.assertEqual(expected, actual)

    def test_normalise_warp_scheme_invalid(self):
        # Given
        uri = 'carp://foo_bar:9000'
        # When
        with self.assertRaises(TypeError) as error:
            _URI._normalise_warp_scheme(uri)
        # Then
        message = error.exception.args[0]
        self.assertEqual('Invalid scheme "carp" for Warp URI!', message)
