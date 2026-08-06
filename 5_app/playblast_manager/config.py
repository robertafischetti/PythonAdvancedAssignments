"""---------------------------------------------------------------------------------------
 Module: config

 Author = Roberta Fischetti

 Date = 2026-08-06

 Description = Load yaml and expose settings.
---------------------------------------------------------------------------------------"""
import yaml
from pathlib import Path

# VARIABLES ------------------------------------------------------------------------------
CONFIG_PATH = Path(__file__).parent / "config.yaml"


# FUNCTIONS ------------------------------------------------------------------------------
def load_config():
    with open(CONFIG_PATH) as f:
        return yaml.safe_load(f)

config = load_config()
