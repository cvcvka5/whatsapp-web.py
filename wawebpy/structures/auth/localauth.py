from .baseauth import BaseAuth
from ...exceptions import QrNotFound, SessionExpired, SessionLoadError
from ...util import get_qr_in_page
from ...logger import logger
import os
import shutil
from playwright.sync_api import Page
from playwright._impl._errors import TimeoutError as PWTimeoutError


class LocalAuth(BaseAuth):
    """
    Handles authentication using a local WhatsApp Web session.

    Extends BaseAuth. Intended to persist session data locally so
    that QR scanning is not required on subsequent logins.
    """
    
    def __init__(self, client, dirPath: str = ".wawebpy_auth", sessionId: str = "default"):
        super().__init__(client)
        self._dirPath = dirPath.rstrip("/").rstrip("\\") + "/"
        self._sessionId = f'{sessionId.replace("/", "").replace("\\", "")}-session/'

    @property
    def filepath(self):
        return f"{self._dirPath}{self._sessionId}"

    def authenticate(self, client_options, playwright) -> Page:
        logger.info("Starting LocalAuth authentication.")
        session_exists = os.path.exists(self.filepath)
        logger.debug(f"Session directory exists: {session_exists} at {self.filepath}")

        ctx = playwright.chromium.launch_persistent_context(
            user_data_dir=self.filepath,
            headless=client_options.get("headless")
        )

        if session_exists:
            logger.info("Loading existing session.")
            return self._load_session(client_options=client_options, browser_or_ctx=ctx)
        
        logger.info("No existing session found. Saving new session via QR login.")
        return self._save_session(client_options=client_options, browser_or_ctx=ctx)

    def logout(self) -> None:
        logger.info("Logging out and removing local session.")
        self.client.stop()
        shutil.rmtree(self.filepath, ignore_errors=True)
        logger.debug(f"Removed session directory: {self.filepath}")

    def _load_session(self, client_options, browser_or_ctx, max_retries: int = 3) -> Page:
        page = browser_or_ctx.new_page()
        page.goto(client_options.get("web_url"))

        retry = 0
        page_is_valid = False
        while retry <= max_retries:
            try:
                get_qr_in_page(page, client_options.get("qr_data_selector"), 5000)
                self.logout()
                logger.warning("Local session expired.")
                raise SessionExpired(f"Local session expired at {self.filepath}")
            except QrNotFound:
                logger.debug(f"No QR found, assuming session is valid. Retry {retry}.")

            try:
                page.wait_for_selector(client_options.get("loaded_selector"), timeout=5000)
                page_is_valid = True
                logger.info("Local session loaded successfully.")
                break
            except PWTimeoutError:
                logger.debug(f"Page not loaded yet, retry {retry}. Reloading.")
            
            page.reload()
            retry += 1

        if not page_is_valid:
            logger.error(f"Failed to load local session after {retry} retries.")
            raise SessionLoadError(f"Failed to load local session after {retry} retries.")

        return page

    def _save_session(self, client_options, browser_or_ctx) -> Page:
        logger.info("Authenticating via QR to save new session.")
        try:
            page = self._auth_with_qr(browser_or_ctx=browser_or_ctx, client_options=client_options)
            logger.info("New session saved successfully.")
            return page
        except Exception as e:
            logger.error(f"Failed to save session: {e}")
            raise
