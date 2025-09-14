from . import BaseAuth
from ...exceptions import QrNotFound, InvalidAuth
from ...util import get_qr_in_page
import os
import shutil
from playwright.sync_api import Page

class LocalAuth(BaseAuth):
    """
    Handles authentication using a local WhatsApp Web session.

    Extends BaseAuth. Intended to persist session data locally so
    that QR scanning is not required on subsequent logins.
    """
    
    def __init__(self, client, dirPath: str = ".wawebpy_auth", sessionId: str = "default"):
        """
        Creates a new LocalAuth instance.
        Initializes the base class.
        """
        super().__init__(client)
        
        self._dirPath = dirPath.rstrip("/").rstrip("\\")+"/"
        self._sessionId = f'{sessionId.replace("/", "").replace("\\", "")}-session/'
    
    @property
    def filepath(self):
        return f"{self._dirPath}{self._sessionId}"
        
    def authenticate(self, clientOptions, playwright) -> Page:
        """
        Authenticate the client using a local session.
        """
        session_exists = False

        if os.path.exists(self.filepath):
            session_exists = True
        
        ctx = playwright.chromium.launch_persistent_context(
            user_data_dir=self.filepath,
            headless = clientOptions.get("headless")
        )

        if session_exists:
            return self._load_session(clientOptions=clientOptions, browser_or_ctx=ctx)
        
        
        return self._save_session(clientOptions=clientOptions, browser_or_ctx=ctx)
            
    def logout(self) -> None:
        self.client.stop()
        shutil.rmtree(self.filepath, ignore_errors=True)
    
    
    def _load_session(self, clientOptions, browser_or_ctx) -> Page:
            
        page = browser_or_ctx.new_page()
        page.goto(clientOptions.get("web_url"))
        
        try:
            get_qr_in_page(page, clientOptions.get("qr_data_selector"), 7500)
            raise InvalidAuth("Local session has expired or is invalid.")
        except QrNotFound:
            pass
        
        return page
    
    def _save_session(self, clientOptions, browser_or_ctx) -> Page:
        return self._auth_with_qr(browser_or_ctx=browser_or_ctx, clientOptions=clientOptions)