from dataclasses import dataclass
from typing import Any, Dict, Optional, Union

from shiki4py import Shikimori
from shiki4py.types import Comment

from shikibaio.enums import DataType, EventType


@dataclass
class Event:
    _api: Shikimori
    data_type: Union[DataType, str]
    event_type: Union[EventType, str]
    data_id: int
    chat_id: int
    user_id: int
    text: str
    data: Comment

    @staticmethod
    async def create(api: Shikimori, raw: Dict[str, Any]) -> "Event":
        kwargs: Dict[str, Any] = {}

        kwargs["_api"] = api

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
            kwargs["data"] = await api.comments.show_one(raw["data"]["comment_id"])

            kwargs["data_id"] = kwargs["data"].id
            kwargs["chat_id"] = kwargs["data"].commentable_id
            kwargs["user_id"] = kwargs["data"].user_id
            kwargs["text"] = kwargs["data"].body

        return Event(**kwargs)

    async def answer(
        self,
        text: str,
        is_offtopic: Optional[bool] = None,
        broadcast: Optional[bool] = None,
    ) -> Comment:
        return await self._api.comments.create(
            text, self.chat_id, self.data.commentable_type, is_offtopic, broadcast
        )
