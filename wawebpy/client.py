from .structures.auth.baseauth import BaseAuth
from .structures.auth.noauth import NoAuth
from .structures.message import Message
from .structures.eventemitter import EventEmitter
from .structures.clientoptions import ClientOptions
from .structures.contact import Contact
from .structures.group import Group
from .logger import logger
from .exceptions import (
    ClientAlreadyInitialized,
    InvalidAuth,
    ClientInitError,
    ClientStopError,
    SettingStatusError,
    GettingChatError,
)
from qrcode import QRCode
from .util import get_module_script
from typing import overload, Literal, Callable, Union
from playwright.sync_api import sync_playwright, Playwright, Page


class Client(EventEmitter):
    """Main client class for interacting with WhatsApp Web via Playwright."""

    def __init__(self):
        """
        Initializes the Client instance with pre-initialization placeholders
        for Playwright objects and sets initialized flag to False.
        """
        # Pre Initialization
        self._initialized: bool = False
        self._playwright: Playwright = None
        self._page: Page = None

        logger.debug("Client instance created (not initialized yet).")

        # During Initialization
        super().__init__()

    @overload
    def on(self, event_name: Literal["message"], callback: Callable[[Message], None]) -> None: ...
    @overload
    def on(self, event_name: Literal["qr"], callback: Callable[[QRCode], None]) -> None: ...
    @overload
    def on(self, event_name: Literal["connection"], callback: Callable[[], None]) -> None: ...

    def on(self, event_name: str, callback: Callable[[], None]) -> None:
        """
        Registers an event listener for the client.
        """
        logger.debug(f"Registered event listener for '{event_name}'.")
        return super().on(event_name=event_name, callback=callback)

    @property
    def initialized(self):
        """Returns True if the client has been initialized, False otherwise."""
        return self._initialized

    def initialize(self, options: ClientOptions):
        """
        Initializes the client, starts Playwright, opens a browser page,
        and triggers the authentication method.
        """
        if self.initialized:
            logger.error("Attempted to initialize an already initialized client.")
            raise ClientAlreadyInitialized("You try to initialize a Client that's already initialized.")

        logger.info("Initializing client...")

        options.setdefault("auth", NoAuth(client=self))
        options["auth"].client = self

        if not isinstance(options.get("auth"), BaseAuth):
            logger.error("Invalid Auth object passed to Client.")
            raise InvalidAuth("Invalid Auth object passed to Client object.")

        options.setdefault("headless", True)
        options.setdefault("web_url", "https://web.whatsapp.com/")
        options.setdefault("qr_data_selector", "div[data-ref]")
        options.setdefault("loaded_selector", "span[aria-label=WhatsApp]")

        self._initialized = True
        try:
            logger.debug("Starting Playwright...")
            self._playwright = sync_playwright().start()
            logger.info("Playwright started successfully.")
        except Exception as e:
            self._initialized = False
            logger.exception("Failed to start Playwright.")
            raise ClientInitError("Failed to start Playwright: " + str(e))

        try:
            logger.debug("Authenticating client...")
            self._page = options.get("auth").authenticate(
                client_options=options, playwright=self._playwright
            )
            self._page.wait_for_load_state("networkidle")
            logger.info("Client authenticated and page loaded.")
            self.emit("ready")
        except Exception as e:
            logger.exception("Authentication failed.")
            self._initialized = False
            raise ClientInitError("Authentication failed: " + str(e))

    def set_status(self, status: str) -> bool:
        logger.debug(f"Setting status to: {status}")
        script = get_module_script("WAWebContactStatusBridge", "setMyStatus", (f"'{status}'",))

        try:
            result = self._page.evaluate(script)
            logger.debug(f"Set status result: {result}")
            if not isinstance(result, dict) or "status" not in result:
                logger.warning("Unexpected result when setting status.")
                return False
            success = result["status"] == 200
            if success:
                logger.info(f"Status updated successfully: {status}")
            else:
                logger.warning(f"Status update failed with code: {result['status']}")
            return success
        except Exception as e:
            logger.exception("Failed to set status.")
            raise SettingStatusError("Failed to set status: " + str(e))

    def get_contact(self, jid: str) -> Union[Contact, None]:
        logger.debug(f"Fetching contact: {jid}")
        try:
            contact = Contact.get(self._page, jid)
            logger.info(f"Contact fetched: {jid}")
            return contact
        except Exception as e:
            logger.exception(f"Error fetching contact {jid}.")
            raise GettingChatError(f"Failed to get Contact {jid}: {str(e)}")

    def get_group(self, jid: str) -> Union[Group, None]:
        logger.debug(f"Fetching group: {jid}")
        try:
            group = Group.get(self._page, jid)
            logger.info(f"Group fetched: {jid}")
            return group
        except Exception as e:
            logger.exception(f"Error fetching group {jid}.")
            raise GettingChatError(f"Failed to get Group {jid}: {str(e)}")

    def stop(self):
        """
        Stops the client by closing the Playwright page, browser, and stopping Playwright.
        """
        logger.info("Stopping client...")
        try:
            if self._page:
                logger.debug("Closing page...")
                self._page.close()
                logger.debug("Page closed.")
        except Exception as e:
            logger.exception("Error closing page.")
            raise ClientStopError(f"Error closing page: {str(e)}")

        try:
            if self._playwright:
                logger.debug("Stopping Playwright...")
                self._playwright.stop()
                logger.debug("Playwright stopped.")
        except Exception as e:
            logger.exception("Error stopping Playwright.")
            raise ClientStopError(f"Error stopping Playwright: {str(e)}")
        finally:
            self._initialized = False
            logger.info("Client stopped and de-initialized.")


__all__ = ["Client"]