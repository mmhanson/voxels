"""
Contains configuration constants.
"""

from utils import *


TICKS_PER_SEC = 60 # how many updates per sec
FLYING_SPEED = 15 # how many blocks you move past per second while flying around
SIGHT_SPEED = 0.15 # constant adjusting how fast the player looks around
SIGHT_INVERTED = True # inverts the vertical sight direction

# === Texture Info =====================================================================================================
TEXTURE_PATH = "src/texture.png"
GRASS = tex_coords((1, 0), (0, 1), (0, 0))
SAND = tex_coords((1, 1), (1, 1), (1, 1))
BRICK = tex_coords((2, 0), (2, 0), (2, 0))
STONE = tex_coords((2, 1), (2, 1), (2, 1))
