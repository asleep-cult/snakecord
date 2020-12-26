from .user import User
from .invite import ChannelInviteState

from .message import (
    MessageState,
    Message
)

from .bases import (
    BaseObject,
    BaseState
)

from .utils import (
    JsonField,
    JsonArray,
    Snowflake,
    JsonStructure,
    _try_snowflake
)

from .voice import (
    VoiceConnection,
    VoiceState,
    VoiceServerUpdate
)

from typing import (
    Union,
    Iterable,
    List,
    Optional,
    TYPE_CHECKING
)

if TYPE_CHECKING:
    from .guild import Guild


# TODO: add NewsChannel?, add ChannelRecipientState

class ChannelType:
    GUILD_TEXT = 0	
    DM = 1	
    GUILD_VOICE = 2
    GROUP_DM = 3
    GUILD_CATEGORY = 4
    GUILD_NEWS = 5
    GUILD_STORE = 6


class PermissionFlag:
    CREATE_INSTANT_INVITE = 0x00000001
    KICK_MEMBERS = 0x00000002	
    BAN_MEMBERS = 0x00000004	
    ADMINISTRATOR = 0x00000008	
    MANAGE_CHANNELS = 0x00000010
    MANAGE_GUILD = 0x00000020
    ADD_REACTIONS = 0x00000040	
    VIEW_AUDIT_LOG = 0x00000080
    PRIORITY_SPEAKER = 0x00000100
    STREAM = 0x00000200
    VIEW_CHANNEL = 0x00000400
    SEND_MESSAGES = 0x00000800
    SEND_TTS_MESSAGES = 0x00001000
    MANAGE_MESSAGES = 0x00002000
    EMBED_LINKS = 0x00004000
    ATTACH_FILES = 0x00008000
    READ_MESSAGE_HISTORY = 0x00010000
    MENTION_EVERYONE = 0x00020000
    USE_EXTERNAL_EMOJIS = 0x00040000
    VIEW_GUILD_INSIGHTS = 0x00080000
    CONNECT = 0x00100000
    SPEAK = 0x00200000
    MUTE_MEMBERS = 0x00400000
    DEAFEN_MEMBERS = 0x00800000
    MOVE_MEMBERS = 0x01000000
    USE_VAD = 0x02000000
    CHANGE_NICKNAME = 0x04000000
    MANAGE_NICKNAMES = 0x08000000
    MANAGE_ROLES  = 0x10000000
    MANAGE_WEBHOOKS = 0x20000000
    MANAGE_EMOJIS = 0x40000000


class GuildChannel(BaseObject):
    __json_slots__ = (
        '_state', 'id', 'name', 'guild_id', 'permission_overwrites', 'position',
        'nsfw', 'parent_id', 'type'
    )

    name: str = JsonField('name')
    guild_id: Snowflake = JsonField('guild_id', Snowflake, str)
    _permission_overwrites = JsonField('permission_overwrites')
    position: int = JsonField('position')
    nsfw = JsonField('nsfw')
    parent_id: Snowflake = JsonField('parent_id', Snowflake, str)
    type = JsonField('type')

    def __init__(self, *, state, guild=None):
        self._state: ChannelState = state
        self.messages: Iterable[Message] = MessageState(state._client, self)
        self.guild: 'Guild' = guild or state._client.guilds.get(self.guild_id)
        self.permission_overwrites = PermissionOverwriteState(self._state._client, self)

        for overwrite in self._permission_overwrites:
            self.permission_overwrites._add(overwrite)

        del self._permission_overwrites

    @property
    def mention(self) -> str:
        return '<#{0}>'.format(self.id)

    async def delete(self) -> None:
        rest = self._state._client.rest
        await rest.delete_channel(self.id)


