from . import BaseAuth


class LegacySessionAuth(BaseAuth):
    """
    Handles authentication using a legacy WhatsApp Web session.

    Extends BaseAuth. Currently a stub; authentication logic should restore
    an existing session rather than scanning a QR code.
    """
    
    def __init__(self):
        """
        Creates a new LegacySessionAuth instance.
        Initializes the base class.
        """
        super().__init__()
        
    def authenticate(self):
        """
        Authenticate the client using a legacy session.

        TODO: Implement session retrieval and validation.
        """
        pass
