"""---------------------------------------------------------------------------------------
 Module: ffmpeg

 Author = Roberta Fischetti

 Date = 2026-08-06

 Description = Works out the full path to the ffmpeg program and 
                makes sure ffmpeg can actually be found and run.
---------------------------------------------------------------------------------------"""
import os
import shutil
import subprocess

from playblast_manager.config import config


# FUNCTIONS ------------------------------------------------------------------------------
def find_ffmpeg() -> str:
    """
    Checks ffmpeg_path (from config.yaml), then PATH, then a few common install locations.
    """
    # 1. Explicit path from config
    ffmpeg_path = config.platform.ffmpeg_path
    if ffmpeg_path:
        return ffmpeg_path
    
    # 2. Search PATH
    found = shutil.which("ffmpeg")
    if found:
        return found

    # 3. Search platform defaults
    common_locations = [
        "/opt/homebrew/bin/ffmpeg",   # Homebrew on Apple Silicon Macs
        "/usr/local/bin/ffmpeg",      # Homebrew on Intel Macs
        "/usr/bin/ffmpeg",            # most Linux installs
    ]
    for path in common_locations:
        if os.path.isfile(path):
            return path
 
    raise RuntimeError(
        "Couldn't find ffmpeg anywhere -- not on Maya's PATH, and not in "
        "any of the usual install locations.\n\n"
        "Open a Terminal and run:  which ffmpeg\n"
        "Then either paste the path it prints into ffmpeg_path near the "
        "top of this file, or add it to config.yaml as:\n"
        "    ffmpeg_bin: /the/folder/it/is/in"
    )
 
def check_ffmpeg_available() -> str:
    """
    Make sure ffmpeg can actually be found and run, and return the exact path to use for it.
    """
    ffmpeg_path = find_ffmpeg()
    try:
        subprocess.run(
            [ffmpeg_path, "-version"], 
            capture_output=True, 
            check=True, #if the program exits with an error, raise an exception
        )
    except FileNotFoundError as not_found_error:
        raise RuntimeError(
            "ffmpeg isn't installed, or isn't on your system's PATH.\n"
            "Install it (e.g. 'brew install ffmpeg' on Mac) and try again."
        ) from not_found_error
    except subprocess.CalledProcessError as process_error:
        raise RuntimeError(
            f"ffmpeg is installed but returned an error: {process_error}"
        ) from process_error

    return ffmpeg_path