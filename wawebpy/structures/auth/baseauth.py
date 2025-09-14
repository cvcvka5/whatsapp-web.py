from abc import ABC, abstractmethod
from playwright._impl._errors import TimeoutError as PWTimeoutError
from wawebpy.exceptions import QrNotFound
from playwright.sync_api import Page
from ...util import get_qr_in_page



class BaseAuth(ABC):
    def __init__(self, client):
        """
        Base class for authentication methods.
        Holds a reference to the client instance.
        """
        self.client = client
    
    @abstractmethod
    def authenticate(self, clientOptions, playwright):
        """
        Abstract method that must be implemented by subclasses
        to perform the actual authentication.
        """
        pass

    def _auth_with_qr(self, browser_or_ctx, clientOptions) -> Page:
        """
        Handles QR-based authentication for WhatsApp Web.

        Continuously checks for the QR code, emits it when it changes,
        and waits for the main WhatsApp interface to load. Retries
        a limited number of times if the QR is not found.

        Args:
            clientOptions: Dictionary of client options including selectors.
        """
        qr = None  # Store the last QR code to detect changes

            
        page = browser_or_ctx.new_page()
        page.goto(clientOptions.get("web_url"))
        retry = 0
        max_retries = 12
        while retry < max_retries:
            try:
                # Try to get the current QR code from the page
                current_qr = get_qr_in_page(page=page,
                                            qr_data_selector=clientOptions.get("qr_data_selector"))
                retry = 0  # Reset retry counter on success
            except QrNotFound as exc:
                retry += 1  # Increment retry counter if QR is not found
                
                if retry >= max_retries:
                    raise exc  # Give up after exceeding max retries

                current_qr = None  # No QR available this iteration
            
            # Emit QR only if it exists and has changed since last emission
            if current_qr is not None and (qr is None or qr.data_list[0].data != current_qr.data_list[0].data):
                self.client.emit("qr", current_qr)
                qr = current_qr

            # Check if the main WhatsApp interface has loaded
            try:
                if current_qr is None:
                    # Wait for the WhatsApp chats interface to appear
                    page.wait_for_selector("span[aria-label=WhatsApp]", timeout=1000)
                    break  # Chats loaded, exit loop
            except PWTimeoutError:
                # Page not loaded yet, continue checking
                pass
        
        return page