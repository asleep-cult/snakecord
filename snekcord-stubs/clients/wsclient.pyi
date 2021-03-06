import typing as t

from .client import Client
from ..flags import WebSocketIntents
from ..objects.userobject import User
from ..typedefs import Json
from ..ws.shardws import Shard

__all__ = ('WebSocketClient',)


class WebSocketClient(Client):
    shards: dict[int, Shard]
    shard_id: int
    shard_count: int
    intents: WebSocketIntents | None
    timeouts: dict[str, float] | None
    shards: dict[int, Shard]

    def __init__(self, *args: t.Any, **kwargs: t.Any) -> None: ...

    @property
    def user(self) -> User | None: ...

    async def fetch_gateway(self) -> Json: ...

    async def fetch_gateway_bot(self) -> Json: ...

    async def connect(self, *args: t.Any, **kwrags: t.Any) -> None: ...

    def run_forever(self) -> BaseException | None: ...
