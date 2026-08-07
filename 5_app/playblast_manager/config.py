"""---------------------------------------------------------------------------------------
 Module: config

 Author = Roberta Fischetti

 Date = 2026-08-06

 Description = Load yaml and expose settings.
---------------------------------------------------------------------------------------"""
import yaml
import platform
from pathlib import Path
from dataclasses import dataclass


# DATACLASSES ----------------------------------------------------------------------------
""" 
Created several configuration classes for the following benefits:
- Autocomplete: instead of guessing dictionary keys, the IDE suggests the available options (also, it reduces typos errors);
- Type checking: all data is clearly documented;
- Readability: config.playblast.folder_pattern is easier to read compared to config["playblast"]["folder_pattern"].

Used a decorator to avoid writing a lot of repetitive code. 
In particular, the @dataclass decorator automatically generates the __init__() method.
It also communicates the classes' intent, that is to hold data.
"""
@dataclass
class FFmpegConfig:
    codec: str
    pixel_format: str
    crf: int

@dataclass
class PlayblastConfig:
    folder_pattern: str
    filename_pattern: str
    version_padding: int

@dataclass
class PlatformConfig:
    ffmpeg_path: str
    font_path: str

@dataclass
class Config:
    ffmpeg: FFmpegConfig
    playblast: PlayblastConfig
    platform: PlatformConfig


# VARIABLES ------------------------------------------------------------------------------
""" 
Used a YAML configuration file to separate code from data.
In this application the data refers to: 
- encoding options and video quality of the playblast;
- naming convention and folder pattern of the generated playblast;
- ffmpeg settings which can vary on different system platforms.
An artist or a producer can easily modify these settings, according to their studio's preferences and systems,
without touching any Python code.
Used YAML instead of JSON because it is easier to read.
"""
CONFIG_PATH = Path(__file__).parent / "config.yaml"


# FUNCTIONS ------------------------------------------------------------------------------
def load_config() -> Config:

    with open(CONFIG_PATH) as file:
        raw = yaml.safe_load(file)

    system = platform.system()

    return Config(
        ffmpeg=FFmpegConfig(**raw["ffmpeg"]),
        playblast=PlayblastConfig(**raw["playblast"]),
        platform=PlatformConfig(**raw["platforms"][system]),
    )


# START ------------------------------------------------------------------------------
config = load_config()
