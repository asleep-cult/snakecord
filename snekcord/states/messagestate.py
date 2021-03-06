from .basestate import BaseState, BaseSubState
from .. import rest
from ..clients.client import ClientClasses
from ..objects.embedobject import Embed, EmbedBuilder
from ..utils import Snowflake, undefined

__all__ = ('MessageState', 'ChannelPinsState')


def _embed_to_dict(embed):
    if isinstance(embed, EmbedBuilder):
        embed = embed.embed

    if isinstance(embed, Embed):
        return embed.to_dict()

    raise TypeError(
        f'embed should be an Embed or EmbedBuilder, got {embed.__class__.__name__!r}'
    )


class MessageState(BaseState):
    def __init__(self, *, client, channel):
        super().__init__(client=client)
        self.channel = channel

    def upsert(self, data):
        message = self.get(Snowflake(data['id']))

        if message is not None:
            message.update(data)
        else:
            message = ClientClasses.Message.unmarshal(data, state=self)
            message.cache()

        return message

    async def fetch(self, message):
        message_id = Snowflake.try_snowflake(message)

        data = await rest.get_channel_message.request(
            self.client.rest,
            {'channel_id': self.channel.id, 'message_id': message_id}
        )

        return self.upsert(data)

    async def fetch_many(
        self, *, around=undefined, before=undefined, after=undefined, limit=undefined
    ):
        params = {}

        if around is not undefined:
            params['around'] = Snowflake.try_snowflake(around, allow_datetime=True)

        if before is not undefined:
            params['before'] = Snowflake.try_snowflake(before, allow_datetime=True)

        if after is not undefined:
            params['after'] = Snowflake.try_snowflake(after, allow_datetime=True)

        if limit is not undefined:
            params['limit'] = int(limit)

        data = await rest.get_channel_messages.request(
            self.client.rest, {'channel_id': self.channel.id}, params=params
        )

        return [self.upsert(message) for message in data]

    async def create(
        self, *, content=undefined, tts=undefined, file=undefined, embed=undefined, embeds=undefined
        # allowed mentions, message_reference, components
    ):
        json = {'embeds': []}

        if content is not undefined:
            json['content'] = str(content)

        if tts is not undefined:
            json['tts'] = bool(tts)

        if embeds is not undefined:
            json['embeds'].extend(map(_embed_to_dict, embeds))

        if embed is not undefined:
            json['embeds'].append(_embed_to_dict(embed))

        if not any((json.get('content'), json.get('file'), json.get('embeds'))):
            raise TypeError('None of (content, file, embed(s)) were provided')

        data = await rest.create_channel_message.request(
            self.client.rest, {'channel_id': self.channel.id}, json=json
        )

        return self.upsert(data)

    async def delete(self, message):
        message_id = Snowflake.try_snowflake(message)

        data = await rest.delete_message.request(
            self.client.rest, {'channel_id': self.channel.id, 'message_id': message_id}
        )

        return self.upsert(data)

    async def bulk_delete(self, messages):
        message_ids = Snowflake.try_snowflake_many(messages)

        if len(message_ids) == 0:
            raise TypeError('bulk_delete requires at least 1 message')

        elif len(message_ids) == 1:
            message_id, = message_ids
            return await self.delete(message_id)

        elif len(message_ids) > 100:
            raise TypeError('bulk_delete can\'t delete more than 100 messages')

        await rest.bulk_delete_messages.request(
            self.client.rest, {'channel_id': self.channel.id}, json={'message_ids': message_ids}
        )


class ChannelPinsState(BaseSubState):
    def __init__(self, *, superstate, channel):
        super().__init__(superstate=superstate)
        self.channel = channel

    async def fetch_all(self):
        data = await rest.get_pinned_messages.request(
            self.superstate.client.rest, {'channel_id': self.channel.id}
        )

        return [self.superstate.upsert(message) for message in data]

    async def add(self, message):
        message_id = Snowflake.try_snowflake(message)

        await rest.add_pinned_message.request(
            self.superstate.client.rest,
            {'channel_id': self.channel.id, 'message_id': message_id}
        )

    async def remove(self, message):
        message_id = Snowflake.try_snowflake(message)

        await rest.remove_pinned_message.request(
            self.superstate.client.rest,
            {'channel_id': self.channel.id, 'message_id': message_id}
        )
