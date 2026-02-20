from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, List, Union

class Audience(Enum):
    EXECUTIVE = "executive"
    TEAM = "team"
    EXTERNAL = "external"
    MIXED = "mixed"

class Goal(Enum):
    PERSUADE = "persuade"
    INFORM = "inform"
    DECIDE = "decide"
    INSPIRE = "inspire"

class Tone(Enum):
    BOLD = "bold"
    CALM = "calm"
    URGENT = "urgent"

class CutPolicy(Enum):
    RUTHLESS = "ruthless"
    BALANCED = "balanced"
    PRESERVE_ALL = "preserve-all"

@dataclass
class InputContract:
    source_md: str
    audience: Audience = Audience.TEAM
    goal: Goal = Goal.INFORM
    time_minutes: int = 15
    slide_budget: Union[str, int] = "auto"
    tone: Tone = Tone.CALM
    cut_policy: CutPolicy = CutPolicy.BALANCED

    def __post_init__(self):
        if self.slide_budget == "auto":
            self.slide_budget = int(self.time_minutes * 1.5)
