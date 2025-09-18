class ClientAlreadyInitialized(Exception):
    """Raised when initializing an already initialized Client."""
    pass

class InvalidAuth(Exception):
    """Raised when the provided Auth object is invalid."""
    pass

class QrNotFound(Exception):
    """Raised when the QR code element is not found."""
    pass

class ClientInitError(Exception):
    """Raised when Client initialization fails."""
    pass

class ClientStopError(Exception):
    """Raised when stopping the Client fails."""
    pass

class SettingStatusError(Exception):
    """Raised when setting status fails."""
    pass

class GettingChatError(Exception):
    """Raised when getting Chat fails."""
    pass

class ContactNotFound(Exception):
    """Raised when the contact with the given JID cannot be found."""
    pass

class ProfilePictureNotFound(Exception):
    """Raised when the contact has no profile picture."""
    pass

class StatusFetchError(Exception):
    """Raised when fetching the contact status fails."""
    pass

class WidFetchError(Exception):
    """Raised when fetching the contact phone number fails."""
    pass

class GroupNotFound(Exception):
    """Raised when a group cannot be found or fetched."""
    pass

class FetchGroupMetadataError(Exception):
    """Raised when fetching the group metadata fails."""
    pass

class SessionExpired(InvalidAuth):
    """Raised when the local session has expired (QR detected)."""
    pass

class SessionLoadError(InvalidAuth):
    """Raised when session could not be loaded after retries."""
    pass