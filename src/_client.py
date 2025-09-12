from .structures.auth import NoAuth, LegacySessionAuth, LocalAuth, BaseAuth
from .structures import Message, EventEmitter
from .exceptions import ClientAlreadyInitialized, InvalidAuth, QrNotFound
from typing import overload, Literal, Callable, TypedDict
from playwright.sync_api import sync_playwright, Playwright, Browser, Page
from playwright._impl._errors import TimeoutError as PWTimeoutError
import qrcode

class ClientOptions(TypedDict):
    """
    TypedDict for client configuration options.
    
    Attributes:
        auth: Authentication method (NoAuth, LegacySessionAuth, LocalAuth)
        headless: Whether to run browser in headless mode
        web_url: URL of WhatsApp Web
        qr_data_selector: CSS selector for the QR code data element
    """
    auth: NoAuth | LegacySessionAuth | LocalAuth
    headless: bool
    web_url: str
    qr_data_selector: str


class Client(EventEmitter):
    """Main client class for interacting with WhatsApp Web via Playwright."""
    
    def __init__(self):
        """
        Initializes the Client instance with pre-initialization placeholders
        for Playwright objects and sets initialized flag to False.
        """
        # Pre Initialization
        self._initialized = False
        self._pwright: Playwright = None
        self._browser: Browser = None
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
        
        options.setdefault("auth", NoAuth())
        options["auth"].client = self
    
        if not isinstance(options.get("auth"), BaseAuth): 
            raise InvalidAuth("Invalid Auth object passed to Client object.")
    
        options.setdefault("headless", True)
        options.setdefault("web_url", "https://web.whatsapp.com/")
        options.setdefault("qr_data_selector", "div[data-ref]")
        
        # Set initialized flag and start Playwright browser
        self._initialized = True
        self._pwright = sync_playwright().start()
        self._browser = self._pwright.chromium.launch(headless=False)
        self._page = self._browser.new_page()
        
        # Trigger authentication
        options.get("auth").authenticate(clientOptions=options)    
        
    
    def _get_qr(self, options: ClientOptions, timeout: int = 5000) -> qrcode.QRCode:
        """
        Retrieves the current QR code from WhatsApp Web and returns a QRCode object.
        
        Args:
            options: ClientOptions containing the QR data selector
            timeout: Maximum time to wait for the QR element (milliseconds)
            
        Returns:
            qrcode.QRCode: QR code object representing the current QR
        
        Raises:
            QrNotFound: If the QR code element is not found within the timeout
        """
        if self._page.url != options.get("web_url"):
            self._page.goto(options.get("web_url"))
            
        try:
            qr_data_div = self._page.wait_for_selector(options.get("qr_data_selector"), timeout=timeout)
            qr_data = qr_data_div.get_attribute("data-ref")
        except PWTimeoutError:
            raise QrNotFound(f"QR code couldn't be found with selector '{options.get('qr_data_selector')}'.")
        
        qr = qrcode.QRCode(
            version=None,
            error_correction=qrcode.ERROR_CORRECT_M,
            box_size=1,
            border=0
        )
        qr.add_data(qr_data)
        qr.make(fit=True)
        return qr
        
    def stop(self):
        """
        Stops the client by closing the Playwright page, browser, and stopping Playwright.
        Resets the initialized flag to False.
        """
        self._page.close()
        self._browser.close()
        self._pwright.stop()
        self._initialized = False
        
        
__all__ = ["Client"]