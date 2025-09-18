from __future__ import annotations
from typing import TypedDict, List, Optional, Any

from ..exceptions import GroupNotFound, FetchGroupMetadataError
from ..logger import logger
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

    def __init__(self, page: Page, **kwargs: GroupKwargs):
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

        logger.debug(f"Initialized Group({self._name}, {self._id['_serialized']})")

    @staticmethod
    def get(page: Page, jid: str) -> Group:
        logger.debug(f"Fetching group {jid}")
        attrs = {}
        group_script = get_contact_script(jid)
        try:
            for func_name, attr_name in Chat._attribute_map.items():
                script = get_module_script(
                    module="WAWebChatGetters",
                    function=func_name,
                    args=(group_script,),
                )
                attrs[attr_name] = page.evaluate(script)

            for func_name, attr_name in Group._attribute_map.items():
                script = get_module_script(
                    module="WAWebContactGetters",
                    function=func_name,
                    args=(group_script,),
                )
                attrs[attr_name] = page.evaluate(script)

            logger.info(f"Successfully fetched group {jid}")
            return Group(page, **attrs)
        except Exception as e:
            logger.error(f"Failed to fetch group {jid}: {e}")
            raise GroupNotFound(f"An error occurred while trying to get Group {jid}") from e

    def resync(self) -> None:
        logger.debug(f"Resyncing group {self.jid}")
        try:
            new_group = Group.get(self.page, self.jid)
            self.__dict__.update(new_group.__dict__)
            logger.info(f"Resynced group {self.jid}")
        except Exception as e:
            logger.error(f"Failed to resync group {self.jid}: {e}")
            raise e

    def get_metadata(self) -> GroupMetadata:
        logger.debug(f"Fetching metadata for group {self.jid}")
        script = get_module_script(
            module="WAWebGroupQueryJob",
            function="queryGroupsById",
            args=("["+self._js_variable_repr('id')+"['_serialized']]",)
        )
        try:
            metadata = self.page.evaluate(script)[0]
            logger.info(f"Fetched metadata for group {self.jid}")
            return metadata
        except Exception as e:
            logger.error(f"Error fetching metadata for group {self.jid}: {e}")
            raise FetchGroupMetadataError(
                f"Failed to fetch Group Metadata for {self.jid}"
            ) from e

    def get_participants(self) -> List[Contact]:
        logger.debug(f"Fetching participants for group {self.jid}")
        participants: List[Contact] = []
        try:
            metadata = self.get_metadata()
            participant_objects = metadata.get("participants", [])
            
            for obj in participant_objects:
                _id = obj.get("id")
                if not _id:
                    logger.warning(f"Skipping participant with missing id in group {self.jid}")
                    continue
                _jid = _id.get("_serialized")
                if not _jid:
                    logger.warning(f"Skipping participant with missing jid in group {self.jid}")
                    continue
                try:
                    participant = Contact.get(self.page, _jid)
                    participants.append(participant)
                except Exception as e:
                    logger.warning(f"Failed to fetch participant {_jid} in group {self.jid}: {e}")
                    continue

            logger.info(f"Fetched {len(participants)} participants for group {self.jid}")
            return participants
        except Exception as e:
            logger.error(f"Error fetching participants for group {self.jid}: {e}")
            raise FetchGroupMetadataError(
                f"Failed to fetch participants for group {self.jid}"
            ) from e

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
        return f"Group({self._name}, {self.jid})"

    def __repr__(self):
        return f"Group({self._name}, {self.jid})"
