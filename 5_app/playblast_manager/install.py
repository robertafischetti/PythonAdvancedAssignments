"""---------------------------------------------------------------------------------------
 Module: install

 Author = Roberta Fischetti

 Date = 2026-09-03

 Description = Installs the Playblast Manager creating a Shelf Tab and a tool icon.
---------------------------------------------------------------------------------------"""

from pathlib import Path

import maya.mel as mel
import maya.cmds as cmds


# VARIABLES ------------------------------------------------------------------------------
TOOL_NAME = "PlayblastManager"
SHELF_NAME = "PlayblastManagerShelf"
BUTTON_NAME = "PlayblastManagerButton"
ICON_PATH = Path(__file__).parent / "images" / "playblast_manager_icon_64.png"


# FUNCTIONS ------------------------------------------------------------------------------
def install() -> None:
    """Install the Playblast Manager shelf button."""

    # Get the current Maya shelf layout
    shelf_top_level = mel.eval("$temp = $gShelfTopLevel")

    # Check whether our shelf already exists
    if not cmds.shelfLayout(SHELF_NAME, exists=True):

        cmds.shelfLayout(
            SHELF_NAME,
            parent=shelf_top_level
        )

    # Remove existing button
    if cmds.shelfButton(BUTTON_NAME, exists=True):
        cmds.deleteUI(BUTTON_NAME)

    # Create the shelf button
    cmds.shelfButton(
        BUTTON_NAME,
        parent=SHELF_NAME,
        label=TOOL_NAME,
        annotation="Open Playblast Manager",
        image=str(ICON_PATH),
        command="""import playblast_manager.playblast_manager_ui
classVar = playblast_manager.playblast_manager_ui.PlayblastManagerUI()""",
        sourceType="python"
    )

    print("Playblast Manager installed successfully!")
