from typing import Any, Dict

import cattrs
from shiki4py import Shikimori

from shikibaio.adapt_clients.base import BaseAdapt


class Shiki4pyAdapt(BaseAdapt):
    def __init__(self, client: Shikimori) -> None:
        self._client = client

    async def open(self):
        return await self._client.open()

    async def close(self) -> None:
        await self._client.close()

    async def my_info(self) -> Any:
        return await self._client.users.my_info()

    async def get_comment(self, comment_id: int) -> Any:
        return await self._client.comments.show_one(comment_id=comment_id)

    async def create_comment(
        self,
        body: str,
        commentable_id: int,
        commentable_type: str,
        is_offtopic: bool = False,
        broadcast: bool = False,
    ) -> Any:
        return await self._client.comments.create(
            body=body,
            commentable_id=commentable_id,
            commentable_type=commentable_type,
            is_offtopic=is_offtopic,
            broadcast=broadcast,
        )

    def to_dict(self, model: Any) -> Dict[str, Any]:
        return cattrs.unstructure(model)
