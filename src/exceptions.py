class ClientAlreadyInitialized(Exception):
    """
    Exception thrown when attempting to initialize a Client instance
    that has already been initialized.
    """
    pass


class InvalidAuth(Exception):
    """
    Exception thrown when an invalid Auth object is provided
    to the Client during initialization.
    """
    pass


class QrNotFound(Exception):
    """
    Exception thrown when the QR code element cannot be found
    using the specified selector.
    """
    pass
