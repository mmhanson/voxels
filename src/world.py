"""
This file models the world and its inhabitants. Below are some descriptions of the confusing parts.

=== Position ===========================================================================================================
x: positive goes east, negative goes west
y: positive goes up, negative goes down
z: positive goes south, negative goes north

     -z +y
      ↑↗
-x  ←-+-→ +x 
     ↙↓
   -y +z

"""

from config import *
from utils import *

import math
from random import randint, choice
from threading import Lock
from pyglet import image
from pyglet.graphics import TextureGroup, Batch
from pyglet.gl import GL_QUADS


class World:
    """
    Provides a single interface to all submodel classes.
    """
    def __init__(self):
        self.map = Map()
        self.player = Player()

    def draw(self):
        self.map.draw()

    def update(self, dt):
        """
        Called every frame.
        @param dt: float of the time passed since the last update
        """
        self.player.update(dt)

    def add_forward_strafe(self):
        self.player.add_forward_strafe()
    
    def add_backward_strafe(self):
        self.player.add_backward_strafe()
    
    def add_left_strafe(self):
        self.player.add_left_strafe()

    def add_right_strafe(self):
        self.player.add_right_strafe()

    def add_up_strafe(self):
        self.player.add_up_strafe()

    def remove_up_strafe(self):
        self.player.remove_up_strafe()

    def add_player_rotn(self, horiz, vert):
        self.player.add_rotn(horiz, vert)

    def get_player_rotn(self):
        return self.player.rotn

    def get_player_posn(self):
        return self.player.posn

    def get_player_vel(self):
        return self.player.get_vel()

    def get_player_sight_vec(self):
        return self.player.get_sight_vec()


class Map:
    def __init__(self):
        self.batch = Batch()
        """
        Pyglet vertex batch for all blocks in the world.
        """
        self.group = TextureGroup(image.load(TEXTURE_PATH).get_texture())
        """
        Pyglet texture group that stores our texture atlas.
        Block textures are cropped from this atlas. It's more efficient than loading textures individually.
        """
        self.blocks = {}
        """
        Maps coordinates to the block that exists at that coordinate.
        """
        self.generate()

    def generate(self):
        # 3d plus shape at origin
        #self.add_block((0, 0, 0), GRASS) # origin
        #self.add_block((0, 1, 0), GRASS) # on top of origin
        #self.add_block((0, -1, 0), GRASS) # on bottom of origin
        #self.add_block((1, 0, 0), GRASS) # west of origin
        #self.add_block((-1, 0, 0), GRASS) # east of origin
        #self.add_block((0, 0, 1), GRASS) # south of origin
        #self.add_block((0, 0, -1), GRASS) # north of origin
        n = 80  # 1/2 width and height of world
        s = 1  # step size
        y = 0  # initial y height
        for x in range(-n, n + 1, s):
            for z in range(-n, n + 1, s):
                # create a layer stone an grass everywhere.
                self.add_block((x, y - 2, z), GRASS)
                self.add_block((x, y - 3, z), STONE)
                if x in (-n, n) or z in (-n, n):
                    # create outer walls.
                    for dy in range(-2, 3):
                        self.add_block((x, y + dy, z), STONE)

        # generate the hills randomly
        o = n - 10
        for _ in range(120):
            a = randint(-o, o)  # x position of the hill
            b = randint(-o, o)  # z position of the hill
            c = -1  # base of the hill
            h = randint(1, 6)  # height of the hill
            s = randint(4, 8)  # 2 * s is the side length of the hill
            d = 1  # how quickly to taper off the hills
            t = choice([GRASS, SAND, BRICK])
            for y in range(c, c + h):
                for x in range(a - s, a + s + 1):
                    for z in range(b - s, b + s + 1):
                        if (x - a) ** 2 + (z - b) ** 2 > (s + 1) ** 2:
                            continue
                        if (x - 0) ** 2 + (z - 0) ** 2 < 5 ** 2:
                            continue
                        self.add_block((x, y, z), t)
                s -= d  # decrement side length so hills taper off

    def add_block(self, position, texture):
        self.blocks[position] = texture
        x, y, z = position
        vertex_data = cube_vertices(x, y, z, 0.5)
        texture_data = list(texture)
        # create vertex list
        # TODO use add_indexed
        self.batch.add(24, GL_QUADS, self.group,
            ('v3f/static', vertex_data),
            ('t2f/static', texture_data))

    def draw(self):
        self.batch.draw()


