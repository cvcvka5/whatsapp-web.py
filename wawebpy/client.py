from .structures.auth.baseauth import BaseAuth
from .structures.auth.noauth import NoAuth
from .structures.message import Message
from .structures.eventemitter import EventEmitter
from .structures.clientoptions import ClientOptions
from .structures.contact import Contact
from .structures.group import Group
from .exceptions import ClientAlreadyInitialized, InvalidAuth
from .util import get_module_script
from typing import overload, Literal, Callable
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
        
        # During Initialization
        super().__init__()
        
    @overload
    def on(self, event_name: Literal["message"], callback: Callable[[Message], None]) -> None: ...
    
    @overload
    def on(self, event_name: Literal["qr"], callback: Callable[[str], None]) -> None: ...
    
    @overload
    def on(self, event_name: Literal["connection"], callback: Callable[[], None]) -> None: ...
    
    def on(self, event_name: str, callback: Callable[[], None]) -> None:
        """
        Registers an event listener for the client.
        
        Args:
            event_name: Name of the event ("message", "qr", or "connection")
            callback: Function to call when the event occurs
        """
        return super().on(event_name=event_name, callback=callback)
    
    @property
    def initialized(self):
        """Returns True if the client has been initialized, False otherwise."""
        return self._initialized
    
    def initialize(self, options: ClientOptions):
        """
        Initializes the client, starts Playwright, opens a browser page,
        and triggers the authentication method.
        
        Args:
            options: ClientOptions containing auth method, headless flag, etc.
            
        Raises:
            ClientAlreadyInitialized: If initialize is called on an already initialized client
            InvalidAuth: If the provided auth object is not a subclass of BaseAuth
        """
        if self.initialized: 
            raise ClientAlreadyInitialized("You try to initialize a Client that's already initialized.")
        
        options.setdefault("auth", NoAuth(client=self))
        options["auth"].client = self
    
        if not isinstance(options.get("auth"), BaseAuth): 
            raise InvalidAuth("Invalid Auth object passed to Client object.")
    
        options.setdefault("headless", True)
        options.setdefault("web_url", "https://web.whatsapp.com/")
        options.setdefault("qr_data_selector", "div[data-ref]")
        options.setdefault("loaded_selector", "span[aria-label=WhatsApp]")
        
        # Set initialized flag and start Playwright browser
        self._initialized = True
        self._playwright = sync_playwright().start()
        
        # Trigger authentication
        self._page = options.get("auth").authenticate(client_options=options, playwright=self._playwright)    
        self._page.wait_for_load_state("networkidle")
        self.emit("ready")
        
    def set_status(self, status: str) -> bool:
        script = get_module_script("WAWebContactStatusBridge", "setMyStatus", (f"'{status}'", ))
        status = self._page.evaluate(script)["status"]

        return status == 200
        
    def get_contact(self, jid: str) -> Contact:
        return Contact.get(self._page, jid)
    
    def get_group(self, jid: str) -> Group:
        return Group.get(self._page, jid)


    def stop(self):
        """
        Stops the client by closing the Playwright page, browser, and stopping Playwright.
        Resets the initialized flag to False.
        """
        if self._page:
            self._page.close()
        if self._playwright:
            self._playwright.stop()
            
        self._initialized = False
        
        
__all__ = ["Client"]