class PermissionOverwrite(BaseObject):
    __json_slots__ = ('id', 'type', 'deny', 'allow')

    allow: int = JsonField('allow', int, str)
    deny: int = JsonField('deny', int, str)
    type: str = JsonField('type')

    create_instant_invite: Optional[bool]
    kick_members: Optional[bool]
    ban_members: Optional[bool]
    administrator: Optional[bool]
    manage_channels: Optional[bool]
    manage_guild: Optional[bool]
    add_reactions: Optional[bool]
    view_audit_log: Optional[bool]
    priority_speaker: Optional[bool]
    stream: Optional[bool]
    view_channel: Optional[bool]
    send_messages: Optional[bool]
    send_tts_messages: Optional[bool]
    manage_messages: Optional[bool]
    embed_links: Optional[bool]
    attach_files: Optional[bool]
    read_message_history: Optional[bool]
    mention_everyone: Optional[bool]
    use_external_emojis: Optional[bool]
    view_guild_insights: Optional[bool]
    connect: Optional[bool]
    speak: Optional[bool]
    mute_members: Optional[bool]
    deafen_members: Optional[bool]
    move_members: Optional[bool]
    use_vad: Optional[bool]
    change_nickname: Optional[bool]
    manage_nicknames: Optional[bool]
    manage_roles: Optional[bool]
    manage_webhooks: Optional[bool]
    manage_emojis: Optional[bool]

    def __init__(self, state):
        self._state = state

        for name, flag in PermissionFlag.__dict__.items():
            if name.startswith('_'):
                continue

            allowed = (flag | self.deny) == flag
            denied = (flag | self.allow) == flag

            if allowed:
                setattr(self, name.lower(), True)
            elif denied:
                setattr(self, name.lower(), False)
            else:
                setattr(self, name.lower(), None)

    async def edit(self, overwrite):
        rest = self._state._client.rest
        await rest.edit_channel_permissions(self._state._channel.id, self.id, overwrite.allow, overwrite.deny, overwrite.type)

    async def delete(self):
        rest = self._state._client.rest
        await rest.delete_channel_permission(self._state._channel.id, self.id)


class PermissionOverwriteState(BaseState):
    def __init__(self, client, channel):
        super().__init__(client)
        self._channel = channel

    def _add(self, data):
        overwrite = self.get(data['id'])
        if overwrite is not None:
            overwrite._update(data)
            return overwrite
        overwrite = PermissionOverwrite.unmarshal(data, state=self)
        self._values[overwrite.id] = overwrite
        return overwrite


class TextChannel(GuildChannel):
    __json_slots__ = (*GuildChannel.__json_slots__, 'last_message_id')

    last_message_id: Snowflake = JsonField('last_message_id', Snowflake, str)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.invites = ChannelInviteState(self._state._client.invites, self)

    async def edit(
        self, 
        *, 
        name=None, 
        channel_type=None, 
        position=None, 
        topic=None, 
        nsfw=None, 
        slowmode=None, 
        permission_overwrites=None, 
        perent=None
    ) -> None:
        rest = self._state._client.rest

        if perent is not None:
            perent = perent.id

        resp = await rest.modify_channel(
            self.id, name=name, channel_type=channel_type, 
            position=position, topic=topic, nsfw=nsfw, 
            slowmode=slowmode, permission_overwrites=permission_overwrites,
            perent_id=perent
        )
        data = await resp.json()
        message = self.messages._add(data)
        return message

    async def send(self, content=None, *, nonce=None, tts=False, embed=None) -> None:
        rest = self._state._client.rest
        if embed is not None:
            embed = embed.to_dict()
        resp = await rest.send_message(self.id, content=content, nonce=nonce, tts=tts, embed=embed)
        data = await resp.json()
        message = self.messages._add(data)
        return message

    async def trigger_typing(self):
        rest = self._state._client.rest
        await rest.trigger_typing(self.id)


class VoiceChannel(GuildChannel):
    __json_slots__ = (*GuildChannel.__json_slots__, 'bitrate', 'user_limit')

    bitrate: int = JsonField('bitrate')
    user_limit: int = JsonField('user_limit')

    async def connect(self):
        voice_state_update, voice_server_update = await self.guild.shard.update_voice_state(self.guild.id, self.id)
        state_data = await voice_state_update
        server_data = await voice_server_update
        voice_state = VoiceState.unmarshal(state_data.data, voice_channel=self)
        voice_server = VoiceServerUpdate.unmarshal(server_data.data)
        self.voice_connection = VoiceConnection(voice_state, voice_server)
        await self.voice_connection.connect()
        return self.voice_connection

    async def edit(
        self,
        channel_id,
        *,
        name=None,
        channel_type=None,
        position=None,
        topic=None,
        nsfw=None,
        bitrate=None,
        user_limit=None,
        permission_overwrites=None,
        parent=None
    ):
        rest = self._state._client.rest

        if parent is not None:
            parent = parent.id

        resp = await rest.modify_channel(
            self.id, name=name, channel_type=channel_type,
            position=position, topic=topic, nsfw=nsfw, 
            bitrate=bitrate, user_limit=user_limit, 
            permission_overwrites=permission_overwrites,
            parent_id=parent
        )
        data = await resp.json()
        channel = self._state._add(data, guild=self.guild)
        return channel


