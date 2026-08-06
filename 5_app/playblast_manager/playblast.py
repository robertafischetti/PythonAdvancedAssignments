"""---------------------------------------------------------------------------------------
 Module: simple_playblast_tool

 Author = Roberta Fischetti

 Date = 2026-08-06

 Description = First draft of the picre application.
---------------------------------------------------------------------------------------"""
import os
import getpass

import maya.cmds as cmds

from .maya_utils import *
from .burnins import burn_in_with_ffmpeg
from .file_utils import resolve_output_path


# FUNCTIONS ------------------------------------------------------------------------------
def generate_playblast(project: str, sequence: str, shot: str, burnin_fields: list, artist=None) -> str:
    """
    The main function. Works out where to save the file, reads the
    scene, records a clean raw playblast (no HUDs at all), burns in the
    selected fields with ffmpeg, and returns the path it saved to.
    """

    folder, filename, version_number = resolve_output_path(project, sequence, shot)

    if not os.path.isdir(folder):
        try:
            os.makedirs(folder)
        except OSError as error:
            raise RuntimeError(
                f"Couldn't create the output folder:\n{folder}\n\n"
                f"Original error: {error}"
            )

    final_path = os.path.join(folder, filename)
    raw_path = os.path.join(folder, "_raw_" + filename)

    camera = get_active_camera()
    frame_start, frame_end = get_frame_range()
    width, height = get_resolution()
    artist = artist or getpass.getuser()

    # Hide every HUD -- ours and Maya's own defaults alike -- so the raw
    # capture is a completely clean plate. Only ffmpeg's text will end
    # up in the final video; whatever Maya happens to have on screen
    # never leaks through. Always restored afterward, success or not.
    saved_hud_state = hide_all_huds()
    try:
        actual_raw_path = cmds.playblast(
            filename=raw_path,
            format="qt",
            startTime=frame_start, endTime=frame_end,
            width=width, height=height,
            percent=100, quality=100,
            showOrnaments=False,
            viewer=False,
        )
    finally:
        restore_huds(saved_hud_state)

    burn_in_with_ffmpeg(actual_raw_path, final_path, burnin_fields, shot, camera, artist, frame_start)

    print(f"Saved playblast (v{version_number}) to: {final_path}")
          
    return final_path



