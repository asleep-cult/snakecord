from __future__ import annotations

import typing as t

from ..clients.client import Client

__all__ = ('BaseState', 'BaseSubState')

KT = t.TypeVar('KT')
VT = t.TypeVar('VT')
DT = t.TypeVar('DT')


class _StateCommon(t.Generic[KT, VT]):
    def __contains__(self, value) -> t.NoReturn: ...

    def first(self, func: t.Callable[[VT], bool] | None = ...) -> VT | None: ...


class BaseState(_StateCommon[KT, VT]):
    _mapping_: t.ClassVar[type[t.MutableMapping[KT, VT]]] = dict

    client: Client
    mapping: _mapping_

    def __init__(self, *, client: Client) -> None: ...

    def __iter__(self) -> t.Iterator[VT]: ...

    def __reversed__(self) -> t.Iterator[VT]: ...

    def __getitem__(self, key: KT) -> VT: ...

    def __len__(self) -> int: ...

    @t.overload
    def get(self, key: KT) -> VT | None: ...

    @t.overload
    def get(self, key: KT, default: DT) -> VT | DT: ...

    def keys(self) -> t.Iterable[KT]: ...

    def values(self) -> t.Iterable[VT]: ...

    def items(self) -> t.Iterable[tuple[KT, VT]]: ...

    def upsert(self, *args: t.Any, **kwargs: t.Any) -> VT: ...

    def clear(self) -> None: ...


class BaseSubState(_StateCommon[KT, VT]):
    superstate: BaseState[KT, VT]

    def __init__(self, *, superstate: BaseState[KT, VT]) -> None: ...

    def __iter__(self) -> t.Iterator[VT]: ...

    def __reversed__(self) -> t.Iterator[VT]: ...

    def __getitem__(self, key: KT) -> VT: ...

    def __len__(self) -> int: ...

    @t.overload
    def get(self, key: KT) -> VT | None: ...

    @t.overload
    def get(self, key: KT, default: DT) -> VT | DT: ...

    def keys(self) -> t.Iterable[KT]: ...

    def values(self) -> t.Iterable[VT]: ...

    def items(self) -> t.Iterable[tuple[KT, VT]]: ...
