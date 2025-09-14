from __future__ import annotations
from typing import TypedDict, Optional
from playwright.sync_api import Page
from ..util import get_contact_script
from ..constants import WAWEB_STORE

class IDType(TypedDict):
    server: str
    user: str
    _serialized: str

class ContactAttributes(TypedDict, total=False):
    id: IDType
    name: str
    shortName: str
    pushname: str
    type: str
    statusMute: bool
    isContactSyncCompleted: int
    textStatusLastUpdateTime: int
    syncToAddressbook: bool
    stale: bool
    isContactBlocked: bool
    isContactOptedOut: bool
    isEverOptedOutOfMarketingMessages: bool
    isMarketingMessageThread: bool
    pendingAction: int
    promises: dict
    isHosted: bool
    isOrHasBeenHosted: bool
    isFavorite: bool
    canSendMsgWhileTimelocked: bool

class Contact:
    def __init__(self, page: Page, **kwargs):
        attrs: ContactAttributes = kwargs
        self.id: Optional[IDType] = attrs.get("id")
        self.jid = self.id.get("_serialized")
        self.name: Optional[str] = attrs.get("name")
        self.shortName: Optional[str] = attrs.get("shortName")
        self.pushname: Optional[str] = attrs.get("pushname")
        self.type: Optional[str] = attrs.get("type")
        self.statusMute: bool = attrs.get("statusMute", False)
        self.isContactSyncCompleted: int = attrs.get("isContactSyncCompleted", 0)
        self.textStatusLastUpdateTime: int = attrs.get("textStatusLastUpdateTime", -1)
        self.syncToAddressbook: bool = attrs.get("syncToAddressbook", True)
        self.stale: bool = attrs.get("stale", False)
        self.isContactBlocked: bool = attrs.get("isContactBlocked", False)
        self.isContactOptedOut: bool = attrs.get("isContactOptedOut", False)
        self.isEverOptedOutOfMarketingMessages: bool = attrs.get("isEverOptedOutOfMarketingMessages", False)
        self.isMarketingMessageThread: bool = attrs.get("isMarketingMessageThread", False)
        self.pendingAction: int = attrs.get("pendingAction", 0)
        self.promises: dict = attrs.get("promises", {})
        self.isHosted: bool = attrs.get("isHosted", False)
        self.isOrHasBeenHosted: bool = attrs.get("isOrHasBeenHosted", False)
        self.isFavorite: bool = attrs.get("isFavorite", False)
        self.canSendMsgWhileTimelocked: bool = attrs.get("canSendMsgWhileTimelocked", True)
        # TODO Add common groups & profilePic
        self.commonGroups: None = None
        self.profilePic: None = None

    @staticmethod
    def get(page: Page, jid: str) -> Contact:
        res = page.evaluate(get_contact_script(jid)+".attributes")
        return Contact(page, **res)

    def resync(self) -> None:
        """Update this instance with fresh attributes from WhatsApp Web."""
        new_contact = Contact.get(self.page, self.jid)
        self.__dict__.update(new_contact.__dict__)