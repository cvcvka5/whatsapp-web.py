from __future__ import annotations
from typing import TypedDict, List, Optional, Any, Dict
from playwright.sync_api import Page
from ..util import get_contact_script, get_module_script
from .contact import Contact
from .chat import Chat, ChatKwargs


class GroupIDType(TypedDict, total=True):
    server: str
    user: str
    _serialized: str


class GroupParticipantObject(TypedDict):
    id: GroupIDType
    phoneNumber: GroupIDType
    username: str
    isAdmin: bool
    isSuperAdmin: bool
    

class GroupMetadata(TypedDict, total=False):
    id: GroupIDType
    owner: GroupIDType
    subject: str
    creation: int
    participants: List[GroupParticipantObject]
    subjectOwner: GroupIDType
    subjectTime: int
    size: int

    # Feature toggles / restrictions
    allowNonAdminSubGroupCreation: bool
    announce: bool
    restrict: bool
    incognito: bool
    generalChatAutoAddDisabled: bool
    generalSubgroup: bool
    defaultSubgroup: bool
    membershipApprovalMode: bool
    reportToAdminMode: bool
    noFrequentlyForwarded: bool
    suspended: bool
    support: bool

    # Extra details
    creatorCountryCode: Optional[str]
    creatorUsername: Optional[str]
    subjectOwnerUsername: Optional[str]
    numSubgroups: Optional[int]
    membershipApprovalRequest: Optional[Any]
    hasCapi: bool
    hasIncompleteParticipantInformation: bool
    isLidAddressingMode: bool
    isParentGroup: bool
    isParentGroupClosed: bool
    memberAddMode: str
    trusted: Optional[bool]

class GroupKwargs(ChatKwargs, total=True):
    mentionName: str
    
    isMe: bool
    isBot: bool
    isContact: bool

class Group(Chat):
    _attribute_map = {
        # Attributes
        "getMentionName": "mentionName",
        
        # Flags
        "getIsMe": "isMe",
        "getIsBot": "isBot",
        "getIsWAContact": "isContact"
    }

    def __init__(self, page: Page, **kwargs: Group):
        self._page: Page = page

        # Identifiers
        self._id: GroupIDType = kwargs["id"]
        self._name: str = kwargs["name"]
        self._mention_name: str = kwargs["mentionName"]
        
        
        # Flags
        self._is_group: bool = kwargs["isGroup"]
        self._is_me: bool = kwargs["isMe"]
        self._is_bot: bool = kwargs["isBot"]
        self._is_contact: bool = kwargs["isContact"]
        

    @staticmethod
    def get(page: Page, jid: str) -> Group:
        attrs = {}
        # Get general chat attributes
        group_script = get_contact_script(jid)
        for func_name, attr_name in Chat._attribute_map.items():
            script = get_module_script(
                module="WAWebChatGetters",
                function=func_name,
                args=(group_script,),
            )
            attr_value = page.evaluate(script)
            attrs[attr_name] = attr_value

        # Get group specific attributes
        for func_name, attr_name in Group._attribute_map.items():
            script = get_module_script(
                module="WAWebContactGetters",
                function=func_name,
                args=(group_script,),
            )
            attr_value = page.evaluate(script)
            attrs[attr_name] = attr_value

        # Get metadata

        return Group(page, **attrs)

    def resync(self) -> None:
        """Update this instance with fresh attributes from WhatsApp Web."""
        new_group = Group.get(self.page, self.jid)
        self.__dict__.update(new_group.__dict__)

    # --- Properties ---
    def get_metadata(self) -> GroupMetadata:
        script = get_module_script(
            module="WAWebGroupQueryJob",
            function="queryGroupsById",
            args=("["+self._js_variable_repr('id')+"['_serialized']]",)
        )
        metadata = self.page.evaluate(script)[0]
        
        return metadata

    def get_participants(self) -> List[Contact]:
        metadata = self.get_metadata()
        participant_objects = metadata.get("participants", [])
        
        participants = []
        for obj in participant_objects:
            _id = obj.get("id", None)
            if not _id: continue
            _jid = _id.get("_serialized", None)
            if not _jid: continue
            
            participants.append(Contact.get(self.page, _jid))
            
        return participants
        
    
    @property
    def mention_name(self) -> str:
        return self._mention_name
    
    @property
    def is_me(self) -> bool:
        return self._is_me

    @property
    def is_bot(self) -> bool:
        return self._is_bot

    @property
    def is_contact(self) -> bool:
        return self._is_contact

    def __str__(self):
        return f"Group({self.name}, {self.jid})"

    def __repr__(self):
        return f"Group({self.name}, {self.jid})"
