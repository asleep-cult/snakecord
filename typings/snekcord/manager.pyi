import asyncio
from types import FrameType
from typing import ClassVar, Dict, List, Optional, Type

from .states.basestate import BaseState
from .utils import EventDispatcher

StateClasses = Dict[str, Type[BaseState]]

class client(EventDispatcher):
    DEFAULT_CLASSES: ClassVar[StateClasses]
    __classes__: ClassVar[StateClasses]
    __handled_signals__: List[int]

    def __init__(
        self, token: str, *, loop: Optional[asyncio.AbstractEventLoop] = ..., api_version: str = ...
    ) -> None: ...

    @classmethod
    def set_class(cls, name: str, klass: type) -> None: ...
    @classmethod
    def get_class(cls, name: str) -> Type[BaseState]: ...
    @classmethod
    def add_handled_signal(cls, int) -> None: ...
    def _repropagate(self) -> None: ...
    def _sighandle(self, signo: int, frame: FrameType) -> None: ...
    async def close(self) -> None: ...
    async def finalize(self) -> None: ...
    def run_forever(self) -> None: ...
