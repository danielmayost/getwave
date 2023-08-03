from abc import ABC, abstractmethod
from typing import List, NamedTuple
from utils import ProgressCallback

Broadcast = NamedTuple("Broadcast", [("name", str), ("url", str)])

class RadioStation(ABC):
    def __init__(self, name: str) -> None:
        self.name = name

    @abstractmethod
    def load_programs(self) -> List[str]:
        pass

    @abstractmethod
    def load_broadcasts(self, program: str | int, progress: ProgressCallback | None = None) -> List[Broadcast]:
        pass