import json
from dataclasses import dataclass, field
from typing import List

from dataclasses_json import LetterCase, dataclass_json
from loguru import logger


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass()
class ColourConfig:
    contents: str = ""
    capacity_grams: int = 0
    idx: int = 0
    intensity: int = 255
    colour_list: List[int] = field(default_factory=lambda: [0, 0, 0])
    rgb_string: str = field(init=False)

    def __post_init__(self):
        self.colour_list[self.idx] = self.intensity
        self.rgb_string = f"rgb{tuple(self.colour_list)}"


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass()
class Colours:
    red: ColourConfig = field(default_factory=ColourConfig)
    green: ColourConfig = field(default_factory=ColourConfig)
    blue: ColourConfig = field(default_factory=ColourConfig)


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass()
class HardwareLink:
    host: str = "mechanic"
    port: int = 5000


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass()
class Twin:
    colours: Colours = field(default_factory=Colours)
    hardware_api: HardwareLink = field(default_factory=HardwareLink)
    welcome_text: str = ""

    @classmethod
    def from_local(cls):
        with open("config.json", "r") as json_file:
            config = json.load(json_file)
        return cls.from_dict(config)

    def log(self):
        logger.info(f"MODULE TWIN\n{json.dumps(self.to_dict(), indent=4)}")
