"""---------------------------------------------------------------------------------------
 Module: file_utils

 Author = Roberta Fischetti

 Date = 2026-08-06

 Description = Everything related to folders and filenames, that is information about
                where the file goes and what version it should be.
---------------------------------------------------------------------------------------"""
import os
import platform

import maya.cmds as cmds

from playblast_manager.config import config


# VARIABLES ------------------------------------------------------------------------------
system = platform.system()

settings = {
    **config,
    **config["platforms"][system],
}

FOLDER_PATTERN = settings["folder_pattern"]
FILENAME_PATTERN = settings["filename_pattern"]
VERSION_PADDING = settings["version_padding"]


# FUNCTIONS ------------------------------------------------------------------------------
def get_default_project_root() -> str:
    """
    Maya always has a 'current project' folder set (see File > Set
    Project), and it's always a real, absolute path on disk. Using it as
    the starting value for the Project field means the field never
    starts out as just a bare word like 'dragonfly' that looks like a
    name but isn't actually a real folder anywhere.
    """
    return cmds.workspace(query=True, rootDirectory=True)


def get_next_version(folder: str, shot: str) -> int:
    """
    Look inside `folder` for files already named like sh0210_v001.mov,
    sh0210_v002.mov, etc., and return the next number to use.

    If the folder doesn't exist yet, or nothing matches, start at 1.
    Never reuses a number -- even if v002 was deleted, the next one
    after v001 and v003 is still v004, not v002. Reusing a number would
    mean silently overwriting a file someone might be reviewing.
    """
    if not os.path.isdir(folder):
        return 1 # : Exits the current function, returning an error status code 

    highest_found = 0
    prefix = shot + "_v"   # e.g. "sh0210_v"

    for filename in os.listdir(folder): # list all files and directories in folder
        if filename.startswith(prefix) and filename.endswith(".mov"):
            # A matching filename looks like "sh0210_v003.mov".
            # Chop off the prefix ("sh0210_v") and the ending (".mov"),
            # leaving just the number part, e.g. "003".
            version_text = filename[len(prefix):-len(".mov")]
            if version_text.isdigit():
                version_number = int(version_text)
                if version_number > highest_found:
                    highest_found = version_number

    return highest_found + 1


def resolve_output_path(project: str, sequence: str, shot: str) -> tuple[str, str, int]:
    """Work out the full folder + filename + version for this playblast."""
    if not os.path.isabs(project):      
        raise RuntimeError(
            f"Project needs to be a full folder path, starting from the "
            "very top (e.g. /Users/you/Desktop/dragonfly on Mac, or "
            "C:/projects/dragonfly on Windows) -- not just a name.\n"
            "You entered: '{project}'"
        )

    folder = FOLDER_PATTERN.format(project=project, sequence=sequence, shot=shot)
    shot_name = FILENAME_PATTERN.format(shot=shot)

    version_number = get_next_version(folder, shot_name)
    version_text = "v" + str(version_number).zfill(VERSION_PADDING)
    filename = f"{shot_name}_{version_text}.mov"

    return folder, filename, version_number