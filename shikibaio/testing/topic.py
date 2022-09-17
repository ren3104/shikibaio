from copy import deepcopy
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional, Union

from shikibaio import Dispatcher
from shikibaio.enums import EventType
from shikibaio.types import Event
from shikibaio.utils import dict_diff


class Topic:
    def __init__(
        self,
        dispatcher: Dispatcher,
        custom_default_data: Optional[Dict[str, Any]] = None,
    ) -> None:
        self._dispatcher = dispatcher
        self._default_data: Dict[str, Any] = {
            "id": 0,
            "user_id": 1,
            "commentable_id": 1,
            "commentable_type": "Topic",
            "body": "",
            "html_body": "",
            "created_at": "",
            "updated_at": "",
            "is_offtopic": False,
            "is_summary": False,
            "can_be_edited": False,
            "user": {
                "id": 1,
                "nickname": "test",
                "avatar": "https://shikimori.one/assets/globals/missing_avatar/x48.png",
                "image": {
                    "x160": "https://shikimori.one/assets/globals/missing_avatar/x160.png",
                    "x148": "https://shikimori.one/assets/globals/missing_avatar/x148.png",
                    "x80": "https://shikimori.one/assets/globals/missing_avatar/x80.png",
                    "x64": "https://shikimori.one/assets/globals/missing_avatar/x64.png",
                    "x48": "https://shikimori.one/assets/globals/missing_avatar/x48.png",
                    "x32": "https://shikimori.one/assets/globals/missing_avatar/x32.png",
                    "x16": "https://shikimori.one/assets/globals/missing_avatar/x16.png",
                },
                "last_online_at": "",
            },
        }
        if custom_default_data is not None:
            self._default_data.update(custom_default_data)
        self._current_id = 0
        self._history: Dict[int, Dict[str, Any]] = {}

    async def create_comment(
        self, text: str, custom_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        response_data = deepcopy(self._default_data)

        now = self._iso_now()
        response_data["created_at"] = now
        response_data["updated_at"] = now
        response_data["user"]["last_online_at"] = now

        self._current_id += 1
        response_data["id"] = self._current_id

        response_data["body"] = text

        if custom_data is not None:
            response_data.update(custom_data)

        await self._dispatcher._notify_handlers(
            await self._event(EventType.NEW, response_data)
        )

        self._add_history(response_data)

        return response_data

    async def update_comment(
        self,
        text: str,
        id: Optional[int] = None,
        custom_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        if id == None:
            id = self._current_id

        if id in self._history:
            comment_data = self._history[id]
        else:
            print(f"Комментарий (id={id}) не найден!")
            return {}

        response_data = deepcopy(self._default_data)
        response_data.update(comment_data)

        now = self._iso_now()
        response_data["updated_at"] = now
        response_data["user"]["last_online_at"] = now

        response_data["body"] = text

        if custom_data is not None:
            response_data.update(custom_data)

        await self._dispatcher._notify_handlers(
            await self._event(EventType.EDIT, response_data)
        )

        self._add_history(response_data)

        return response_data

    async def _event(
        self, event_type: Union[EventType, str], data: Dict[str, Any]
    ) -> Event:
        if isinstance(event_type, EventType):
            event_type = event_type.value
        return await Event.create(
            None, {"data": {"event": f"comment:{event_type}"}}, data
        )

    def _iso_now(self) -> str:
        return datetime.isoformat(datetime.now(timezone(timedelta(hours=3))))

    def _add_history(self, data: Dict[str, Any]) -> None:
        self._history[data["id"]] = dict_diff(data, self._default_data)
