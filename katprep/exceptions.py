"""
Exceptions used by the management classes
"""


class SessionException(Exception):
    """
    Exception for session errors

    .. class:: SessionException
    """


class InvalidCredentialsException(Exception):
    """
    Exception for invalid credentials

    .. class:: InvalidCredentialsException
    """


class APILevelNotSupportedException(Exception):
    """
    Exception for unsupported API levels

    .. class:: APILevelNotSupportedException
    """


class UnsupportedRequestException(Exception):
    """
    Exception for unsupported requests

    .. class:: UnsupportedRequest
    """


class InvalidHostnameFormatException(Exception):
    """
    Exception for invalid hostname formats (non-FQDN)

    .. class:: InvalidHostnameFormatException
    """


class UnsupportedFilterException(Exception):
    """
    Exception for unsupported filters

    .. class:: UnsupportedFilterException
    """


class EmptySetException(Exception):
    """
    Exception for empty result sets

    .. class:: EmptySetException
    """


class SnapshotExistsException(Exception):
    """
    Exception for already existing snapshots

    .. class:: SnapshotExistsException
    """

class UnauthenticatedError(RuntimeError):
    """
    Exception for showing that a client wasn't able to authenticate itself

    .. class:: UnauthenticatedError
    """

class SSLCertVerificationError(Exception):
    """
    Exception for invalid SSL certificates

    .. class:: SSLCertVerificationError
    """
