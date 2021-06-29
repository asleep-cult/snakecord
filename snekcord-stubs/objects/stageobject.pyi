from __future__ import annotations

import typing as t

from .baseobject import BaseObject
from .channelobject import GuildChannel
from .guildobject import Guild
from ..states.stagestate import StageInstanceState
from ..utils.enum import Enum
from ..utils.json import JsonField
from ..utils.snowflake import Snowflake


class StageInstancePrivacyLevel(Enum[int]):
    PUBLIC: t.ClassVar[int]
    GUILD_ONLY: t.ClassVar[int]


class StageInstance(BaseObject[Snowflake]):
    guild_id: JsonField[Snowflake]
    channel_id: JsonField[Snowflake]
    topic: JsonField[str]
    privacy_level: JsonField[StageInstancePrivacyLevel]
    discoverable_disabled: JsonField[bool]

    state: StageInstanceState

    def __init__(self, *, state: StageInstanceState) -> None: ...

    @property
    def guild(self) -> Guild | None: ...

    @property
    def channel(self) -> GuildChannel: ...

    async def fetch(self) -> StageInstance: ...

    async def modify(self, **kwargs: t.Any) -> StageInstance: ...

    async def delete(self) -> None: ...
