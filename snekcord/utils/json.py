import json

__all__ = ('JsonTemplate', 'JsonField', 'JsonArray', 'JsonObject')


class JsonTemplate:
    def __init__(self, *, __extends__=(), **fields):
        self.local_fields = fields
        self.fields = self.local_fields.copy()

        for template in __extends__:
            self.fields.update(template.fields)

    def update(self, obj, data, *, set_defaults=False):
        for name, field in self.fields.items():
            try:
                value = field.unmarshal(data[field.key])
                obj.__fields__.add(field.key)
                setattr(obj, name, value)
            except Exception:
                if set_defaults:
                    default = field.default()

                    if default is not None:
                        obj.__fields__.add(field.key)

                    setattr(obj, name, default)

    def to_dict(self, obj):
        data = {}

        for name, field in self.fields.items():
            if field.key not in obj.__fields__:
                continue

            value = getattr(obj, name, field.default())

            try:
                value = field.marshal(value)
            except Exception:
                continue

            data[field.key] = value

        return data

    def marshal(self, obj, *args, **kwargs):
        return json.dumps(self.to_dict(obj), *args, **kwargs)

    def default_type(self, name='GenericClass'):
        return JsonObjectMeta(name, (JsonObject,), {}, template=self)


class JsonField:
    def __init__(self, key, unmarshal=None, marshal=None, object=None,
                 default=None):
        self.key = key
        self.object = object
        self._default = default

        if self.object is not None:
            self._unmarshal = self.object.unmarshal
            self._marshal = self.object.__template__.to_dict
        else:
            self._unmarshal = unmarshal
            self._marshal = marshal

    def unmarshal(self, value):
        if self._unmarshal is not None and value is not None:
            value = self._unmarshal(value)
        return value

    def marshal(self, value):
        if self._marshal is not None:
            value = self._marshal(value)
        return value

    def default(self):
        if callable(self._default):
            return self._default()
        return self._default


class JsonArray(JsonField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('default', list)
        super().__init__(*args, **kwargs)

    def unmarshal(self, value):
        return [super(JsonArray, self).unmarshal(val) for val in value]

    def marshal(self, value):
        return [super(JsonArray, self).marshal(val) for val in value]


def _flatten_slots(cls, slots=None):
    if slots is None:
        slots = set()

    slots.update(getattr(cls, '__slots__', ()))

    for base in cls.__bases__:
        _flatten_slots(base, slots)

    return slots


class JsonObjectMeta(type):
    def __new__(cls, name, bases, attrs, template=None):
        external_slots = set()
        for base in bases:
            _flatten_slots(base, external_slots)

        slots = tuple(attrs.get('__slots__', ()))
        if template is not None:
            fields = template.fields
            slots += tuple(field for field in fields
                           if field not in slots
                           and field not in external_slots)

        attrs['__slots__'] = slots
        attrs['__template__'] = template

        return type.__new__(cls, name, bases, attrs)


class JsonObject(metaclass=JsonObjectMeta):
    __slots__ = ('__fields__',)

    @classmethod
    def unmarshal(cls, data=None, *args, **kwargs):
        if cls.__template__ is None:
            raise NotImplementedError

        if isinstance(data, (bytes, bytearray, memoryview, str)):
            data = json.loads(data)

        self = cls.__new__(cls)
        self.__fields__ = set()
        cls.__init__(self, *args, **kwargs)
        self.update(data or {}, set_defaults=True)

        return self

    def update(self, *args, **kwargs):
        if self.__template__ is None:
            raise NotImplementedError
        return self.__template__.update(self, *args, **kwargs)

    def to_dict(self):
        if self.__template__ is None:
            raise NotImplementedError
        return self.__template__.to_dict(self)

    def marshal(self, *args, **kwargs):
        if self.__template__ is None:
            raise NotImplementedError
        return self.__template__.marshal(self, *args, **kwargs)
