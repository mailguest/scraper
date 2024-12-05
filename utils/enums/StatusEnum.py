import enum

class StatusEnum(enum.Enum):
    # Status
    PENDING = "pending"
    FAILED = "failed"
    SUCCESS = "success"
    DELETED = "deleted"
    ONLINE = "online"
    OFFLINE = "offline"

    def get_status(self):
        return self.value