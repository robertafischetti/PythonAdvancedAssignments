"""---------------------------------------------------------------------------------------
 Module: ui

 Author = Roberta Fischetti

 Date = 2026-08-06

 Description = A simple UI (no QT yet).
---------------------------------------------------------------------------------------"""
import getpass

import maya.cmds as cmds

from playblast_manager.playblast import generate_playblast, get_default_project_root


# FUNCTIONS ------------------------------------------------------------------------------
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

# START ------------------------------------------------------------------------------
if __name__ == "__main__":
    show_ui()