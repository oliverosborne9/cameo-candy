import json
from dataclasses import dataclass, field
from typing import List

from dataclasses_json import LetterCase, dataclass_json
from flask import current_app
from loguru import logger


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass()
class ColourConfig:
    """
    A structure to handle each of the three dispensers,
    their display colours and contents.

    :param contents: The material inside the container to be dispensed
    :param capacity_grams: The mass in grams of one full cup of the material
    :param idx: The position in "RGB" of the display colour (Red=0, Green=1, Blue=2)
    :param intensity: The intensity of the colour to display,
        from 0 to 255 on the brightness channel
    """

    contents: str = ""
    capacity_grams: int = 0
    idx: int = 0
    intensity: int = 255
    rgb_string: str = field(init=False)

    def __post_init__(self):
        """
        Immediately after config is parsed in, populate the RGB string
        to be given to the HTML templates and front-end of the app.
        """
        colour_list: List[int] = [0, 0, 0]
        colour_list[self.idx] = self.intensity
        # e.g. bright red -- rgb(255,0,0)
        self.rgb_string = f"rgb{tuple(colour_list)}"


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass()
class Colours:
    """
    Container and display setup for each of the three colours,
    red, green and blue.
    """

    red: ColourConfig = field(default_factory=ColourConfig)
    green: ColourConfig = field(default_factory=ColourConfig)
    blue: ColourConfig = field(default_factory=ColourConfig)


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass()
class HardwareLink:
    """
    Information allowing connection to the adjacently running
    Raspberry Pi dispensing app, depending on deployment.

    :param host: The host of the RPi web server,
        "mechanic" for Docker container deployment,
        "172.17.0.1" to access localhost of Raspberry Pi
    :param port: The exposed port of the RPi web server
    """

    host: str = "mechanic"
    port: int = 7070

    @property
    def url(self):
        """
        Base URL of the dispensing endpoints of the  Raspberry Pi server.
        """
        return f"http://{self.host}:{self.port}/api/v1/dispense"


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass()
class Twin:
    """
    Dataclass containing all configurable options for this module.
    config.template.json indicates JSON schema.

    :param colours: The structure configuring contents of the containers
        and settings on how to display the colour in the UI
    :param hardware_api: The structure providing the host and port of the
        Raspberry Pi dispensing web server
    :param welcome_text: Message to display to the user on the homepage
    """

    colours: Colours = field(default_factory=Colours)
    hardware_api: HardwareLink = field(default_factory=HardwareLink)
    welcome_text: str = ""

    @classmethod
    def from_local(cls) -> "Twin":
        """
        Method to read module configuration from a local JSON file,
        used on startup of the app.

        :param json_file: Path to the JSON file containing configuration
        :return: The loaded module twin, used to configure the app
        """
        with open("config.json", "r") as json_file:
            config = json.load(json_file)
        return cls.from_dict(config)

    @staticmethod
    def from_current_app() -> "Twin":
        return current_app.config["TWIN"]

    def log(self):
        """
        Write the twin object with its values to the logger in a readable way.
        Used to print an overview of the configuration on startup of the app.
        """
        logger.info(f"MODULE TWIN\n{json.dumps(self.to_dict(), indent=4)}")
