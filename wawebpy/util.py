from playwright._impl._errors import TimeoutError as PWTimeoutError
from playwright.sync_api import Page
from typing import Tuple
from .constants import WAWebModuleType, WAWEB_STORE
import qrcode
from .exceptions import QrNotFound

def get_qr_in_page(page: Page, qr_data_selector: str, timeout: int = 5000) -> qrcode.QRCode:
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
    try:
        qr_data_div = page.wait_for_selector(qr_data_selector, timeout=timeout)
        qr_data = qr_data_div.get_attribute("data-ref")
    except PWTimeoutError:
        raise QrNotFound(f"QR code couldn't be found with selector '{qr_data_selector}'.")
    
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.ERROR_CORRECT_M,
        box_size=1,
        border=0
    )
    qr.add_data(qr_data)
    qr.make(fit=True)
    
    return qr



def get_module_script(module: WAWebModuleType, function: str = None, args: Tuple[str] = None) -> str:
    
    basename, *variables = module.split(".")
    
    ret = f"require('{basename}')"
    if variables:
        for variable in variables:
            ret += f".{variable}"
    
    if function:
        ret += f".{function}("

    if args is not None:
        for arg in args:
            is_string = type(arg) == str
            is_script = type(arg) == tuple
            if is_script:
                ret += str(arg[0])
            else:
                ret += f"'{arg}'" if is_string else str(arg)  
            ret += ","
    
    ret = ret.strip(",")
    
    if function:
        ret += ")"
    
    return ret

def get_contact_script(jid: str) -> str:
    return get_module_script(WAWEB_STORE["Contacts"])+f"._index['{jid}']"