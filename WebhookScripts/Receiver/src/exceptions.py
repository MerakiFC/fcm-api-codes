
class HTTPRequestExceptionError(Exception):
    """ Raises this if response code is not 200"""

class ConverterExceptionError(Exception):
    """ Raises this if there's conversion errors"""


class InvalidPayloadExceptionError(Exception):
    """ Raises this if there's Payload errors"""
