"""
Exceptions used by the management classes.
"""


class SessionException(Exception):
    """
    Dummy class for session errors

    .. class:: SessionException
    """

    pass


class InvalidCredentialsException(Exception):
    """
    Dummy class for invalid credentials

    .. class:: InvalidCredentialsException
    """

    pass


class APILevelNotSupportedException(Exception):
    """
    Dummy class for unsupported API levels

    .. class:: APILevelNotSupportedException
    """

    pass


class UnsupportedRequestException(Exception):
    """
    Dummy class for unsupported requests

    .. class:: UnsupportedRequest
    """

    pass


class InvalidHostnameFormatException(Exception):
    """
    Dummy class for invalid hostname formats (non-FQDN)

    .. class:: InvalidHostnameFormatException
    """

    pass


class UnsupportedFilterException(Exception):
    """
    Dummy class for unsupported filters

    .. class:: UnsupportedFilterException
    """

    pass


class EmptySetException(Exception):
    """
    Dummy class for empty result sets

    .. class:: EmptySetException
    """

    pass


class SnapshotExistsException(Exception):
    """
    Dummy class for existing snapshots

    .. class:: SnapshotExistsException
    """

    pass