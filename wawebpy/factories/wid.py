from ..structures.chat import Chat, ChatIDType
from ..util import get_module_script
from playwright.sync_api import Page

class Wid:
    def __new__(cls, *args, **kwargs):
        raise TypeError(f"{cls.__name__} can't be instantiated.")
    
    @staticmethod
    def fromChat(page: Page, chat: Chat) -> ChatIDType:
        script = page.evaluate(Wid.fromChatScript(chat))
        return script
    
    @staticmethod
    def fromChatScript(chat: Chat) -> str:
        return get_module_script(module="WAWebWidFactory", function="createWid", args=(chat._js_repr,))