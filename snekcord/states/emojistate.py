from .basestate import BaseState
from .. import rest
from ..clients.client import ClientClasses
from ..objects.emojiobject import BaseEmoji, UnicodeEmoji
from ..resolvers import resolve_emoji, resolve_image_data
from ..utils import Snowflake

try:
    import snekcord.emojis as _emojis  # type: ignore
except ImportError:
    _emojis = None

__all__ = ('GuildEmojiState',)


def _class_init_(surrogates, name):
    if _emojis is not None:
        for category, emojis in _emojis.ALL_CATEGORIES.items():
            for data in emojis:
                emoji = UnicodeEmoji(category=category, data=data)
                emoji._store(surrogates, name)


class GuildEmojiState(BaseState):
    UNICODE_EMOJIS_BY_SURROGATES = {}
    UNICODE_EMOJIS_BY_NAME = {}

    _class_init_(UNICODE_EMOJIS_BY_SURROGATES, UNICODE_EMOJIS_BY_NAME)

    def __init__(self, *, client, guild):
        super().__init__(client=client)
        self.guild = guild

    @classmethod
    def get_unicode_emoji(cls, data, default=None):
        if isinstance(data, str):
            emoji = cls.UNICODE_EMOJIS_BY_NAME.get(data.strip(':'))

            if emoji is not None:
                return emoji

            data = data.encode()

        if isinstance(data, bytes):
            emoji = cls.UNICODE_EMOJIS_BY_SURROGATES.get(data)

            if emoji is not None:
                return emoji

            return ClientClasses.PartialUnicodeEmoji(surrogates=data)

        return default

    def upsert(self, data):
        emoji_id = data['id']

        if emoji_id is not None:
            emoji = self.get(Snowflake(emoji_id))

            if emoji is not None:
                emoji.update(data)
            else:
                emoji = ClientClasses.GuildEmoji.unmarshal(data, state=self)
                emoji.cache()
        else:
            emoji = self.get_unicode_emoji(data['name'].encode())

        return emoji

    async def fetch(self, emoji):
        emoji_id = Snowflake.try_snowflake(emoji)

        data = await rest.get_guild_emoji.request(
            self.client.rest, {'guild_id': self.guild.id, 'emoji_id': emoji_id}
        )

        return self.upsert(data)

    async def fetch_all(self):
        data = await rest.get_guild_emojis.request(
            self.client.rest, {'guild_id': self.guild.id}
        )

        return [self.upsert(emoji) for emoji in data]

    async def create(self, *, name, image, roles=None):
        json = {'name': str(name)}

        json['image'] = await resolve_image_data(image)

        if roles is not None:
            json['roles'] = Snowflake.try_snowflake_many(roles)

        data = await rest.create_guild_emoji.request(
            self.client.rest, {'guild_id': self.guild.id}, json=json
        )

        return self.upsert(data)

    async def delete(self, emoji):
        emoji_id = Snowflake.try_snowflake(emoji)

        await rest.delete_guild_emoji.request(
            self.client.rest, {'guild_id': self.guild.id, 'emoji_id': emoji_id}
        )

    def resolve(self, emoji):
        if isinstance(emoji, BaseEmoji):
            return emoji

        if isinstance(emoji, int):
            return self.get(emoji)

        if isinstance(emoji, str):
            data = resolve_emoji(emoji)

            if data is not None:
                emoji = self.get(data['id'])

                if emoji is not None:
                    return emoji

                return ClientClasses.PartialGuildEmoji(client=self.client, **data)

        return self.get_unicode_emoji(emoji)
