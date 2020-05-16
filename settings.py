"""
This global variables will help us to make pre 
simulation window to set beginning settings
"""

def meters_to_pixels(meters):
    return int((meters*PATH_LEN)/2.55)

def pixels_to_meters(pixels):
    return int((pixels*2.55)/PATH_LEN)

PATH_LEN = 40
TUNNEL_LEN = meters_to_pixels(600)  #1377.5
EXIT_SIZE = meters_to_pixels(2)

CAR_MARGIN = meters_to_pixels(1)
CELL_SIZE = int(CAR_MARGIN/3)

NUM_OF_PATHES = 4

MARGIN = 30


WIN_WIDTH = 600
WIN_HEIGHT = 400
FPS = 60
FONT = "monospace"

DISPLAY = (WIN_WIDTH, WIN_HEIGHT)
RUNNING = True

