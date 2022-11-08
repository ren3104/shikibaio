import asyncio
from typing import Awaitable, Callable, Dict, List, Optional, Tuple, Union

from aiocometd import Client as Faye
from shiki4py import Shikimori

from shikibaio.enums import DataType, EventType
from shikibaio.filters import DataTypeFilter, EventTypeFilter, Filter
from shikibaio.handler import Handler
from shikibaio.types import Event


class Dispatcher:
    def __init__(self, api: Optional[Shikimori] = None) -> None:
        self._restricted_mode = api is None
        self._api = api
        self._faye = (
            Faye("wss://faye-v2.shikimori.one/") if not self._restricted_mode else None
        )
        self._scheduled_subscriptions: List[str] = []
        self._handlers: List[Handler] = []
        self._listeners: Dict[
            str, List[Tuple[asyncio.Future, Callable[..., bool]]]
        ] = {}

    def run(self) -> None:
        async def runner():
            try:
                if not self._restricted_mode:
                    self._faye._loop = asyncio.get_running_loop()
                    await self._api.open()
                    await self._faye.open()

                for subscription in self._scheduled_subscriptions:
                    await self._faye.subscribe(subscription)

                async for message in self._faye:
                    event = await Event.create(self._api, message)
                    await self._notify_handlers(event)
            finally:
                if not self._restricted_mode:
                    await self._api.close()
                    await self._faye.close()

        try:
            asyncio.run(runner())
        except KeyboardInterrupt:
            pass

    async def _notify_handlers(self, event: Event) -> None:
        event_type = event.event_type
        if isinstance(event_type, EventType):
            event_type = event_type.value

        listeners = self._listeners.get(event_type)
        if listeners:
            removed = []
            for i, (future, condition) in enumerate(listeners):
                if future.cancelled():
                    removed.append(i)
                    continue

                try:
                    result = condition(event)
                except Exception as exc:
                    future.set_exception(exc)
                    removed.append(i)
                else:
                    if result:
                        future.set_result(event)
                        removed.append(i)

            if len(removed) == len(listeners):
                self._listeners.pop(event_type)
            else:
                for idx in reversed(removed):
                    del listeners[idx]

        for handler in self._handlers:
            if await handler.filter(event):
                await handler.handle(event)

                if handler.blocking:
                    break

    def wait_for(
        self,
        event: Union[str, EventType],
        check: Optional[Callable[..., bool]] = None,
        timeout: Optional[float] = None,
    ) -> Awaitable[Event]:
        future = asyncio.get_running_loop().create_future()

        if check is None:
            check = lambda e: True

        if isinstance(event, EventType):
            event = event.value

        try:
            listeners = self._listeners[event]
        except KeyError:
            listeners = []
            self._listeners[event] = listeners

        listeners.append((future, check))

        return asyncio.wait_for(future, timeout)

    def event_handler(self, *filters: Filter, blocking: bool = True):
        def decorator(callback):
            if callback not in self._handlers:
                self._handlers.append(Handler(callback, filters, blocking))

            return callback

        return decorator

    def topic_handler(self, *filters: Filter, blocking: bool = True):
        def decorator(callback):
            if callback not in self._handlers:
                topic_filters = (
                    EventTypeFilter(EventType.NEW),
                    DataTypeFilter(DataType.COMMENT),
                )
                self._handlers.append(
                    Handler(callback, topic_filters + filters, blocking)
                )

            return callback

        return decorator

    def subscribe_topic(self, topic_id: int, is_user_topic: bool = False) -> None:
        commentable_type = "user" if is_user_topic else "topic"
        self._scheduled_subscriptions.append(f"/{commentable_type}-{topic_id}")