class CategoryChannel(GuildChannel):
    async def edit(
        self, 
        *, 
        name=None, 
        channel_type=None, 
        position=None, 
        topic=None, 
        nsfw=None, 
        slowmode=None, 
        permission_overwrites=None, 
    ) -> None:
        rest = self._state._client.rest
        resp = await rest.modify_channel(
            self.id, name=name, channel_type=channel_type, 
            position=position, topic=topic, nsfw=nsfw, 
            slowmode=slowmode, permission_overwrites=permission_overwrites,
        )
        data = await resp.json()
        channel = self._state._add(data, guild=self.guild)
        return channel


class DMChannel(BaseObject):
    __json_slots__ = (*GuildChannel.__json_slots__, 'last_message_id', 'type', '_recipients', 'recipients')

    last_message_id: Snowflake = JsonField('last_message_id', Snowflake, str)
    type: int = JsonField('type')
    _recipients = JsonArray('recipients')

    def __init__(self, state):
        self._state: ChannelState = state
        self.recipients = ChannelRecipientState(self._state.client, channel=self)

        for recipient in self._recipients:
            self.recipients._add(recipient)

        del self._recipients


class ChannelRecipientState(BaseState):
    def __init__(self, client, channel):
        super().__init__(client)
        self._channel = channel

    def _add(self, data):
        user = self._client.users._add(data)
        self._values[user.id] = user
        return user

    async def add(self, user, access_token, *, nick):
        rest = self._client.rest
        await rest.add_dm_recipient(self._channel.id, user.id, access_token, nick)

    async def remove(self, user):
        rest = self._client.rest
        await rest.remove_dm_recipient(self._channel.id, user.id)


_CHANNEL_TYPE_MAP = {
    ChannelType.GUILD_TEXT: TextChannel,
    ChannelType.DM: DMChannel,
    ChannelType.GUILD_VOICE: VoiceChannel,
    ChannelType.GUILD_CATEGORY: CategoryChannel
}


class ChannelState(BaseState):
    def __init__(self, client):
        super().__init__(client)

    def _add(self, data, *args, **kwargs):
        channel = self.get(data['id'])
        if channel is not None:
            channel._update(data)
            return channel
        cls = _CHANNEL_TYPE_MAP.get(data['type'])
        channel = cls.unmarshal(data, *args, state=self, **kwargs)
        self._values[channel.id] = channel
        return channel

    async def fetch(self, channel_id):
        data = await self._client.rest.get_channel(channel_id)
        return self._add(data)

class GuildChannelState:
    def __init__(self, channel_state, guild):
        self._channel_state = channel_state
        self._guild = guild

    def __iter__(self):
        for channel in self._channel_state:
            if channel.guild == self._guild:
                yield channel

    async def fetch_all(self):
        rest = self._channel_state._client.rest
        resp = await rest.get_guild_channels(self._guild.id)
        data = await resp.json()
        channels = []
        for channel in data:
            channel = self._channel_state._add(channel)
            channels.append(channel)
        return channels

    async def create(
        self,
        *,
        name=None, 
        channel_type=None,
        topic=None,
        bitrate=None,
        user_limit=None,
        slowmode=None,
        position=None,
        permission_overwrites=None,
        parent=None,
        nsfw=None
    ):
        rest = self._channel_state._client.rest

        if parent is not None:
            parent = parent.id

        await rest.create_guild_channel(
            self._guild.id, name=name, channel_type=channel_type,
            topic=topic, bitrate=bitrate, user_limit=user_limit,
            slowmode=slowmode, position=position, permission_overwrites=permission_overwrites,
            parent=parent, nsfw=nsfw
        )

    async def modify_positions(self, positions):
        rest = self._channel_state._client.rest
        await rest.modify_guild_channel_positions(self._guild.id, positions)

_Channel = Union[DMChannel, CategoryChannel, VoiceChannel, TextChannel, GuildChannel]
