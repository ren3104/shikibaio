from enum import Enum


class EventType(Enum):
    NEW = "created"
    EDIT = "updated"
    DELETE = "deleted"
