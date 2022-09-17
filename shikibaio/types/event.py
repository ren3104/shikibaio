from dataclasses import dataclass
from typing import Any, Dict, Optional, Union

from shiki4py import Shikimori

from shikibaio.enums import DataType, EventType


@dataclass
class Event:
    data_type: str
    event_type: Union[EventType, str]
    data_id: int
    chat_id: int
    user_id: int
    text: str
    data: Dict[str, Any]

    @staticmethod
    async def create(
        api: Shikimori, raw: Dict[str, Any], data: Optional[Dict[str, Any]] = None
    ) -> "Event":
        kwargs: Dict[str, Any] = {}

        data_type: str
        event_type: str
        data_type, event_type = raw["data"]["event"].split(":")

        try:
            kwargs["data_type"] = DataType(data_type)
        except ValueError:
            kwargs["data_type"] = data_type

        try:
            kwargs["event_type"] = EventType(event_type)
        except ValueError:
            kwargs["event_type"] = event_type

        if data_type == "comment":
            if data != None:
                kwargs["data"] = data
            else:
                kwargs["data"] = await api.comments.show_one(raw["data"]["comment_id"])

            if isinstance(kwargs["data"], dict):
                kwargs["data_id"] = kwargs["data"]["id"]
                kwargs["chat_id"] = kwargs["data"]["commentable_id"]
                kwargs["user_id"] = kwargs["data"]["user_id"]
                kwargs["text"] = kwargs["data"]["body"]
            else:
                kwargs["data_id"] = kwargs["data"].__getattribute__("id")
                kwargs["chat_id"] = kwargs["data"].__getattribute__("commentable_id")
                kwargs["user_id"] = kwargs["data"].__getattribute__("user_id")
                kwargs["text"] = kwargs["data"].__getattribute__("body")

        return Event(**kwargs)
