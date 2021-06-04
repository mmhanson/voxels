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
        self.add_block((0, 0, 0), GRASS) # origin
        self.add_block((0, 1, 0), GRASS) # on top of origin
        self.add_block((0, -1, 0), GRASS) # on bottom of origin
        self.add_block((1, 0, 0), GRASS) # west of origin
        self.add_block((-1, 0, 0), GRASS) # east of origin
        self.add_block((0, 0, 1), GRASS) # south of origin
        self.add_block((0, 0, -1), GRASS) # north of origin

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
        First value is horizntal rotation, rom -180 to _180.
        Second value is vertical rotation, from -90 to +90.
        Horizontal rotation wraps but vertical rotation doesnt.
        """
        self.rotn_buf = (0, 0)
        """
        Player rotation buffer. Rotation changes should be put here, then rotation is updated in the update method.
        """
        self.strafe = [0, 0]
        """
        Player strafe.
        First element is forward strafe, 1 when moving forward, -1 when moving backward, and 0 otherwise.
        Second element is side strafe, -1 when moving left, +1 when moving right, and 0 otherwise.
        """

    def get_vel(self):
        """
        Get the current player velocity.
        @returns: (tuple) 3d vector of velocity as dx, dy, dz
        """
        strafe_fwd, strafe_side = self.strafe

        sight_vec = self.get_sight_vec()
        fwd_vel = vec_mul(sight_vec, strafe_fwd)
        fwd_vel = (fwd_vel[0], 0, fwd_vel[2]) # make vertical element 0 so we dont float up

        right_vec = vec_ortho(sight_vec) # points to the right of sight vector on the horizontal plane
        side_vel = vec_mul(right_vec, strafe_side)

        vel = vec_add(fwd_vel, side_vel)
        if any(vel):
            vel = vec_normalize(vel) # if there is velocity, normalize it
        return vel

    def get_sight_vec(self):
        """
        Return a 3d unit vector that points where the player is looking.
        @return: (tuple) of x, y, z of player sight vector.
        """
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
        self.posn = vec_add(self.posn, vel) # adjust position with velocity


    def update_rotn(self):
        """
        Add buffered rotation changes into the player rotation.
        """
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
        self.strafe[0] += 1
    
    def add_backward_strafe(self):
        self.strafe[0] -= 1
    
    def add_left_strafe(self):
        self.strafe[1] -= 1

    def add_right_strafe(self):
        self.strafe[1] += 1
