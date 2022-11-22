from dataclasses import dataclass
from typing import Any, Dict, Optional, Union

from shikibaio.adapt_clients.base import BaseAdapt
from shikibaio.enums import DataType, EventType


@dataclass
class Event:
    data_type: Union[DataType, str]
    event_type: Union[EventType, str]
    data_id: int
    chat_id: int
    user_id: int
    text: str
    data: Optional[Any]
    _adapt_client: BaseAdapt

    async def answer(
        self,
        text: str,
        is_offtopic: bool = False,
        broadcast: bool = False,
    ) -> Any:
        if self.event_type == EventType.DELETE:
            raise RuntimeError("Невозможно ответить на комментарий, так как он удален!")
        if self.data is None:
            raise RuntimeError("Event.data не может быть None!")
        return await self._adapt_client.create_comment(
            text, self.chat_id, self.data["commentable_type"], is_offtopic, broadcast
        )


async def create_event(adapt_client: BaseAdapt, raw: Dict[str, Any]) -> Event:
    kwargs: Dict[str, Any] = {}

    kwargs["_adapt_client"] = adapt_client

    data_type: Union[DataType, str]
    event_type: Union[EventType, str]
    data_type, event_type = raw["data"]["event"].split(":")

    try:
        data_type = DataType(data_type)
    except ValueError:
        pass

    try:
        event_type = EventType(event_type)
    except ValueError:
        pass

    kwargs["data_type"] = data_type
    kwargs["event_type"] = event_type

    if data_type == DataType.COMMENT:
        kwargs["data_id"] = raw["data"]["comment_id"]
        kwargs["chat_id"] = raw["data"]["topic_id"]
        kwargs["user_id"] = raw["data"]["user_id"]

        if event_type != EventType.DELETE:
            kwargs["data"] = await adapt_client.get_comment(kwargs["data_id"])
            kwargs["text"] = adapt_client.to_dict(kwargs["data"])["body"]
        else:
            kwargs["data"] = None
            kwargs["text"] = ""

    return Event(**kwargs)
