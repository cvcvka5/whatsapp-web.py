from ...logger import logger
from playwright.sync_api import Page, Playwright

from .baseauth import BaseAuth



class NoAuth(BaseAuth):
    """
    Authentication class for QR-based login without any saved session.
    Inherits from BaseAuth and uses QR scanning for authentication.
    """
    
    def __init__(self, client):
        """Initializes NoAuth and calls BaseAuth constructor."""
        super().__init__(client)
        
    def authenticate(self, client_options, playwright: Playwright) -> Page:
        """
        Performs authentication using QR code scanning.
        
        Args:
            client_options: ClientOptions dictionary passed from the Client.
            
        Returns:
            The result of the _auth_with_qr method, which handles QR authentication.
        """
        logger.info("Starting NoAuth authentication (QR required).")
        browser = playwright.chromium.launch(headless=client_options.get("headless"))
        try:
            page = self._auth_with_qr(client_options=client_options, browser_or_ctx=browser)
            logger.info("NoAuth authentication successful, session established.")
            return page
        except Exception as e:
            logger.error("NoAuth authentication failed: %s", e)
            raise
