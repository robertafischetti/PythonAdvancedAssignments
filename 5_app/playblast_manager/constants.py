"""---------------------------------------------------------------------------------------
 Module: constants

 Author = Roberta Fischetti

 Date = 2026-08-06

 Description = Burn-ins constants
---------------------------------------------------------------------------------------"""


CORNER_POSITIONS = {
    "top_left": "x=20:y=20",
    "top_right": "x=w-tw-20:y=20",
    "bottom_left": "x=20:y=h-th-20",
    "bottom_center": "x=(w-tw)/2:y=h-th-20",
    "bottom_right": "x=w-tw-20:y=h-th-20",
}

BURNIN_CORNER_FOR_FIELD = {
    "shot_name": "top_left",
    "camera_name": "top_right",
    "artist": "bottom_left",
    "date": "bottom_center",
    "frame": "bottom_right",
}