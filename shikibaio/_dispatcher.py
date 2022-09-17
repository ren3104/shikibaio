import asyncio
from typing import List, Optional

from aiocometd import Client as Faye
from shiki4py import Shikimori

from shikibaio.enums import DataType, EventType
from shikibaio.filters import DataTypeFilter, EventTypeFilter, Filter
from shikibaio.handler import Handler
from shikibaio.types import Event


class Dispatcher:
    def __init__(
        self,
        api: Optional[Shikimori] = None,
        loop: Optional[asyncio.AbstractEventLoop] = None,
    ) -> None:
        self._loop = loop
        self._api = api
        self._faye = Faye("wss://faye-v2.shikimori.one/") if api is not None else None
        self._scheduled_subscriptions: List[str] = []
        self._handlers: List[Handler] = []

    @property
    def closed(self) -> bool:
        if self._api is None or self._faye is None:
            return True
        return self._faye.closed and self._api.closed

    async def open(self) -> "Dispatcher":
        if self._api is not None and self._faye is not None:
            if self._loop is None:
                self._loop = asyncio.get_running_loop()
            self._faye._loop = self._loop

            await self._api.open()
            await self._faye.open()

        return self

    async def close(self) -> None:
        if self._api is not None and self._faye is not None:
            await self._api.close()
            await self._faye.close()

    async def __aenter__(self) -> "Dispatcher":
        return await self.open()

    async def __aexit__(self, *args) -> None:
        await self.close()

    def run(self) -> None:
        if not self.closed or self._api == None:
            return

        async def runner():
            async with self:
                for subscription in self._scheduled_subscriptions:
                    await self._faye.subscribe(subscription)

                async for message in self._faye:
                    event = await Event.create(self._api, message)
                    await self._notify_handlers(event)

        try:
            asyncio.run(runner())
        except KeyboardInterrupt:
            pass

    async def _notify_handlers(self, event: Event) -> None:
        for handler in self._handlers:
            if await handler.filter(event):
                await handler.handle(event)

                if handler.blocking:
                    break

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
