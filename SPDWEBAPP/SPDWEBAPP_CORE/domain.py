"""Shared failure contract for rejected state transitions across business domains."""


class Conflict(Exception):
    """The resource changed or its current state does not permit this operation."""
