from __future__ import annotations
from typing import TypedDict, Dict, Any
from playwright.sync_api import Page
from ..util import get_contact_script, get_module_script


class ChatIDType(TypedDict, total=True):
    server: str
    user: str
    _serialized: str


class ChatKwargs(TypedDict, total=True):
    id: ChatIDType
    name: str
    isGroup: bool
    unreadCount: int
    


class Chat:
    """Base class for WhatsApp chats (both contacts and groups)."""

    _attribute_map = {
        "getId": "id",
        "getName": "name",
        "getIsGroup": "isGroup",
        "getUnreadCount": "unreadCount",
    }

    def __init__(self, page: Page, **kwargs: ChatKwargs):
        self._page: Page = page

        # Identifiers
        self._id: ChatIDType = kwargs["id"]
        self._name: str = kwargs["name"]

        # Flags / State
        self._is_group: bool = kwargs["isGroup"]
        self._unread_count: int = kwargs["unreadCount"]

    # --- Factory ---
    @staticmethod
    def get(page: Page, jid: str) -> Chat:
        attrs: Dict[str, Any] = {}
        for func_name, attr_name in Chat._attribute_map.items():
            chat_script = get_contact_script(jid)
            script = get_module_script(
                module="WAWebChatGetters",
                function=func_name,
                args=(chat_script,),
            )
            attr_value = page.evaluate(script)
            attrs[attr_name] = attr_value

        return Chat(page, **attrs)

    def resync(self) -> None:
        """Update this instance with fresh attributes from WhatsApp Web."""
        new_chat = Chat.get(self.page, self.jid)
        self.__dict__.update(new_chat.__dict__)

    # --- Properties ---
    @property
    def page(self) -> Page:
        return self._page

    @property
    def id(self) -> ChatIDType:
        return self._id

    @property
    def jid(self) -> str:
        return self._id["_serialized"]

    @property
    def name(self) -> str:
        return self._name

    @property
    def is_group(self) -> bool:
        return self._is_group

    @property
    def unread_count(self) -> int:
        return self._unread_count

    @property
    def _js_repr(self) -> str:
        return get_contact_script(self.jid)

    def _js_variable_repr(self, variable: str) -> str:
        return f"{self._js_repr}.{variable}"

    def __str__(self) -> str:
        kind = "Group" if self.is_group else "Contact"
        return f"{kind}({self.name}, {self.jid})"
