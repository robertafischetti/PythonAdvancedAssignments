"""---------------------------------------------------------------------------------------
 Module: burnins

 Author = Roberta Fischetti

 Date = 2026-08-06

 Description = FFmpeg filters.
---------------------------------------------------------------------------------------"""
import os
import time
import subprocess

from playblast_manager.config import config
from playblast_manager.constants import CORNER_POSITIONS, BURNIN_CORNER_FOR_FIELD

from .ffmpeg import check_ffmpeg_available

# VARIABLES ------------------------------------------------------------------------------
font_path = config.platform.font_path


# FUNCTIONS ------------------------------------------------------------------------------
def escape_drawtext(text: str) -> str:
    """
    ffmpeg's drawtext filter treats backslash, colon, and single-quote
    as special characters -- escape them so a shot/artist name with an
    unusual character in it can't accidentally break the filter string.
    """
    text = text.replace("\\", "\\\\")
    text = text.replace(":", "\\:")
    text = text.replace("'", "\\'")
    return text


def one_drawtext(corner: str, literal_text: str) -> str:
    """Build one drawtext filter segment showing literal_text in the given corner."""
    text = escape_drawtext(literal_text)
    position = CORNER_POSITIONS[corner]
    
    return (
       f"drawtext=fontfile='{font_path}':text='{text}':{position}:fontsize=28:fontcolor=white:"
        "box=1:boxcolor=black@0.5:boxborderw=6"
    )


def build_burnin_filters(enabled_fields: list, shot: str, camera: str, artist: str, maya_frame_start: int) -> str:
    """Build the full ffmpeg -vf filter chain for every enabled burn-in field."""
    filters = []

    if "shot_name" in enabled_fields:
        filters.append(one_drawtext(BURNIN_CORNER_FOR_FIELD["shot_name"], shot))
    if "camera_name" in enabled_fields:
        filters.append(one_drawtext(BURNIN_CORNER_FOR_FIELD["camera_name"], camera))
    if "artist" in enabled_fields:
        filters.append(one_drawtext(BURNIN_CORNER_FOR_FIELD["artist"], artist))
    if "date" in enabled_fields:
        today = time.strftime("%Y-%m-%d")
        filters.append(one_drawtext(BURNIN_CORNER_FOR_FIELD["date"], today))
    if "frame" in enabled_fields:
        frame_burnin_position = CORNER_POSITIONS[BURNIN_CORNER_FOR_FIELD["frame"]]
        filters.append(
            f"drawtext=fontfile='{font_path}':text='Frame\\: %{{eif\\:n+{maya_frame_start}\\:d}}':{frame_burnin_position}:"
            "fontsize=28:fontcolor=white:box=1:boxcolor=black@0.5:boxborderw=6"
        )

    return ",".join(filters)


def burn_in_with_ffmpeg(raw_path: str, final_path: str, enabled_fields: list, shot: str, camera: str, artist: str, frame_start: int) -> None:
    """Run ffmpeg once, drawing every enabled field onto the raw playblast."""
    ffmpeg_path = check_ffmpeg_available()
    filter_chain = build_burnin_filters(enabled_fields, shot, camera, artist, frame_start)

    if not filter_chain:
        # Nothing was ticked -- nothing to draw, just use the raw file as-is.
        # move the file instead of processing it
        os.replace(raw_path, final_path)
        return
    
    codec = config.ffmpeg.codec
    pixel_format = config.ffmpeg.pixel_format
    crf = str(config.ffmpeg.crf)

    command = [
        ffmpeg_path, "-y", "-i", raw_path,                      # -y: overwrite existing file, -i: input file = raw path
        "-vf", filter_chain,                                    # -vf: apply video filter, which is filter chain
        "-c:v", codec, "-pix_fmt", pixel_format, "-crf", crf,   # encoding options and video quality
        final_path,                                             # output
    ]

    result = subprocess.run(command, capture_output=True, text=True)

    # Check if FFmpeg succeeded, 0 means success
    if result.returncode != 0: 
        raise RuntimeError("ffmpeg failed while burning in text:\n" + result.stderr[-1500:])

    os.remove(raw_path)