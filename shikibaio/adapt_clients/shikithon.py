from typing import Any, Dict

from pydantic import BaseModel
from shikithon import ShikimoriAPI

from shikibaio.adapt_clients.base import BaseAdapt


class ShikithonAdapt(BaseAdapt):
    def __init__(self, client: ShikimoriAPI) -> None:
        self._client = client

    async def open(self):
        return await self._client.open()

    async def close(self) -> None:
        await self._client.close()

    async def my_info(self) -> Dict[str, Any]:
        return self.to_dict(await self._client.users.current())

    async def get_comment(self, comment_id: int) -> Dict[str, Any]:
        return self.to_dict(await self._client.comments.get(comment_id=comment_id))

    async def create_comment(
        self,
        body: str,
        commentable_id: int,
        commentable_type: str,
        is_offtopic: bool = False,
        broadcast: bool = False,
    ) -> Dict[str, Any]:
        return self.to_dict(
            await self._client.comments.create(
                body=body,
                commentable_id=commentable_id,
                commentable_type=commentable_type,
                is_offtopic=is_offtopic,
                broadcast=broadcast,
            )
        )

    def to_dict(self, model: BaseModel) -> Dict[str, Any]:
        return model.dict()
