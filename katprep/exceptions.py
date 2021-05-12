"""
Exceptions used by the management classes
"""


class SessionException(Exception):
    """
    Dummy class for session errors

    .. class:: SessionException
    """


class InvalidCredentialsException(Exception):
    """
    Dummy class for invalid credentials

    .. class:: InvalidCredentialsException
    """


class APILevelNotSupportedException(Exception):
    """
    Dummy class for unsupported API levels

    .. class:: APILevelNotSupportedException
    """


class UnsupportedRequestException(Exception):
    """
    Dummy class for unsupported requests

    .. class:: UnsupportedRequest
    """


class InvalidHostnameFormatException(Exception):
    """
    Dummy class for invalid hostname formats (non-FQDN)

    .. class:: InvalidHostnameFormatException
    """


class UnsupportedFilterException(Exception):
    """
    Dummy class for unsupported filters

    .. class:: UnsupportedFilterException
    """


class EmptySetException(Exception):
    """
    Dummy class for empty result sets

    .. class:: EmptySetException
    """


class SnapshotExistsException(Exception):
    """
    Dummy class for existing snapshots

    .. class:: SnapshotExistsException
    """

class UnauthenticatedError(RuntimeError):
    """
    Exception for showing that a client wasn't able to authenticate itself
    """

class SSLCertVerificationError(Exception):
    """
    Exception for invalid SSL certificates
.. class:: SSLCertVerificationError
    """
    pass
