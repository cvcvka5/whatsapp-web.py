from .baseauth import BaseAuth
from playwright.sync_api import Page, Playwright


class NoAuth(BaseAuth):
    """
    Authentication class for QR-based login without any saved session.
    Inherits from BaseAuth and uses QR scanning for authentication.
    """
    
    def __init__(self, client):
        """Initializes NoAuth and calls BaseAuth constructor."""
        super().__init__(client)
        
    def authenticate(self, clientOptions, playwright: Playwright) -> Page:
        """
        Performs authentication using QR code scanning.
        
        Args:
            clientOptions: ClientOptions dictionary passed from the Client.
            
        Returns:
            The result of the _auth_with_qr method, which handles QR authentication.
        """
        browser = playwright.chromium.launch(headless=clientOptions.get("headless"))
        return self._auth_with_qr(clientOptions=clientOptions, browser=browser)
