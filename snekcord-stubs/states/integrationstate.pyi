from .basestate import BaseState
from ..clients.client import Client
from ..objects.guildobject import Guild
from ..objects.integrationobject import Integration
from ..utils import Snowflake


class IntegrationState(BaseState[Snowflake, Integration]):
    guild: Guild

    def __init__(self, *, client: Client, guild: Guild) -> None: ...

    async def fetch_all(self) -> list[Integration]: ...
