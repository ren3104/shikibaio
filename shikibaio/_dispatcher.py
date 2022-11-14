import asyncio
from typing import Any, Awaitable, Callable, Coroutine, List, Optional, Union

from aiocometd import Client as Faye

from shikibaio.adapt_clients import get_adapt_client
from shikibaio.enums import EventType
from shikibaio.handlers import Handler, IterHandler
from shikibaio.types import Event, create_event


class Dispatcher:
    def __init__(self, api_client: Any, prefixes: List[str] = ["!", "/"]) -> None:
        self._adapt_client = get_adapt_client(api_client)
        self._faye = Faye("wss://faye-v2.shikimori.one/")

        self._prefixes = prefixes

        self._startup_handlers: List[Coroutine] = []
        self._event_handlers: List[Handler] = []

    async def _startup(self) -> None:
        for handler in self._startup_handlers:
            await handler

    async def _runner(self) -> None:
        try:
            self._faye._loop = asyncio.get_running_loop()
            await self._adapt_client.open()
            await self._faye.open()

            await self._startup()

            async for message in self._faye:
                event = await create_event(self._adapt_client, message)
                await self._notify_handlers(event)
        finally:
            await self._adapt_client.close()
            await self._faye.close()

    def run(self) -> None:
        try:
            asyncio.run(self._runner())
        except KeyboardInterrupt:
            pass

    async def _notify_handlers(self, event: Event) -> None:
        for handler in self._event_handlers:
            if event.event_type == handler.event_type and handler.check(event):
                if callable(handler.callback):
                    await handler.callback(event)
                elif isinstance(handler.callback, asyncio.Future):
                    if not handler.callback.cancelled():
                        handler.callback.set_result(event)
                    self._event_handlers.remove(handler)
                elif isinstance(handler.callback, IterHandler):
                    if not handler.callback.is_finished():
                        handler.callback._events.append(event)
                    else:
                        self._event_handlers.remove(handler)

    def subscribe_topic(self, topic_id: int, is_user_topic: bool = False) -> None:
        commentable_type = "user" if is_user_topic else "topic"
        self._startup_handlers.append(
            self._faye.subscribe(f"/{commentable_type}-{topic_id}")
        )

    def command(
        self,
        commands: Union[List[str], str],
        ignore_case: bool = True,
        event: Union[str, EventType] = EventType.NEW,
    ):
        def decorator(callback):
            nonlocal commands, event

            if not any([callback == h.callback for h in self._event_handlers]):
                if isinstance(commands, str):
                    commands = [commands]

                commands = list(map(str.lower, commands)) if ignore_case else commands

                if isinstance(event, str):
                    try:
                        event = EventType(event)
                    except ValueError:
                        pass

                def cmd_check(e: Event) -> bool:
                    if e.event_type != event:
                        return False

                    text = e.text.lower() if ignore_case else e.text

                    cmd_prefix = None
                    for prefix in self._prefixes:
                        if text.startswith(prefix):
                            cmd_prefix = prefix
                            break

                    if cmd_prefix == None:
                        return False

                    if text.lstrip(cmd_prefix) in commands:
                        return True

                    return False

                self._event_handlers.append(Handler(event, callback, cmd_check))

            return callback

        return decorator

    def wait_for(
        self,
        event: Union[str, EventType],
        check: Optional[Callable[..., bool]] = None,
        timeout: Optional[float] = None,
    ) -> Awaitable[Event]:
        future = asyncio.get_running_loop().create_future()

        if check is None:
            check = lambda _: True

        if isinstance(event, str):
            try:
                event = EventType(event)
            except ValueError:
                pass

        self._event_handlers.append(Handler(event, future, check))

        return asyncio.wait_for(future, timeout)

    def iter_wait_for(
        self,
        event: Union[str, EventType],
        check: Optional[Callable[..., bool]] = None,
        number: Optional[int] = None,
        timeout: Optional[int] = None,
    ) -> IterHandler:
        if check is None:
            check = lambda _: True

        if isinstance(event, str):
            try:
                event = EventType(event)
            except ValueError:
                pass

        iter_handler = IterHandler(number, timeout)

        self._event_handlers.append(Handler(event, iter_handler, check))

        return iter_handler
