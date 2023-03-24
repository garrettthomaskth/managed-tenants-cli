from dataclasses import dataclass
from pathlib import Path
from typing import Set


@dataclass
class AddonsByType:
    olm: Set[Path]
    package: Set[Path]