class Player:
    def __init__(self):
        self.posn = (0, 0, 0)
        """
        Player position as x, y, z
        """
        self.rotn = (0, 0)
        """
        Player rotation.
        First value is horizntal rotation, from -180 to _180.
        Second value is vertical rotation, from -90 to +90.
        Horizontal rotation wraps but vertical rotation doesnt.
        """
        self.rotn_buf = (0, 0)
        """
        Player rotation buffer. Rotation changes should be put here, then rotation is updated in the update method.
        """
        self.strafe = [0, 0, 0]
        """
        Player strafe.
        First element is forward strafe, 1 when moving forward, -1 when moving backward, and 0 otherwise.
        Second element is side strafe, -1 when moving left, +1 when moving right, and 0 otherwise.
        Third element is vertical strafe (flying/jumping), -1 when flying down, 1 when flying up/jumping, 0 otherwise.
        """
        self.mutex = Lock()
        """
        Hold this mutex before modifying or using any fields of this class.
        """

    def get_vel(self):
        """
        Get the current player velocity.
        @returns: (tuple) normalized 3d vector of velocity as dx, dy, dz
        """
        with self.mutex:
            strafe_fwd, strafe_side, strafe_up = self.strafe

        sight_vec = self.get_sight_vec()
        fwd_vel = vec_mul(sight_vec, strafe_fwd)
        fwd_vel = (fwd_vel[0], 0, fwd_vel[2]) # make vertical velocity 0 so we dont float up when looking upward

        right_vec = vec_ortho(sight_vec) # points to the right of sight vector on the horizontal plane
        side_vel = vec_mul(right_vec, strafe_side)

        up_vec = (0, 1, 0) # points straight up
        up_vel = vec_mul(up_vec, strafe_up)

        vel = vec_add(vec_add(fwd_vel, side_vel), up_vel)
        vel = vec_normalize(vel) # if there is velocity, normalize it
        return vel

    def get_sight_vec(self):
        """
        Return a 3d unit vector that points where the player is looking.
        @return: (tuple) of x, y, z of player sight vector.
        """
        with self.mutex:
            horiz_rotn, vert_rotn = self.rotn
        x = math.sin(math.radians(horiz_rotn))
        y = math.sin(math.radians(vert_rotn))
        z = math.cos(math.radians(horiz_rotn))
        z *= -1 # since negative z points outward from the camera
        sight_vec = vec_normalize((x, y, z))
        return sight_vec

    def add_rotn(self, horiz, vert):
        """
        Add to the player rotation.
        @param horiz: Change in horizontal rotation
        @param vert: Change in vertical rotation
        
        Note that rotation changes are buffered and rotation is updated in the update method.
        Note vertical rotation is clamped to 90 and -90, it cannot exceed that. And horizontal rotation wraps around at
        180 and -180 degrees (backwards facing).
        """
        with self.mutex:
            old_horiz, old_vert = self.rotn_buf
            self.rotn_buf = (old_horiz+horiz, old_vert+vert)

    def update(self, dt):
        """
        Update player position and rotation.
        @param dt: (float) the change in time since the last update.
        """
        self.update_posn(dt)
        self.update_rotn()

    def update_posn(self, dt):
        """
        Update the player position.
        @param dt: (float) The change in time since the last update.
        """
        d = dt * FLYING_SPEED # distance covered since the last update
        vel = vec_mul(self.get_vel(), d) # scale velocity for distance
        with self.mutex:
            self.posn = vec_add(self.posn, vel) # adjust position with velocity


    def update_rotn(self):
        """
        Add buffered rotation changes into the player rotation.
        """
        with self.mutex:
            old_horiz, old_vert = self.rotn
            horiz_add, vert_add = self.rotn_buf
            self.rotn_buf = (0, 0)
            new_horiz = old_horiz + horiz_add
            new_vert = old_vert + vert_add

            # clamp vertical rotn
            if new_vert > 90:
                new_vert = 90
            elif new_vert < -90:
                new_vert = -90
            # wrap horiz rotn around
            if new_horiz >= 180:
                extra_rotn = new_horiz - 180
                new_horiz = -180 + extra_rotn
            elif new_horiz < -180:
                extra_rotn = -180 - new_horiz 
                new_horiz = 180 - extra_rotn

            self.rotn = (new_horiz, new_vert)

    def add_forward_strafe(self):
        with self.mutex:
            self.strafe[0] += 1
    
    def add_backward_strafe(self):
        with self.mutex:
            self.strafe[0] -= 1
    
    def add_left_strafe(self):
        with self.mutex:
            self.strafe[1] -= 1

    def add_right_strafe(self):
        with self.mutex:
            self.strafe[1] += 1

    def add_up_strafe(self):
        with self.mutex:
            self.strafe[2] += 1

    def remove_up_strafe(self):
        with self.mutex:
            self.strafe[2] -= 1
