from playwright.sync_api import Page

class Contact:
    def __init__(
        self,
        id: str,
        name: str,
        shortName: str,
        pushname: str,
        type: str,
        statusMute: bool,
        isContactSyncCompleted: int,
        textStatusLastUpdateTime: int,
        syncToAddressbook: bool,
        stale: bool,
        isContactBlocked: bool,
        isContactOptedOut: bool,
        isEverOptedOutOfMarketingMessages: bool,
        isMarketingMessageThread: bool,
        pendingAction: int,
        promises: dict,
        isHosted: bool,
        isOrHasBeenHosted: bool,
        isFavorite: bool,
        canSendMsgWhileTimelocked: bool
    ):
        self.id = id
        self.name = name
        self.shortName = shortName
        self.pushname = pushname
        self.type = type
        self.statusMute = statusMute
        self.isContactSyncCompleted = isContactSyncCompleted
        self.textStatusLastUpdateTime = textStatusLastUpdateTime
        self.syncToAddressbook = syncToAddressbook
        self.stale = stale
        self.isContactBlocked = isContactBlocked
        self.isContactOptedOut = isContactOptedOut
        self.isEverOptedOutOfMarketingMessages = isEverOptedOutOfMarketingMessages
        self.isMarketingMessageThread = isMarketingMessageThread
        self.pendingAction = pendingAction
        self.promises = promises
        self.isHosted = isHosted
        self.isOrHasBeenHosted = isOrHasBeenHosted
        self.isFavorite = isFavorite
        self.canSendMsgWhileTimelocked = canSendMsgWhileTimelocked

    @staticmethod
    def create(page: Page, jid: str):
        page.evaluate()
        
