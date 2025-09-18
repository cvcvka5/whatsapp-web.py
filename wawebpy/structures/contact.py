from __future__ import annotations
from typing import TypedDict, List, Union, TYPE_CHECKING
if TYPE_CHECKING:
    from .group import Group
from ..exceptions import StatusFetchError, ContactNotFound, ProfilePictureNotFound, WidFetchError
from playwright.sync_api import Page
from ..util import get_contact_script, get_module_script
from .chat import Chat, ChatIDType
from ..logger import logger


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
        super().__init__(page, **kwargs)

        # Contact-specific fields
        self._push_name: str = kwargs["pushName"]
        self._notify_name: str = kwargs["notifyName"]
        self._short_name: str = kwargs["shortName"]
        self._mention_name: str = kwargs["mentionName"]
        self._hash: str = kwargs["hash"]
        self._phone_number: str = self.get_wid().get("user")

        # Flags
        self._can_request_number: bool = kwargs["canRequestPhoneNumber"]
        self._is_me: bool = kwargs["isMe"]
        self._is_business: bool = kwargs["isBusiness"]
        self._is_bot: bool = kwargs["isBot"]
        self._is_contact: bool = kwargs["isContact"]

        logger.debug(f"Contact initialized: {self}")

    # --- Actions ---
    def block(self) -> None:
        logger.info(f"Blocking contact {self.jid}")
        script = get_module_script("WAWebBlockContactAction", "blockContact", (self._js_repr,))
        self.page.evaluate(script)
        logger.debug(f"Contact {self.jid} blocked.")

    def unblock(self) -> None:
        logger.info(f"Unblocking contact {self.jid}")
        script = get_module_script("WAWebBlockContactAction", "unblockContact", (self._js_repr,))
        self.page.evaluate(script)
        logger.debug(f"Contact {self.jid} unblocked.")

    # --- Factory ---
    @staticmethod
    def get(page: Page, jid: str) -> Contact:
        logger.debug(f"Fetching contact {jid}")
        attrs = {}

        try:
            contact_script = get_contact_script(jid)
            for func_name, attr_name in Chat._attribute_map.items():
                script = get_module_script("WAWebChatGetters", func_name, (contact_script,))
                attrs[attr_name] = page.evaluate(script)

            for func_name, attr_name in Contact._attribute_map.items():
                script = get_module_script("WAWebContactGetters", func_name, (contact_script,))
                attrs[attr_name] = page.evaluate(script)
        except Exception as e:
            logger.exception(f"Failed to fetch contact {jid}")
            raise ContactNotFound(f"Failed to fetch contact {jid}") from e

        if not attrs.get("id"):
            logger.warning(f"Contact {jid} not found in attributes.")
            raise ContactNotFound(f"Contact {jid} not found")

        logger.info(f"Contact {jid} fetched successfully.")
        
        logger.debug(f"Ensuring the id is of type WID.")
        try:
            contact = Contact(page, **attrs)

            contact._id = contact.get_wid()
            logger.debug(f"The id is forced as WID.")
        except Exception as e:
            logger.exception(f"Couldn't ensure that id is of type WID.")
            raise WidFetchError(f"Couldn't force WID conversion for contact '{contact.name}'.") 
        
        return contact

    def resync(self) -> None:
        logger.info(f"Resyncing contact {self.jid}")
        new_contact = Contact.get(self.page, self.jid)
        self.__dict__.update(new_contact.__dict__)
        logger.debug(f"Contact {self.jid} resynced.")

    # --- Contact-only methods ---
    def get_status(self) -> str:
        logger.debug(f"Fetching status for {self.jid}")
        try:
            script = get_module_script("WAWebContactStatusBridge", "getStatus", (self._js_variable_repr("id"),))
            status = self.page.evaluate(script)["status"]
            logger.info(f"Fetched status for {self.jid}: {status}")
            return status
        except Exception as e:
            logger.exception(f"Failed to fetch status for {self.jid}")
            raise StatusFetchError(f"Failed to fetch status for {self.jid}") from e

    def get_profile_picture(self) -> Union[str, None]:
        logger.debug(f"Fetching profile picture for {self.jid}")
        try:
            script = get_module_script("WAWebContactProfilePicThumbBridge", "profilePicResync", (f"[{self._js_repr}]",))

            pic = self.page.evaluate(script)[0].get("eurl", None)
            if not pic:
                logger.warning(f"No profile picture found for {self.jid}")
            else:
                logger.info(f"Fetched profile picture for {self.jid}")
    
            return pic
        except Exception as e:
            logger.exception(f"Failed to fetch profile picture for {self.jid}")
            raise ProfilePictureNotFound(f"Failed to fetch profile picture for {self.jid}") from e

    def get_lid(self) -> ChatIDType:
        logger.debug(f"Fetching LID for {self.jid}")
        script = get_module_script("WAWebApiContact", "getCurrentLid", (self._js_variable_repr("id"),))
        lid = self.page.evaluate(script)
        logger.info(f"Fetched LID for {self.jid}")
        return lid

    def get_common_groups(self) -> List['Group']:
        logger.debug(f"Fetching common groups for {self.jid}")
        script = get_module_script(
            module="WAWebFindCommonGroupsContactAction",
            function="findCommonGroups",
            args=(self._js_repr,),
        )
        group_objects = self.page.evaluate(script).get("_index", [])

        common_groups = []
        for jid in group_objects.keys():
            logger.debug(f"Fetching group {jid} for common groups of {self.jid}")
            common_groups.append(Group.get(jid))

        logger.info(f"Found {len(common_groups)} common groups for {self.jid}")
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

    def get_wid(self) -> ChatIDType:
        logger.debug(f"Fetching WID for {getattr(self, 'jid', 'unknown')}")
        try:
            if self.id["server"] == "c.us":
                return self.id
            elif self.id["server"] == "lid":
                script = get_module_script(
                    module="WAWebApiContact",
                    function="getPhoneNumber",
                    args=(self._js_variable_repr("id"),),
                )
                wid = self.page.evaluate(script)
                if not wid:
                    logger.warning(f"No WID found for {self.jid}")
                    raise WidFetchError(f"No WID found for {self.jid}")
                logger.info(f"Fetched WID for {self.jid}")
                return wid
            else:
                logger.error(f"Unsupported server type for {self.jid}")
                raise WidFetchError(f"Unsupported server type for {self.jid}")
        except Exception as e:
            logger.exception(f"Failed to fetch WID for {self.jid}")
            raise WidFetchError(f"Failed to fetch WID for {self.jid}") from e

    def __str__(self):
        return f"Contact({self.short_name}, {self.phone_number})"

    def __repr__(self):
        return f"Contact({self.short_name}, {self.phone_number})"