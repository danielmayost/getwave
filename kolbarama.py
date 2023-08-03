from typing import List
from station import RadioStation, Broadcast, ProgressCallback

# The 'Kol-Barama' archive has been down for ages, 
# when it does come back up, I (or someone else) will do it

class KolBaramaStation(RadioStation):
    def __init__(self) -> None:
        super().__init__("Kol-Barama")
        self._program_list: List[str] = []

    def load_programs(self) -> List[str]:
        raise NotImplementedError("not implemented yet")

    def load_broadcasts(self, program: str | int, progress: ProgressCallback | None = None) -> List[Broadcast]:
        raise NotImplementedError("not implemented yet")