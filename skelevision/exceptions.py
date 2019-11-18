class IllegalLogAction(Exception):
    """Raised when an incorrect action is performed on a log (e.g.
    in a trace-to-frequency log import duplicated traces)
    """
    pass
