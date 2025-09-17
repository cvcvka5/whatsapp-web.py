from __future__ import annotations
from typing import TypedDict, List, TYPE_CHECKING
if TYPE_CHECKING:
    from .group import Group

from playwright.sync_api import Page
from ..util import get_contact_script, get_module_script
from .chat import Chat, ChatIDType


class ContactKwargs(TypedDict, total=True):
    id: ChatIDType
    name: str
    pushName: str
    notifyName: str
    shortName: str
    mentionName: str
    hash: str
    isMe: bool
    isGroup: bool
    isBusiness: bool
    isBot: bool
    isContact: bool


class Contact(Chat):
    _attribute_map = {
        "getPushname": "pushName",
        "getNotifyName": "notifyName",
        "getShortName": "shortName",
        "getMentionName": "mentionName",
        "getUserhash": "hash",
        "getIsMe": "isMe",
        "getIsBusiness": "isBusiness",
        "getIsBot": "isBot",
        "getIsWAContact": "isContact",
        "getCanRequestPhoneNumber": "canRequestPhoneNumber"
    }

    def __init__(self, page: Page, **kwargs: ContactKwargs):
        super().__init__(page, **kwargs)  # let Chat handle id, name, isGroup, unreadCount

        # Contact-specific fields
        self._push_name: str = kwargs["pushName"]
        self._notify_name: str = kwargs["notifyName"]
        self._short_name: str = kwargs["shortName"]
        self._mention_name: str = kwargs["mentionName"]
        self._hash: str = kwargs["hash"]
        self._phone_number: str = self._get_wid().get("user")

        # Flags
        self._can_request_number: bool = kwargs["canRequestPhoneNumber"]
        self._is_me: bool = kwargs["isMe"]
        self._is_business: bool = kwargs["isBusiness"]
        self._is_bot: bool = kwargs["isBot"]
        self._is_contact: bool = kwargs["isContact"]

    # --- Actions ---
    def block(self) -> None:
        script = get_module_script("WAWebBlockContactAction", "blockContact", (self._js_repr,))
        self.page.evaluate(script)

    def unblock(self) -> None:
        script = get_module_script("WAWebBlockContactAction", "unblockContact", (self._js_repr,))
        self.page.evaluate(script)

    # --- Factory ---
    @staticmethod
    def get(page: Page, jid: str) -> Contact:
        attrs = {}
        
        # Pull common Chat attributes
        contact_script = get_contact_script(jid)
        for func_name, attr_name in Chat._attribute_map.items():
            script = get_module_script("WAWebChatGetters", func_name, (contact_script,))
            attr_value = page.evaluate(script)
            attrs[attr_name] = attr_value

        # Pull Contact-specific attributes
        for func_name, attr_name in Contact._attribute_map.items():
            script = get_module_script("WAWebContactGetters", func_name, (contact_script,))
            attr_value = page.evaluate(script)
            attrs[attr_name] = attr_value

        return Contact(page, **attrs)

    def resync(self) -> None:
        """Update this instance with fresh attributes from WhatsApp Web."""
        new_contact = Contact.get(self.page, self.jid)
        self.__dict__.update(new_contact.__dict__)

    # --- Contact-only methods ---
    def get_status(self) -> str:
        script = get_module_script("WAWebContactStatusBridge", "getStatus", (self._js_variable_repr("id"),))
        return self.page.evaluate(script)["status"]

    def get_profile_picture(self) -> str:
        script = get_module_script("WAWebContactProfilePicThumbBridge", "profilePicResync", (f"[{self._js_repr}]",))
        return self.page.evaluate(script)[0].get("eurl")

    def get_lid(self) -> ChatIDType:
        script = get_module_script("WAWebApiContact", "getCurrentLid", (self._js_variable_repr("id"),))
        return self.page.evaluate(script)

    def get_common_groups(self) -> List['Group']:
        script = get_module_script(module="WAWebFindCommonGroupsContactAction", 
                                   function="findCommonGroups",
                                   args=(self._js_repr,))
        group_objects = self.page.evaluate(script).get("_index", [])
        
        common_groups = []
        for jid in group_objects.keys():
            common_groups.append(Group.get(jid))
        
        return common_groups

    # --- Properties ---
    @property
    def phone_number(self) -> str:
        return self._phone_number
    
    @property
    def jid(self) -> str:
        return self.id["_serialized"]
        
    @property
    def push_name(self) -> str:
        return self._push_name

    @property
    def notify_name(self) -> str:
        return self._notify_name

    @property
    def short_name(self) -> str:
        return self._short_name

    @property
    def mention_name(self) -> str:
        return self._mention_name

    @property
    def hash(self) -> str:
        return self._hash

    @property
    def is_me(self) -> bool:
        return self._is_me

    @property
    def is_business(self) -> bool:
        return self._is_business

    @property
    def is_bot(self) -> bool:
        return self._is_bot

    @property
    def is_contact(self) -> bool:
        return self._is_contact

    @property
    def can_request_number(self) -> bool:
        return self._can_request_number

    def _get_wid(self) -> ChatIDType:
        if self.id["server"] == "c.us":
            return self.id
        elif self.id["server"] == "lid":
            script = get_module_script(module="WAWebApiContact",
                              function="getPhoneNumber",
                              args=(self._js_variable_repr("id"),))
            wid = self.page.evaluate(script)
            
            return wid
        else:
            return None

    
    def __str__(self):
        return f"Contact({self.short_name}, {self.phone_number})"

    def __repr__(self):
        return f"Contact({self.short_name}, {self.phone_number})"


