from __future__ import annotations
from typing import TypedDict
from playwright.sync_api import Page
from ..util import get_contact_script, get_module_script

class IDType(TypedDict, total=True):
    server: str
    user: str
    _serialized: str

class ContactKwargs(TypedDict, total=True):
    id: IDType
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

class Contact:
    __attribute_map = {
            "getId": "id",
            "getName": "name",
            "getPushname": "pushName",
            "getNotifyName": "notifyName",
            "getShortName": "shortName",
            "getMentionName": "mentionName",

            # Flags
            "getUserhash": "hash",
            "getIsMe": "isMe",
            "getIsGroup": "isGroup",
            "getIsBusiness": "isBusiness",
            "getIsBot": "isBot",
            "getIsWAContact": "isContact",
        }
    
    def __init__(self, page: Page, **kwargs: ContactKwargs):
        self._page: Page = page
        
        # Required fields from kwargs
        self._id: IDType = kwargs["id"]
        self._name: str = kwargs["name"]
        self._push_name: str = kwargs["pushName"]
        self._notify_name: str = kwargs["notifyName"]
        self._short_name: str = kwargs["shortName"]
        self._mention_name: str = kwargs["mentionName"]
        self._hash: str = kwargs["hash"]

        # Flags
        self._is_me: bool = kwargs["isMe"]
        self._is_group: bool = kwargs["isGroup"]
        self._is_business: bool = kwargs["isBusiness"]
        self._is_bot: bool = kwargs["isBot"]
        self._is_contact: bool = kwargs["isContact"]


    def block(self) -> None:
        script = get_module_script("WAWebBlockContactAction", "blockContact", ("{'contact': "+self.__js_repr+"}", ))
        self.page.evaluate(script)
        
 
    def unblock(self) -> None:
        script = get_module_script("WAWebBlockContactAction", "unblockContact", (self.__js_repr, ))
        self.page.evaluate(script)


    @staticmethod
    def get(page: Page, jid: str) -> Contact:
        attrs = {}
        for func_name, attr_name in Contact.__attribute_map.items():
            contact_script = get_contact_script(jid)
            script = get_module_script(module="WAWebContactGetters",
                                       function=func_name,
                                       args=(contact_script, ))
            attr_value = page.evaluate(script)
            
            attrs[attr_name] = attr_value
                
        
        return Contact(page, **attrs)

    def resync(self) -> None:
        """Update this instance with fresh attributes from WhatsApp Web."""
        new_contact = Contact.get(self.page, self.jid)
        self.__dict__.update(new_contact.__dict__)
    

    
    # --- Properties (read-only) ---
    def get_common_groups(self):
        # TODO
        pass
    
    
    def get_status(self) -> str:
        script = get_module_script("WAWebContactStatusBridge", "getStatus",
                                   (self.__js_variable_repr("id"),))
        
        return self.page.evaluate(script)["status"]
    
    def get_profile_picture(self) -> str:
        script = get_module_script("WAWebContactProfilePicThumbBridge", "profilePicResync", (f"[{self.__js_repr}]",))
        return self.page.evaluate(script)[0].get("eurl")

    
    @property
    def page(self) -> Page:
        return self._page

    @property
    def id(self) -> IDType:
        return self._id

    @property
    def jid(self) -> str:
        return self._id["_serialized"]

    @property
    def name(self) -> str:
        return self._name

    @property
    def phone_number(self) -> str:
        return self._id["user"]

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

    # Flags
    @property
    def is_me(self) -> bool:
        return self._is_me

    @property
    def is_group(self) -> bool:
        return self._is_group

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
    def __js_repr(self) -> str:
        return get_contact_script(self.jid) 
    
    def __js_variable_repr(self, variable: str):
        return f"{self.__js_repr}.{variable}"
    
    def __str__(self):
        return f"Contact({self.short_name}, {self.phone_number})"
        