"""
SIMPLE PLAYBLAST TOOL
=====================
This is a stripped-down, single-file version of the Playblast Manager.
It does the exact same job as the full multi-file version -- capture the
scene, work out the right name and version number, bake in some burn-in
text, and play the shot back to disk -- but with as few moving parts as
possible, so it's easier to read start to finish.

Burn-ins are done with ffmpeg's `drawtext` filter, as a step AFTER Maya
records the raw playblast, rather than with Maya's own on-screen HUDs.
Trade-off worth knowing: this needs ffmpeg installed and on your
system's PATH -- if it isn't, generate_playblast() will say so clearly
rather than failing with a cryptic error. In exchange, you get full
control over exactly what appears in the final file (nothing from
Maya's own HUD setup can leak through), and finer control over
fonts/position than Maya's native HUDs allow.

What's deliberately LEFT OUT compared to the "full" version, and why:

  - No separate files/package. Everything is here, in order, top to
    bottom. Nothing to import from a sibling file.
  - No regex. Finding the next version number uses plain string slicing
    instead (see get_next_version below).
  - No JSON config file. The naming pattern is just two constants near
    the top of this file -- edit them directly.
  - No PySide/Qt. The window is built with Maya's own built-in `cmds`
    UI commands. No classes, no "signals and slots" -- just "make a
    field, and read its value when the button is clicked."
  - No live-updating version badge. You fill in the fields and click
    one button; it does everything in one go.
  - No automated tests, no fallback for testing outside Maya. This file
    is meant to be run inside Maya, full stop.

HOW TO USE THIS FILE
--------------------
1. Make sure ffmpeg is installed and on your PATH (e.g. `brew install
   ffmpeg` on Mac, or download a build and add it to PATH on Windows).
   Check by running `ffmpeg -version` in a terminal.
2. Save this file anywhere Maya can import it -- e.g. your `scripts`
   folder.
3. In Maya's Script Editor (Python tab), click into a viewport, then run:

       import simple_playblast_tool
       simple_playblast_tool.show_ui()

4. Fill in Project / Sequence / Shot / Artist, tick some burn-in boxes,
   click the button.
"""


import os
import time
import json
import getpass
import platform
import subprocess
from pathlib import Path

import maya.cmds as cmds


# ---------------------------------------------------------------------
# STEP 0: SETTINGS
# ---------------------------------------------------------------------
# In the full version, these two patterns live in a JSON file so a
# studio can change them without touching code. For now, they're just
# two strings -- edit them directly if you want a different folder
# structure or filename.

# VARIABLES

FOLDER_PATTERN = "{project}/movies/{sequence}/{shot}/"
FILENAME_PATTERN = "{shot}"          # the version number gets added onto this
VERSION_PADDING = 3                   # v1 -> "v001"

CORNER_POSITIONS = {
    "top_left": "x=20:y=20",
    "top_right": "x=w-tw-20:y=20",
    "bottom_left": "x=20:y=h-th-20",
    "bottom_center": "x=(w-tw)/2:y=h-th-20",
    "bottom_right": "x=w-tw-20:y=h-th-20",
}

# Which corner of the frame each burn-in field appears in.
BURNIN_CORNER_FOR_FIELD = {
    "shot_name": "top_left",
    "camera_name": "top_right",
    "artist": "bottom_left",
    "date": "bottom_center",
    "frame": "bottom_right",
}

# FFMPEG 
def get_ffmpeg() -> None:
    CONFIG_PATH = Path(__file__).parent / "config.json"

    with CONFIG_PATH.open("r") as file:
        config = json.load(file)

    os.environ["PATH"] += os.pathsep + config["ffmpeg_bin"]

# ffmpeg's drawtext filter needs an actual font FILE, not just a font
# name -- pick a sensible default per platform. If burn-ins fail with a
# message about this font path, change it to any real .ttf file on your
# machine.
if platform.system() == "Darwin":
    FONT_PATH = "/System/Library/Fonts/Supplemental/Arial.ttf"
elif platform.system() == "Windows":
    FONT_PATH = "C:/Windows/Fonts/arial.ttf"
else:
    FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

        
# ---------------

