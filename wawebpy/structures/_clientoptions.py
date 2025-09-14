from typing import TypedDict, Union
class ClientOptions(TypedDict):
    """
    TypedDict for client configuration options.
    
    Attributes:
        auth: Authentication method (NoAuth, LegacySessionAuth, LocalAuth)
        headless: Whether to run browser in headless mode
        web_url: URL of WhatsApp Web
        qr_data_selector: CSS selector for the QR code data element
    """
    auth: Union['NoAuth', 'LegacySessionAuth', 'LocalAuth']
    headless: bool
    web_url: str
    qr_data_selector: str
