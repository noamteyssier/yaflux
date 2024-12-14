class YaxMissingResultError(Exception):
    """Raised when a result is missing from the results object."""


class YaxMissingResultFileError(Exception):
    """Raised when a result file is missing from the tarfile."""


class YaxMissingVersionFileError(Exception):
    """Raised when the version file is missing from the tarfile."""


class YaxMissingParametersFileError(Exception):
    """Raised when the parameters file is missing from the tarfile."""


class YaxNotArchiveFileError(Exception):
    """Raised when the file is not a yax archive."""
