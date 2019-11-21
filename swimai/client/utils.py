from urllib.parse import urlparse


class URI:

    @staticmethod
    def normalise_scheme(uri):
        uri = urlparse(uri)
        if URI.has_valid_scheme(uri):
            uri = uri._replace(scheme='ws')
            return uri.geturl()
        else:
            raise TypeError('Invalid scheme for URI!')

    @staticmethod
    def has_valid_scheme(uri):
        scheme = uri.scheme
        return scheme == 'ws' or scheme == 'warp'
