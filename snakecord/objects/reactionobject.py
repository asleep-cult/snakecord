from ..utils import JsonField, JsonTemplate


ReactionTemplate = JsonTemplate(
    count=JsonField('count'),
    me=JsonField('me'),
    emoji=JsonField('emoji')
)