# ---------------------------------------------------------------------
# STEP 1: FIGURE OUT WHERE THE FILE GOES, AND WHAT VERSION IT SHOULD BE
# ---------------------------------------------------------------------

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
    if not os.path.isabs(project): # if the path is not absolute (an absolute path begins with a slash (/).)

        # A relative path (like "dragonfly" or "Project") gets created
        # relative to whatever Maya's current working folder happens to
        # be -- which is not something we control and, on some systems
        #  can be a read-only location.
        # Catching this up front gives a clear message instead of a
        # confusing OS-level error several steps later.
        
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


# ---------------------------------------------------------------------
# STEP 2: READ THE CURRENT SCENE (camera, frame range, resolution)
# ---------------------------------------------------------------------

def get_active_camera() -> str:
    """Return the camera used by whichever viewport currently has focus."""
    panel = cmds.getPanel(withFocus=True)
    if not panel or "modelPanel" not in panel:
        panels = cmds.getPanel(type="modelPanel") # get all panels
        panel = panels[0] if panels else None # get panel 1

    if not panel:
        raise RuntimeError("No active viewport found -- click into a viewport first.")

    return cmds.modelPanel(panel, query=True, camera=True)


def get_frame_range() -> tuple[int, int]:
    """Return (start, end) from the current playback range."""
    start = cmds.playbackOptions(query=True, minTime=True)
    end = cmds.playbackOptions(query=True, maxTime=True)
    return int(start), int(end)


def get_resolution() -> tuple[int, int]:
    """Return (width, height) from the scene's render settings."""
    width = cmds.getAttr("defaultResolution.width")
    height = cmds.getAttr("defaultResolution.height")
    return int(width), int(height)


# ---------------------------------------------------------------------
# STEP 3: BURN-IN TEXT, VIA FFMPEG (runs *after* Maya records the raw clip)
# ---------------------------------------------------------------------

def hide_all_huds() -> list:
    """
    Hide every HUD currently on screen -- including Maya's own built-in
    ones (frame counter, poly count, etc.) -- so the raw capture is a
    clean plate. Only the text ffmpeg draws afterward will appear in
    the final video; nothing from Maya's own HUD setup can leak through.

    Returns a list of (name, was_visible) pairs, so everything can be
    put back exactly how it was afterward -- this never permanently
    changes your Maya HUD preferences.
    """
    existing_huds = cmds.headsUpDisplay(query=True, listHeadsUpDisplays=True) #or []
    huds_saved_state = []
    for hud_name in existing_huds:
        hud_visibility = cmds.headsUpDisplay(hud_name, query=True, visible=True)
        huds_saved_state.append((hud_name, hud_visibility))
        if hud_visibility:
            cmds.headsUpDisplay(hud_name, edit=True, visible=False) # turn the hud off
    return huds_saved_state


def restore_huds(huds_saved_state) -> None:
    """Put every HUD back exactly how it was before the playblast."""
    for hud_name, hud_visibility in huds_saved_state:
        cmds.headsUpDisplay(hud_name, edit=True, visible=hud_visibility)


