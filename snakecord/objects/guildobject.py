from .baseobject import BaseObject
from .. import rest
from ..state.channelstate import GuildChannelState
from ..templates import GuildPreviewTemplate, GuildTemplate
from ..utils import _validate_keys


class Guild(BaseObject, template=GuildTemplate):
    def __init__(self, *, state):
        super().__init__(state=state)
        self.channels = GuildChannelState(
            superstate=self._state.manager.channels,
            guild=self)

    async def modify(self, **kwargs):
        keys = rest.modify_guild.keys

        _validate_keys(f'{self.__class__.__name__}.modify',
                       kwargs, (), keys)

        data = await rest.modify_guild.request(
            session=self._state.manager.rest,
            fmt=dict(guild_id=self.id),
            json=kwargs)

        return self.append(data)

    async def delete(self):
        await rest.delete_guild.request(
            session=self._state.manager.rest,
            fmt=dict(guild_id=self.id))

    def to_preview_dict(self):
        return GuildPreviewTemplate.to_dict(self)

    def update(self, data, *args, **kwargs):
        super().update(data, *args, **kwargs)

        for channel in self._channels:
            channel = self._state.manager.channels.append(channel)
            self.channels.add_key(channel.id)

        self._channels.clear()