from __future__ import annotations
from typing import TypedDict, List, Dict, Any
from playwright.sync_api import Page
from ..util import get_contact_script, get_module_script


class GroupIDType(TypedDict, total=True):
    server: str
    user: str
    _serialized: str


class GroupMetadata(TypedDict, total=False):
    id: str
    owner: str
    subject: str
    creation: int
    participants: List[Dict[str, Any]]  # jid + isAdmin/role flags etc.


class GroupKwargs(TypedDict, total=True):
    id: GroupIDType
    name: str
    formattedTitle: str
    groupMetadata: GroupMetadata
    isAnnounceGrpRestrict: bool
    unreadCount: int
    t: int
    mute: Dict[str, Any]
    muteExpiration: int
    archive: bool
    disappearingModeTrigger: str
    ephemeralDuration: int
    notSpam: bool
    trusted: bool


class Group:
    __attribute_map = {
        "getId": "id",  
        "getName": "name",
        "getMentionName": "mentionName",
        
        # Flags
        "getIsMe": "isMe",
        "getIsGroup": "isGroup",
        "getIsBot": "isBot",
        "getIsWAContact": "isContact"
    }

    def __init__(self, page: Page, **kwargs: GroupKwargs):
        self._page: Page = page

        # Identifiers
        self._id: GroupIDType = kwargs["id"]
        self._name: str = kwargs["name"]
        self._mention_name: str = kwargs["mentionName"]
        
        
        # Flags
        self._is_me: bool = kwargs["isMe"]
        self._is_group: bool = kwargs["isGroup"]
        self._is_bot: bool = kwargs["isBot"]
        self._is_contact: bool = kwargs["isContact"]
        

    @staticmethod
    def get(page: Page, jid: str) -> Group:
        attrs = {}
        for func_name, attr_name in Group.__attribute_map.items():
            group_script = get_contact_script(jid)
            script = get_module_script(
                module="WaWebContact",
                function=func_name,
                args=(group_script,),
            )
            attr_value = page.evaluate(script)
            attrs[attr_name] = attr_value

        return Group(page, **attrs)

    def resync(self) -> None:
        """Update this instance with fresh attributes from WhatsApp Web."""
        new_group = Group.get(self.page, self.jid)
        self.__dict__.update(new_group.__dict__)

    # --- Properties ---
    @property
    def page(self) -> Page:
        return self._page

    @property
    def id(self) -> GroupIDType:
        return self._id

    @property
    def jid(self) -> str:
        return self._id["_serialized"]

    @property
    def name(self) -> str:
        return self._name

    @property
    def mention_name(self) -> str:
        return self._mention_name
    
    def is_me(self) -> bool:
        return self._is_me

    @property
    def is_group(self) -> bool:
        return self._is_group

    @property
    def is_bot(self) -> bool:
        return self._is_bot

    @property
    def is_contact(self) -> bool:
        return self._is_contact

    def __str__(self):
        return f"Group({self.formatted_title}, {self.jid})"
