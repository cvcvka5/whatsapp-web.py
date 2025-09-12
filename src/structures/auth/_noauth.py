from ._baseauth import BaseAuth


class NoAuth(BaseAuth):
    """
    Authentication class for QR-based login without any saved session.
    Inherits from BaseAuth and uses QR scanning for authentication.
    """
    
    def __init__(self):
        """Initializes NoAuth and calls BaseAuth constructor."""
        super().__init__()
        
    def authenticate(self, clientOptions):
        """
        Performs authentication using QR code scanning.
        
        Args:
            clientOptions: ClientOptions dictionary passed from the Client.
            
        Returns:
            The result of the _auth_with_qr method, which handles QR authentication.
        """
        return self._auth_with_qr(clientOptions=clientOptions)