def check_ffmpeg_available() -> None:
    """Raise a clear error if ffmpeg isn't installed / isn't on PATH."""
    try:
        subprocess.run(
            ["ffmpeg", "-version"], 
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
       f"drawtext=fontfile='{FONT_PATH}':text='{text}':{position}:fontsize=28:fontcolor=white:"
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
        # %{n} is ffmpeg's own per-frame counter, and it always starts at
        # 0 no matter what frame Maya actually started on. The eif(...)
        # expression adds the real starting frame number on top of that,
        # so what's burned in matches Maya's actual frame count.
        # eif: evaluate integer function -> it tells ffmpeg to calculate an expression
        frame_burnin_position = CORNER_POSITIONS[BURNIN_CORNER_FOR_FIELD["frame"]]
        filters.append(
            f"drawtext=fontfile='{FONT_PATH}':text='Frame\\: %{{eif\\:n+{maya_frame_start}\\:d}}':{frame_burnin_position}:"
            "fontsize=28:fontcolor=white:box=1:boxcolor=black@0.5:boxborderw=6"
        )

    return ",".join(filters)


def burn_in_with_ffmpeg(raw_path: str, final_path: str, enabled_fields: list, shot: str, camera: str, artist: str, frame_start: int) -> None:
    """Run ffmpeg once, drawing every enabled field onto the raw playblast."""
    check_ffmpeg_available()

    filter_chain = build_burnin_filters(enabled_fields, shot, camera, artist, frame_start)

    if not filter_chain:
        # Nothing was ticked -- nothing to draw, just use the raw file as-is.
        # move the file instead of processing it
        os.replace(raw_path, final_path)
        return
    # -y: overwrite existing file
    # -i: input file = raw path
    # -vf: apply video filter, which is filter chain
    # -c:v is codec video, libx264 = h264
    # -pix_fmt", "yuv420p -> video pixel format
    command = [
        "ffmpeg", "-y", "-i", raw_path,
        "-vf", filter_chain,
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "23", # encoding options and video quality
        final_path, # output
    ]
    result = subprocess.run(command, capture_output=True, text=True)
    # Check if FFmpeg succeeded
    if result.returncode != 0: # 0 means success
        raise RuntimeError("ffmpeg failed while burning in text:\n" + result.stderr[-1500:])

    os.remove(raw_path)


# ---------------------------------------------------------------------
# STEP 4: PUT IT ALL TOGETHER -- THE ONE FUNCTION THAT DOES EVERYTHING
# ---------------------------------------------------------------------

def generate_playblast(project: str, sequence: str, shot: str, burnin_fields: list, artist=None) -> str:
    """
    The main function. Works out where to save the file, reads the
    scene, records a clean raw playblast (no HUDs at all), burns in the
    selected fields with ffmpeg, and returns the path it saved to.
    """
    get_ffmpeg()

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


# ---------------------------------------------------------------------
# STEP 5: A SIMPLE WINDOW -- NO QT, JUST MAYA'S OWN UI COMMANDS
# ---------------------------------------------------------------------
# There are no classes here and nothing called a "signal." The pattern
# is just: build a field, remember its name, and read its value later
# when the button gets clicked.

def show_ui():
    if cmds.window("simplePlayblastToolWin", exists=True):
        cmds.deleteUI("simplePlayblastToolWin")

    window = cmds.window("simplePlayblastToolWin", title="Simple Playblast Tool", widthHeight=(280, 320))
    cmds.columnLayout(adjustableColumn=True, rowSpacing=6, columnAttach=("both", 10))

    cmds.text(label="Project", align="left")
    project_field = cmds.textField(text=get_default_project_root())

    cmds.text(label="Sequence", align="left")
    sequence_field = cmds.textField(text="seq010")

    cmds.text(label="Shot", align="left")
    shot_field = cmds.textField(text="sh0230")

    cmds.text(label="Artist", align="left")
    artist_field = cmds.textField(text=getpass.getuser())

    cmds.separator(height=12, style="in")

    cmds.text(label="Burn-in fields:", align="left")
    shot_name_box = cmds.checkBox(label="Shot name", value=True)
    frame_box = cmds.checkBox(label="Frame number", value=True)
    artist_box = cmds.checkBox(label="Artist", value=True)
    date_box = cmds.checkBox(label="Date", value=False)
    camera_box = cmds.checkBox(label="Camera", value=False)

    cmds.separator(height=12, style="in")

    def on_generate_clicked(*_args):
        # Read every field's current value right now, at click-time --
        # there's no "live" connection, we just ask each widget "what do
        # you say right now?" the moment the button is pressed.
        enabled_fields = []
        if cmds.checkBox(shot_name_box, query=True, value=True):
            enabled_fields.append("shot_name")
        if cmds.checkBox(frame_box, query=True, value=True):
            enabled_fields.append("frame")
        if cmds.checkBox(artist_box, query=True, value=True):
            enabled_fields.append("artist")
        if cmds.checkBox(date_box, query=True, value=True):
            enabled_fields.append("date")
        if cmds.checkBox(camera_box, query=True, value=True):
            enabled_fields.append("camera_name")

        try:
            generate_playblast(
                project=cmds.textField(project_field, query=True, text=True),
                sequence=cmds.textField(sequence_field, query=True, text=True),
                shot=cmds.textField(shot_field, query=True, text=True),
                burnin_fields=enabled_fields,
                artist=cmds.textField(artist_field, query=True, text=True),
            )
        except RuntimeError as error:
            cmds.confirmDialog(title="Playblast Manager", message=str(error), button=["OK"])

    cmds.button(label="Generate Playblast", height=32, command=on_generate_clicked)

    cmds.showWindow(window)