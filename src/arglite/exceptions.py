class ParseError(Exception):
    """Raised when CLI arguments cannot be parsed correctly."""


class RequirementError(Exception):
    """Raised when a required argument is missing."""
