from .baseobject import BaseObject
from ..utils.bitset import Bitset, Flag
from ..utils.enum import Enum
from ..utils.json import JsonField

__all__ = ('User',)


class UserFlags(Bitset):
    discord_employee = Flag(0)
    partnered_server_owner = Flag(1)
    hypesquad_events = Flag(2)
    bug_hunter_level_1 = Flag(3)
    mfa_sms = Flag(4)
    premium_promo_dismissed = Flag(5)
    house_bravery = Flag(6)
    house_brilliance = Flag(7)
    house_balance = Flag(8)
    early_supporter = Flag(9)
    team_user = Flag(10)
    has_unread_urgent_message = Flag(13)
    bug_hunter_level_2 = Flag(14)
    verified_bot = Flag(16)
    early_verified_bot_developer = Flag(17)
    discord_certified_moderator = Flag(18)


class PremiumType(Enum[int]):
    NONE = 0
    NITRO_CLASSIC = 1
    NITRO = 2


class User(BaseObject):
    name = JsonField('username')
    discriminator = JsonField('discriminator')
    avatar = JsonField('avatar')
    bot = JsonField('bot')
    system = JsonField('system')
    mfa_enabled = JsonField('mfa_enabled')
    locale = JsonField('locale')
    verified = JsonField('verified')
    email = JsonField('email')
    flags = JsonField('flags', UserFlags.from_value)
    premium_type = JsonField('premium_type', PremiumType.get_enum)
    public_flags = JsonField('public_flags', UserFlags.from_value)

    def __str__(self):
        return f'@{self.name}'

    @property
    def tag(self):
        return f'{self.name}#{self.id}'

    @property
    def mention(self):
        return f'<@{self.id}>'
