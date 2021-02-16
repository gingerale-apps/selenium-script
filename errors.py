"""Own exceptions for newauction script."""


class DatabaseError(Exception):
    """Used when there are no selected lots for creation or auction start time has been passed in database."""
    pass


class CreationError(Exception):
    """Used when lot is not created."""
    pass
