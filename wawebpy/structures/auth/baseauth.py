from ...logger import logger
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
    def authenticate(self, client_options, playwright):
        """
        Abstract method that must be implemented by subclasses
        to perform the actual authentication.
        """
        pass

    def _auth_with_qr(self, browser_or_ctx, client_options, max_retries: int = 5) -> Page:
        """
        Handles QR-based authentication for WhatsApp Web.

        Continuously checks for the QR code, emits it when it changes,
        and waits for the main WhatsApp interface to load. Retries
        a limited number of times if the QR is not found.

        Args:
            client_options: Dictionary of client options including selectors.
        """
        qr = None  # Store the last QR code to detect changes
        page = browser_or_ctx.new_page()
        logger.info("Opening WhatsApp Web at %s", client_options.get("web_url"))
        page.goto(client_options.get("web_url"))

        retry = 0
        while retry <= max_retries:
            try:
                # Try to get the current QR code from the page
                current_qr = get_qr_in_page(
                    page=page,
                    qr_data_selector=client_options.get("qr_data_selector"),
                    timeout=5000,
                )
                logger.debug("QR code successfully retrieved.")
                retry = 0  # Reset retry counter on success
            except QrNotFound as exc:
                retry += 1
                logger.warning(
                    "QR code not found (attempt %d/%d) at %s",
                    retry, max_retries, page.url,
                )

                if retry >= max_retries:
                    logger.error(
                        "Failed to find QR code after %d retries on %s",
                        max_retries, page.url,
                    )
                    raise QrNotFound(
                        f"QR code not found after {max_retries} retries on {page.url}"
                    ) from exc
                elif retry % 3 == 0:
                    logger.info("Reloading page to try QR fetch again.")
                    page.reload()

                current_qr = None

            # Emit QR only if it exists and has changed
            if (
                current_qr is not None
                and (qr is None or qr.data_list[0].data != current_qr.data_list[0].data)
            ):
                logger.info("Emitting new QR code.")
                self.client.emit("qr", current_qr)
                qr = current_qr

            # Check if the main WhatsApp interface has loaded
            try:
                if current_qr is None:
                    page.wait_for_selector(
                        client_options.get("loaded_selector"),
                        timeout=1000,
                    )
                    logger.info("WhatsApp interface loaded successfully.")
                    break
            except PWTimeoutError:
                logger.debug("WhatsApp interface not loaded yet, retrying...")

        return page
